package handler

import (
	"net/http"

	"petmind-backend/internal/model"
	"petmind-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type PetHandler struct {
	petService *service.PetService
}

func NewPetHandler(petService *service.PetService) *PetHandler {
	return &PetHandler{petService: petService}
}

// 创建宠物
func (h *PetHandler) Create(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	var req model.CreatePetRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	pet, err := h.petService.Create(userID, &req)
	if err != nil {
		if err == service.ErrPetNameExists {
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, pet)
}

// 列出宠物
func (h *PetHandler) List(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)

	pets, err := h.petService.List(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, pets)
}

// 获取宠物
func (h *PetHandler) Get(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)
	petID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的宠物ID"})
		return
	}

	pet, err := h.petService.Get(petID, userID)
	if err != nil {
		if err == service.ErrPetNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "宠物不存在"})
			return
		}
		if err == service.ErrForbidden {
			c.JSON(http.StatusForbidden, gin.H{"error": "无权限访问"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, pet)
}

// 更新宠物
func (h *PetHandler) Update(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)
	petID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的宠物ID"})
		return
	}

	var req model.UpdatePetRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	pet, err := h.petService.Update(petID, userID, &req)
	if err != nil {
		if err == service.ErrPetNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "宠物不存在"})
			return
		}
		if err == service.ErrForbidden {
			c.JSON(http.StatusForbidden, gin.H{"error": "无权限访问"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, pet)
}

// 删除宠物
func (h *PetHandler) Delete(c *gin.Context) {
	userID := c.MustGet("user_id").(uuid.UUID)
	petID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的宠物ID"})
		return
	}

	if err := h.petService.Delete(petID, userID); err != nil {
		if err == service.ErrPetNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "宠物不存在"})
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
