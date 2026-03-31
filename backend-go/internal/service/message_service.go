package service

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"path/filepath"

	"petmind-backend/internal/model"
	"petmind-backend/internal/repository"

	"github.com/google/uuid"
)

var (
	ErrMessageSendFailed = errors.New("发送消息失败")
)

type MessageService struct {
	messageRepo *repository.MessageRepository
	fileStore   *repository.FileStore
	aiService   *AIService
}

func NewMessageService(
	messageRepo *repository.MessageRepository,
	fileStore *repository.FileStore,
) *MessageService {
	return &MessageService{
		messageRepo: messageRepo,
		fileStore:   fileStore,
	}
}

func (s *MessageService) SetAIService(aiService *AIService) {
	s.aiService = aiService
}

func (s *MessageService) ListBySession(sessionID uuid.UUID) ([]model.Message, error) {
	return s.messageRepo.ListBySession(sessionID)
}

func (s *MessageService) Send(userID, sessionID uuid.UUID, content string) (*model.Message, error) {
	// 保存用户消息
	userMsg := &model.Message{
		SessionID: sessionID,
		Role:     "user",
		Content:  content,
	}
	if err := s.messageRepo.Create(userMsg); err != nil {
		return nil, err
	}

	// 调用 AI 服务
	if s.aiService != nil {
		aiResp, err := s.aiService.Chat(content, nil)
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
		Role:     "user",
		Content:  question,
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
