package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/textproto"
	"os"
	"path/filepath"
	"strings"

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

// StreamChunk 流式返回的文本块
type StreamChunk struct {
	Content string
	Sources []model.SourceInfo
	Warning string
	Done    bool
	Error   error
}

// ChatWithHistoryStream 带历史记录的流式聊天
func (s *AIService) ChatWithHistoryStream(question string, petInfo *PetInfo, history []string, sessionSummary string) (<-chan StreamChunk, error) {
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

	url := fmt.Sprintf("%s/chat/stream", s.apiURL)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("调用AI服务失败: %w", err)
	}

	chunkChan := make(chan StreamChunk)

	go func() {
		defer close(chunkChan)
		defer resp.Body.Close()

		reader := resp.Body
		buffer := make([]byte, 1024)
		leftover := ""

		for {
			n, err := reader.Read(buffer)
			if n > 0 {
				leftover += string(buffer[:n])

				// 处理 SSE 事件行
				lines := strings.Split(leftover, "\n")
				for i := 0; i < len(lines)-1; i++ {
					line := strings.TrimSpace(lines[i])
					if strings.HasPrefix(line, "data: ") {
						data := line[6:] // 去掉 "data: " 前缀

						var event struct {
							Type    string `json:"type"`
							Content string `json:"content"`
							Sources []struct {
								Source string  `json:"source"`
								Score  float64 `json:"score"`
							} `json:"sources"`
							Warning string `json:"warning"`
						}

						if err := json.Unmarshal([]byte(data), &event); err == nil {
							if event.Type == "content" {
								chunkChan <- StreamChunk{Content: event.Content}
							} else if event.Type == "done" {
								// 转换 sources
								sources := make([]model.SourceInfo, 0, len(event.Sources))
								for _, src := range event.Sources {
									sources = append(sources, model.SourceInfo{
										Source:        src.Source,
										SemanticScore: src.Score,
									})
								}
								chunkChan <- StreamChunk{
									Done:    true,
									Sources: sources,
									Warning: event.Warning,
								}
							}
						}
					}
				}
				leftover = lines[len(lines)-1]
			}
			if err != nil {
				break
			}
		}
	}()

	return chunkChan, nil
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
		return nil, fmt.Errorf("读取图片文件失败: %w (path: %s)", err, imagePath)
	}

	// 根据文件扩展名确定 MIME 类型
	ext := strings.ToLower(filepath.Ext(imagePath))
	var contentType string
	switch ext {
	case ".jpg", ".jpeg":
		contentType = "image/jpeg"
	case ".png":
		contentType = "image/png"
	default:
		contentType = "application/octet-stream"
	}

	// 构建 multipart/form-data 请求
	buf := &bytes.Buffer{}
	writer := multipart.NewWriter(buf)

	// 添加 question 字段
	if err := writer.WriteField("question", question); err != nil {
		return nil, fmt.Errorf("写入 question 失败: %w", err)
	}

	// 添加图片文件（使用正确的 Content-Type）
	header := make(textproto.MIMEHeader)
	header.Set("Content-Disposition", fmt.Sprintf(`form-data; name="file"; filename="%s"`, filepath.Base(imagePath)))
	header.Set("Content-Type", contentType)
	part, err := writer.CreatePart(header)
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
	req, err := http.NewRequest("POST", url, buf)
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
