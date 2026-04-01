package service

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"path/filepath"
	"sync"
	"time"

	"petmind-backend/internal/model"
	"petmind-backend/internal/repository"

	"github.com/google/uuid"
)

var (
	ErrMessageSendFailed = errors.New("发送消息失败")
)

// 最大历史消息数量（保留最近 N 条消息）
const MaxHistoryMessages = 10

// 触发摘要的消息数量阈值
const SummarizeThreshold = 20

type MessageService struct {
	messageRepo *repository.MessageRepository
	sessionRepo *repository.SessionRepository
	petRepo     *repository.PetRepository
	fileStore   *repository.FileStore
	aiService   *AIService
	// 保护正在进行的摘要操作，防止同一 session 并发摘要
	summarizeMu    sync.Mutex
	summarizingMap map[uuid.UUID]bool
}

func NewMessageService(
	messageRepo *repository.MessageRepository,
	sessionRepo *repository.SessionRepository,
	petRepo *repository.PetRepository,
	fileStore *repository.FileStore,
) *MessageService {
	return &MessageService{
		messageRepo:    messageRepo,
		sessionRepo:    sessionRepo,
		petRepo:       petRepo,
		fileStore:      fileStore,
		summarizingMap: make(map[uuid.UUID]bool),
	}
}

func (s *MessageService) SetAIService(aiService *AIService) {
	s.aiService = aiService
}

func (s *MessageService) ListBySession(sessionID uuid.UUID) ([]model.Message, error) {
	return s.messageRepo.ListBySession(sessionID)
}

func (s *MessageService) Send(userID, sessionID uuid.UUID, content string) (*model.Message, error) {
	// 获取历史消息
	historyMsgs, err := s.messageRepo.ListBySession(sessionID)
	if err != nil {
		return nil, err
	}

	// 如果是第一条消息，自动生成会话标题
	if len(historyMsgs) == 0 {
		go s.maybeUpdateTitle(sessionID, userID, content)
	}

	// 检查是否需要生成摘要（消息数量达到阈值时）
	totalMessages := len(historyMsgs) + 1 // +1 因为还没保存当前消息
	if totalMessages >= SummarizeThreshold && (totalMessages%SummarizeThreshold == 1) {
		// 异步触发摘要（在保存消息之后）
		go s.maybeSummarize(sessionID, historyMsgs)
	}

	// 获取 session 及其摘要
	var sessionSummary string
	var petInfo *PetInfo
	session, err := s.sessionRepo.GetByID(sessionID)
	if err == nil && session != nil {
		sessionSummary = session.Summary

		// 如果是宠物专属会话，获取宠物信息
		if session.PetID != nil && s.petRepo != nil {
			pet, petErr := s.petRepo.GetByID(*session.PetID)
			if petErr == nil && pet != nil {
				petInfo = &PetInfo{
					Species: pet.Species,
					Breed:   pet.Breed,
					Age:     pet.Age,
					Weight:  pet.Weight,
				}
			}
		}
	}

	// 压缩历史消息（只保留最近 N 条）
	historyMsgs = compressHistory(historyMsgs)

	// 构建历史格式 ["user:xxx", "assistant:xxx"]
	history := make([]string, 0, len(historyMsgs))
	for _, msg := range historyMsgs {
		if msg.Role == "user" {
			history = append(history, "user:"+msg.Content)
		} else if msg.Role == "assistant" {
			history = append(history, "assistant:"+msg.Content)
		}
	}

	// 保存用户消息
	userMsg := &model.Message{
		SessionID: sessionID,
		Role:      "user",
		Content:   content,
	}
	if err := s.messageRepo.Create(userMsg); err != nil {
		return nil, err
	}

	// 调用 AI 服务（带历史和摘要）
	if s.aiService != nil {
		aiResp, err := s.aiService.ChatWithHistory(content, petInfo, history, sessionSummary)
		if err != nil {
			// AI 调用失败，返回用户消息
			return userMsg, nil
		}

		// 保存 AI 回复
		sourcesJSON, _ := json.Marshal(aiResp.Sources)
		assistantMsg := &model.Message{
			SessionID: sessionID,
			Role:      "assistant",
			Content:   aiResp.Answer,
			Sources:   string(sourcesJSON),
		}
		if err := s.messageRepo.Create(assistantMsg); err != nil {
			return nil, err
		}

		return assistantMsg, nil
	}

	return userMsg, nil
}

// MessageStreamChunk 流式消息块（用于消息服务）
type MessageStreamChunk struct {
	Content   string                // 文本内容
	Sources   []model.SourceInfo    // 来源信息
	Warning   string                // 就医警示
	Done      bool                  // 是否结束
	UserMsg   *model.Message        // 用户消息
	AssistantMsg *model.Message     // AI 回复消息
	Error     error                // 错误信息
}

