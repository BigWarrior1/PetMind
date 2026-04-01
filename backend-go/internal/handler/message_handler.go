package handler

import (
	"encoding/json"
	"fmt"
	"net/http"

	"petmind-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type MessageHandler struct {
	messageService *service.MessageService
	sessionService *service.SessionService
}

func NewMessageHandler(messageService *service.MessageService, sessionService *service.SessionService) *MessageHandler {
	return &MessageHandler{
		messageService: messageService,
		sessionService: sessionService,
	}
}

// 按会话列出消息
func (h *MessageHandler) ListBySession(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)
	sessionID, err := uuid.Parse(c.Param("session_id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的会话ID"})
		return
	}

	// 验证用户是否有权访问该会话
	if err := h.sessionService.CheckAccess(sessionID, userID); err != nil {
		if err == service.ErrSessionNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "会话不存在"})
			return
		}
		if err == service.ErrForbidden {
			c.JSON(http.StatusForbidden, gin.H{"error": "无权限访问该会话"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	messages, err := h.messageService.ListBySession(sessionID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, messages)
}

// 发送消息
func (h *MessageHandler) Send(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	var req struct {
		SessionID string `json:"session_id" binding:"required"`
		Content   string `json:"content" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	sessionID, err := uuid.Parse(req.SessionID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的会话ID"})
		return
	}

	msg, err := h.messageService.Send(userID, sessionID, req.Content)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, msg)
}

// SendStream 流式发送消息
func (h *MessageHandler) SendStream(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	var req struct {
		SessionID string `json:"session_id" binding:"required"`
		Content   string `json:"content" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	sessionID, err := uuid.Parse(req.SessionID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的会话ID"})
		return
	}

	// 启动流式发送
	chunkChan, userMsg, err := h.messageService.SendStream(userID, sessionID, req.Content)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 设置 SSE headers
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("Transfer-Encoding", "chunked")

	// 先发送用户消息
	userMsgJSON, _ := json.Marshal(userMsg)
	c.Writer.Write([]byte(fmt.Sprintf("event: user_msg\ndata: %s\n\n", string(userMsgJSON))))
	c.Writer.Flush()

	// 流式发送 AI 回复
	for chunk := range chunkChan {
		if chunk.Content != "" {
			// 发送文本块
			contentJSON, _ := json.Marshal(chunk.Content)
			data := fmt.Sprintf(`{"type":"content","content":%s}`, string(contentJSON))
			c.Writer.Write([]byte(fmt.Sprintf("event: chunk\ndata: %s\n\n", data)))
			c.Writer.Flush()
		}
		if chunk.Done {
			// 发送完成信号
			if chunk.AssistantMsg != nil {
				assistantMsgJSON, _ := json.Marshal(chunk.AssistantMsg)
				sources := make([]map[string]interface{}, 0)
				for _, s := range chunk.Sources {
					sources = append(sources, map[string]interface{}{
						"source": s.Source,
						"score":  s.SemanticScore,
					})
				}
				doneData := map[string]interface{}{
					"type":          "done",
					"assistant_msg": string(assistantMsgJSON),
					"sources":       sources,
					"warning":       chunk.Warning,
				}
				doneJSON, _ := json.Marshal(doneData)
				c.Writer.Write([]byte(fmt.Sprintf("event: done\ndata: %s\n\n", string(doneJSON))))
				c.Writer.Flush()
			} else if chunk.Error != nil {
				// 发送错误信号
				c.Writer.Write([]byte(fmt.Sprintf("event: error\ndata: {\"error\":\"%s\"}\n\n", chunk.Error.Error())))
				c.Writer.Flush()
			}
		}
	}
}

// 发送图片消息
func (h *MessageHandler) SendImage(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	sessionIDStr := c.PostForm("session_id")
	if sessionIDStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "session_id is required"})
		return
	}

	sessionID, err := uuid.Parse(sessionIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的会话ID"})
		return
	}

	file, err := c.FormFile("image")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "请上传图片"})
		return
	}

	question := c.PostForm("question")
	if question == "" {
		question = "请分析这张图片中的宠物健康状况"
	}

	msg, err := h.messageService.SendImage(userID, sessionID, file, question)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, msg)
}
