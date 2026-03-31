package handler

import (
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