// SendStream 流式发送消息
func (s *MessageService) SendStream(userID, sessionID uuid.UUID, content string) (<-chan MessageStreamChunk, *model.Message, error) {
	// 获取历史消息
	historyMsgs, err := s.messageRepo.ListBySession(sessionID)
	if err != nil {
		return nil, nil, err
	}

	// 如果是第一条消息，自动生成会话标题
	if len(historyMsgs) == 0 {
		go s.maybeUpdateTitle(sessionID, userID, content)
	}

	// 检查是否需要生成摘要
	totalMessages := len(historyMsgs) + 1
	if totalMessages >= SummarizeThreshold && (totalMessages%SummarizeThreshold == 1) {
		go s.maybeSummarize(sessionID, historyMsgs)
	}

	// 获取 session 及其摘要和宠物信息
	var sessionSummary string
	var petInfo *PetInfo
	session, err := s.sessionRepo.GetByID(sessionID)
	if err == nil && session != nil {
		sessionSummary = session.Summary

		if session.PetID != nil && s.petRepo != nil {
			pet, petErr := s.petRepo.GetByID(*session.PetID)
			if petErr == nil && pet != nil {
				petInfo = &PetInfo{
					Species: pet.Species,
					Breed:   pet.Breed,
					Age:     pet.Age,
					Weight:  pet.Weight,
				}
			}
		}
	}

	// 压缩历史消息
	historyMsgs = compressHistory(historyMsgs)

	// 构建历史格式
	history := make([]string, 0, len(historyMsgs))
	for _, msg := range historyMsgs {
		if msg.Role == "user" {
			history = append(history, "user:"+msg.Content)
		} else if msg.Role == "assistant" {
			history = append(history, "assistant:"+msg.Content)
		}
	}

	// 保存用户消息
	userMsg := &model.Message{
		SessionID: sessionID,
		Role:      "user",
		Content:   content,
	}
	if err := s.messageRepo.Create(userMsg); err != nil {
		return nil, nil, err
	}

	// 如果没有 AI 服务，直接返回
	if s.aiService == nil {
		chunkChan := make(chan MessageStreamChunk, 1)
		chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg}
		close(chunkChan)
		return chunkChan, userMsg, nil
	}

	// 启动流式 AI 调用
	chunkChan := make(chan MessageStreamChunk)

	go func() {
		defer close(chunkChan)

		// 调用 AI 流式服务
		aiChan, err := s.aiService.ChatWithHistoryStream(content, petInfo, history, sessionSummary)
		if err != nil {
			chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg, Error: err}
			return
		}

		fullAnswer := ""
		var sources []model.SourceInfo
		var warning string

		// 接收流式数据
		for chunk := range aiChan {
			if chunk.Error != nil {
				chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg, Error: chunk.Error}
				return
			}

			if chunk.Done {
				sources = chunk.Sources
				warning = chunk.Warning
				chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg}
			} else {
				fullAnswer += chunk.Content
				chunkChan <- MessageStreamChunk{Content: chunk.Content}
			}
		}

		// 保存 AI 回复
		if fullAnswer != "" {
			sourcesJSON, _ := json.Marshal(sources)
			assistantMsg := &model.Message{
				SessionID: sessionID,
				Role:      "assistant",
				Content:   fullAnswer,
				Sources:   string(sourcesJSON),
			}
			if err := s.messageRepo.Create(assistantMsg); err != nil {
				chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg, Error: err}
				return
			}
			chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg, AssistantMsg: assistantMsg, Sources: sources, Warning: warning}
		} else {
			chunkChan <- MessageStreamChunk{Done: true, UserMsg: userMsg}
		}
	}()

	return chunkChan, userMsg, nil
}

// maybeSummarize 异步生成会话摘要
func (s *MessageService) maybeSummarize(sessionID uuid.UUID, allMessages []model.Message) {
	if s.aiService == nil || s.sessionRepo == nil {
		return
	}

	// 检查是否正在进行摘要，如果是则跳过
	s.summarizeMu.Lock()
	if s.summarizingMap[sessionID] {
		s.summarizeMu.Unlock()
		return
	}
	s.summarizingMap[sessionID] = true
	s.summarizeMu.Unlock()

	// 确保清理状态
	defer func() {
		s.summarizeMu.Lock()
		delete(s.summarizingMap, sessionID)
		s.summarizeMu.Unlock()
	}()

	// 获取 session
	session, err := s.sessionRepo.GetByID(sessionID)
	if err != nil || session == nil {
		return
	}

	// 计算需要摘要的消息（排除最近的 MaxHistoryMessages）
	if len(allMessages) <= MaxHistoryMessages {
		return
	}
	messagesToSummarize := allMessages[:len(allMessages)-MaxHistoryMessages]

	// 构建待摘要的消息列表
	historyForSummary := make([]string, 0, len(messagesToSummarize))
	for _, msg := range messagesToSummarize {
		if msg.Role == "user" {
			historyForSummary = append(historyForSummary, "user:"+msg.Content)
		} else if msg.Role == "assistant" {
			historyForSummary = append(historyForSummary, "assistant:"+msg.Content)
		}
	}

	// 调用 AI 生成摘要
	summary, err := s.aiService.Summarize(historyForSummary)
	if err != nil || summary == "" {
		return
	}

	// 更新 session 摘要
	now := time.Now()
	session.Summary = summary
	session.SummaryUpdatedAt = &now
	s.sessionRepo.Update(session)
}

