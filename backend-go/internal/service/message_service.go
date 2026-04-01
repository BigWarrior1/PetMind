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
	fileStore   *repository.FileStore
	aiService   *AIService
	// 保护正在进行的摘要操作，防止同一 session 并发摘要
	summarizeMu    sync.Mutex
	summarizingMap map[uuid.UUID]bool
}

func NewMessageService(
	messageRepo *repository.MessageRepository,
	sessionRepo *repository.SessionRepository,
	fileStore *repository.FileStore,
) *MessageService {
	return &MessageService{
		messageRepo:    messageRepo,
		sessionRepo:    sessionRepo,
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

	// 检查是否需要生成摘要（消息数量达到阈值时）
	totalMessages := len(historyMsgs) + 1 // +1 因为还没保存当前消息
	if totalMessages >= SummarizeThreshold && (totalMessages%SummarizeThreshold == 1) {
		// 异步触发摘要（在保存消息之后）
		go s.maybeSummarize(sessionID, historyMsgs)
	}

	// 获取 session 摘要
	var sessionSummary string
	if s.sessionRepo != nil {
		session, err := s.sessionRepo.GetByID(sessionID)
		if err == nil && session != nil {
			sessionSummary = session.Summary
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
		aiResp, err := s.aiService.ChatWithHistory(content, nil, history, sessionSummary)
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
