package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"

	"petmind-backend/internal/model"
)

type AIService struct {
	apiURL string
	client *http.Client
}

func NewAIService(apiURL string) *AIService {
	return &AIService{
		apiURL: apiURL,
		client: &http.Client{},
	}
}

type AIRequest struct {
	Question string `json:"question"`
	PetInfo  *PetInfo `json:"pet_info,omitempty"`
}

type PetInfo struct {
	Species string `json:"species,omitempty"`
	Breed   string `json:"breed,omitempty"`
	Age     string `json:"age,omitempty"`
	Weight  string `json:"weight,omitempty"`
}

type AIRequestBody struct {
	Question       string    `json:"question"`
	PetInfo        *PetInfo  `json:"pet_info,omitempty"`
	History        []string  `json:"history,omitempty"`         // 对话历史 [ "user:xxx", "assistant:xxx", ... ]
	SessionSummary string    `json:"session_summary,omitempty"`  // 会话摘要
}

// ChatWithHistory 带历史记录的聊天
func (s *AIService) ChatWithHistory(question string, petInfo *PetInfo, history []string, sessionSummary string) (*model.AIResponse, error) {
	reqBody := AIRequestBody{
		Question:       question,
		PetInfo:        petInfo,
		History:        history,
		SessionSummary: sessionSummary,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %w", err)
	}

	url := fmt.Sprintf("%s/chat", s.apiURL)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("调用AI服务失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d - %s", resp.StatusCode, string(body))
	}

	var result struct {
		Answer  string `json:"answer"`
		Sources []struct {
			Source string  `json:"source"`
			Score  float64 `json:"score"`
		} `json:"sources"`
		Warning string `json:"warning"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %w", err)
	}

	// 转换来源信息
	sources := make([]model.SourceInfo, 0, len(result.Sources))
	for _, src := range result.Sources {
		sources = append(sources, model.SourceInfo{
			Source:        src.Source,
			SemanticScore: src.Score,
		})
	}

	return &model.AIResponse{
		Answer:  result.Answer,
		Sources: sources,
		Warning: result.Warning,
	}, nil
}

// Chat 不带历史记录的聊天（兼容旧接口）
func (s *AIService) Chat(question string, petInfo *PetInfo) (*model.AIResponse, error) {
	return s.ChatWithHistory(question, petInfo, nil, "")
}

// Summarize 调用 Python 的 /summarize 接口生成会话摘要
func (s *AIService) Summarize(messages []string) (string, error) {
	type SummarizeRequest struct {
		Messages []string `json:"messages"`
	}
	type SummarizeResponse struct {
		Summary string `json:"summary"`
	}

	reqBody := SummarizeRequest{Messages: messages}
	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	url := fmt.Sprintf("%s/summarize", s.apiURL)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("调用AI服务失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("AI服务返回错误: %d - %s", resp.StatusCode, string(body))
	}

	var result SummarizeResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("解析响应失败: %w", err)
	}

	return result.Summary, nil
}

// GenerateTitle 调用 Python 生成会话标题
func (s *AIService) GenerateTitle(firstMessage string) (string, error) {
	type GenerateTitleRequest struct {
		Message string `json:"message"`
	}
	type GenerateTitleResponse struct {
		Title string `json:"title"`
	}

	reqBody := GenerateTitleRequest{Message: firstMessage}
	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	url := fmt.Sprintf("%s/generate_title", s.apiURL)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("调用AI服务失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("AI服务返回错误: %d - %s", resp.StatusCode, string(body))
	}

	var result GenerateTitleResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("解析响应失败: %w", err)
	}

	return result.Title, nil
}

// AnalyzeImage 调用 Python FastAPI 的图片分析端点
func (s *AIService) AnalyzeImage(imagePath, question string) (*model.AIResponse, error) {
	// 读取图片文件
	data, err := os.ReadFile(imagePath)
	if err != nil {
		return nil, fmt.Errorf("读取图片文件失败: %w", err)
	}

	// 构建 multipart/form-data 请求
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// 添加 question 字段
	if err := writer.WriteField("question", question); err != nil {
		return nil, fmt.Errorf("写入 question 失败: %w", err)
	}

	// 添加图片文件
	part, err := writer.CreateFormFile("file", filepath.Base(imagePath))
	if err != nil {
		return nil, fmt.Errorf("创建表单文件失败: %w", err)
	}
	if _, err := part.Write(data); err != nil {
		return nil, fmt.Errorf("写入图片数据失败: %w", err)
	}

	if err := writer.Close(); err != nil {
		return nil, fmt.Errorf("关闭 writer 失败: %w", err)
	}

	url := fmt.Sprintf("%s/analyze/image", s.apiURL)
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	resp, err := s.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("调用AI图片分析服务失败: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI服务返回错误: %d - %s", resp.StatusCode, string(bodyBytes))
	}

	var result struct {
		Analysis string `json:"analysis"`
		Warning  string `json:"warning"`
		Sources  []struct {
			Source string  `json:"source"`
			Score  float64 `json:"score"`
		} `json:"sources"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %w", err)
	}

	// 转换来源信息
	sources := make([]model.SourceInfo, 0, len(result.Sources))
	for _, src := range result.Sources {
		sources = append(sources, model.SourceInfo{
			Source:       src.Source,
			SemanticScore: src.Score,
		})
	}

	return &model.AIResponse{
		Answer:  result.Analysis,
		Sources: sources,
		Warning: result.Warning,
	}, nil
}