// maybeUpdateTitle 异步生成会话标题（基于第一条用户消息）
func (s *MessageService) maybeUpdateTitle(sessionID, userID uuid.UUID, firstMessage string) {
	if s.aiService == nil || s.sessionRepo == nil {
		return
	}

	// 调用 AI 生成简短标题（只需要 10-20 字）
	title, err := s.aiService.GenerateTitle(firstMessage)
	if err != nil || title == "" {
		return
	}

	// 更新 session 标题
	session, err := s.sessionRepo.GetByID(sessionID)
	if err != nil {
		return
	}
	session.Title = title
	session.UpdatedAt = time.Now()
	s.sessionRepo.Update(session)
}

// compressHistory 压缩历史消息，保留最近 N 条
func compressHistory(messages []model.Message) []model.Message {
	if len(messages) <= MaxHistoryMessages {
		return messages
	}
	// 只保留最近的消息
	return messages[len(messages)-MaxHistoryMessages:]
}

func (s *MessageService) SendImage(userID, sessionID uuid.UUID, file *multipart.FileHeader, question string) (*model.Message, error) {
	// 读取文件内容
	src, err := file.Open()
	if err != nil {
		return nil, fmt.Errorf("打开文件失败: %w", err)
	}
	defer src.Close()

	data, err := io.ReadAll(src)
	if err != nil {
		return nil, fmt.Errorf("读取文件失败: %w", err)
	}

	// 保存文件
	ext := filepath.Ext(file.Filename)
	newFilename := fmt.Sprintf("%s%s", uuid.New().String(), ext)
	userIDStr := userID.String()
	sessionIDStr := sessionID.String()

	imagePath, err := s.fileStore.Save(userIDStr, sessionIDStr, newFilename, data)
	if err != nil {
		return nil, fmt.Errorf("保存文件失败: %w", err)
	}

	// 保存用户消息（带图片）
	imageURLsJSON, _ := json.Marshal([]string{imagePath})

	userMsg := &model.Message{
		SessionID: sessionID,
		Role:      "user",
		Content:   question,
		ImageURLs: string(imageURLsJSON),
	}
	if err := s.messageRepo.Create(userMsg); err != nil {
		return nil, err
	}

	// 调用 AI 图片分析
	if s.aiService != nil {
		aiResp, err := s.analyzeImage(imagePath, question)
		if err != nil {
			return userMsg, nil
		}

		sourcesJSON, _ := json.Marshal(aiResp.Sources)
		assistantMsg := &model.Message{
			SessionID: sessionID,
			Role:      "assistant",
			Content:   aiResp.Answer,
			Sources:   string(sourcesJSON),
		}
		if err := s.messageRepo.Create(assistantMsg); err != nil {
			return nil, err
		}

		return assistantMsg, nil
	}

	return userMsg, nil
}

func (s *MessageService) analyzeImage(imagePath, question string) (*model.AIResponse, error) {
	if s.aiService == nil {
		return &model.AIResponse{
			Answer: "图片分析服务暂不可用",
		}, nil
	}

	// 调用 Python FastAPI 的图片分析端点
	resp, err := s.aiService.AnalyzeImage(imagePath, question)
	if err != nil {
		return nil, fmt.Errorf("图片分析失败: %w", err)
	}

	return resp, nil
}

// 辅助函数：解析 ImageURLs JSON
func ParseImageURLs(jsonStr string) ([]string, error) {
	if jsonStr == "" {
		return nil, nil
	}
	var urls []string
	if err := json.Unmarshal([]byte(jsonStr), &urls); err != nil {
		return nil, err
	}
	return urls, nil
}

// 辅助函数：解析 Sources JSON
func ParseSources(jsonStr string) ([]model.SourceInfo, error) {
	if jsonStr == "" {
		return nil, nil
	}
	var sources []model.SourceInfo
	if err := json.Unmarshal([]byte(jsonStr), &sources); err != nil {
		return nil, err
	}
	return sources, nil
}
