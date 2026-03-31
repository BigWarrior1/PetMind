package handler

import (
	"net/http"

	"petmind-backend/internal/model"
	"petmind-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type SessionHandler struct {
	sessionService *service.SessionService
}

func NewSessionHandler(sessionService *service.SessionService) *SessionHandler {
	return &SessionHandler{sessionService: sessionService}
}

// 创建会话
func (h *SessionHandler) Create(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	var req model.CreateSessionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	session, err := h.sessionService.Create(userID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, session)
}

// 列出会话
func (h *SessionHandler) List(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	sessions, err := h.sessionService.List(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, sessions)
}

// 获取会话
func (h *SessionHandler) Get(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)
	sessionID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的会话ID"})
		return
	}

	session, err := h.sessionService.Get(sessionID, userID)
	if err != nil {
		if err == service.ErrSessionNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "会话不存在"})
			return
		}
		if err == service.ErrForbidden {
			c.JSON(http.StatusForbidden, gin.H{"error": "无权限访问"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, session)
}

// 删除会话
func (h *SessionHandler) Delete(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)
	sessionID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的会话ID"})
		return
	}

	if err := h.sessionService.Delete(sessionID, userID); err != nil {
		if err == service.ErrSessionNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "会话不存在"})
			return
		}
		if err == service.ErrForbidden {
			c.JSON(http.StatusForbidden, gin.H{"error": "无权限访问"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "删除成功"})
}
