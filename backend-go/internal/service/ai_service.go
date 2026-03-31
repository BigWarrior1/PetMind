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
	Model   string `json:"model"`
	Messages []struct {
		Role    string `json:"role"`
		Content string `json:"content"`
	} `json:"messages"`
	Temperature float64 `json:"temperature"`
}

func (s *AIService) Chat(question string, petInfo *PetInfo) (*model.AIResponse, error) {
	// 构建请求
	systemPrompt := `你是一个专业的宠物健康顾问。

你的职责：
1. 基于提供的知识库内容，准确回答用户关于宠物健康的问题
2. 当情况危急时（如高烧，呼吸困难、严重出血等），提醒用户立即就医
3. 始终强调：你的建议仅供参考，不能替代执业兽医的诊断

回答要求：
- 基于事实，不要编造信息
- 语言通俗易懂，适合普通宠物主人理解`

	userPrompt := question
	if petInfo != nil {
		userPrompt = fmt.Sprintf("用户宠物信息：\n- 种类：%s\n- 品种：%s\n- 年龄：%s\n- 体重：%s\n\n用户问题：%s",
			petInfo.Species, petInfo.Breed, petInfo.Age, petInfo.Weight, question)
	}

	reqBody := AIRequestBody{
		Model: "qwen3.5-plus",
		Messages: []struct {
			Role    string `json:"role"`
			Content string `json:"content"`
		}{
			{Role: "system", Content: systemPrompt},
			{Role: "user", Content: userPrompt},
		},
		Temperature: 0.7,
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
			Source:       src.Source,
			SemanticScore: src.Score,
		})
	}

	return &model.AIResponse{
		Answer:  result.Answer,
		Sources: sources,
		Warning: result.Warning,
	}, nil
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
