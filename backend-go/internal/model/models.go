package model

import (
	"time"

	"github.com/google/uuid"
)

// 用户
type User struct {
	ID        uuid.UUID `json:"id" gorm:"type:text;primaryKey"`
	Username  string    `json:"username" gorm:"uniqueIndex;not null"`
	Email     string    `json:"email" gorm:"uniqueIndex;not null"`
	Password  string    `json:"-" gorm:"not null"` // 不返回给前端
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// 宠物档案
type Pet struct {
	ID        uuid.UUID `json:"id" gorm:"type:text;primaryKey"`
	UserID    uuid.UUID `json:"user_id" gorm:"type:text;not null;index"`
	Name      string    `json:"name" gorm:"not null"`
	Species   string    `json:"species"`  // 种类：狗、猫
	Breed     string    `json:"breed"`    // 品种
	Age       string    `json:"age"`      // 年龄
	Weight    string    `json:"weight"`   // 体重
	Gender    string    `json:"gender"`   // 性别
	Birthday  string    `json:"birthday"` // 生日
	Notes     string    `json:"notes"`    // 备注
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// 会话
type Session struct {
	ID               uuid.UUID  `json:"id" gorm:"type:text;primaryKey"`
	UserID           uuid.UUID `json:"user_id" gorm:"type:text;not null;index"`
	PetID            *uuid.UUID `json:"pet_id" gorm:"type:text;index"` // 可选，关联宠物
	Title            string    `json:"title" gorm:"not null"`
	Summary          string    `json:"summary" gorm:"type:text"`           // 会话摘要
	SummaryUpdatedAt *time.Time `json:"summary_updated_at"`                  // 摘要更新时间
	CreatedAt        time.Time `json:"created_at"`
	UpdatedAt        time.Time `json:"updated_at"`
}

// 消息
type Message struct {
	ID         uuid.UUID  `json:"id" gorm:"type:text;primaryKey"`
	SessionID  uuid.UUID  `json:"session_id" gorm:"type:text;not null;index"`
	Role       string     `json:"role" gorm:"not null"` // user 或 assistant
	Content    string     `json:"content" gorm:"not null"`
	ImageURLs  string     `json:"image_urls" gorm:"type:text"` // JSON 数组，存储图片路径
	Sources    string     `json:"sources" gorm:"type:text"`    // JSON 数组，RAG 来源
	CreatedAt  time.Time  `json:"created_at"`
}

// 请求/响应 DTO

// 注册请求
type RegisterRequest struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
}

// 登录请求
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// 登录响应
type LoginResponse struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}

// 创建宠物请求
type CreatePetRequest struct {
	Name     string `json:"name" binding:"required"`
	Species  string `json:"species"`
	Breed    string `json:"breed"`
	Age      string `json:"age"`
	Weight   string `json:"weight"`
	Gender   string `json:"gender"`
	Birthday string `json:"birthday"`
	Notes    string `json:"notes"`
}

// 更新宠物请求
type UpdatePetRequest struct {
	Name     string `json:"name"`
	Species  string `json:"species"`
	Breed    string `json:"breed"`
	Age      string `json:"age"`
	Weight   string `json:"weight"`
	Gender   string `json:"gender"`
	Birthday string `json:"birthday"`
	Notes    string `json:"notes"`
}

// 创建会话请求
type CreateSessionRequest struct {
	PetID *uuid.UUID `json:"pet_id"`
	Title string    `json:"title" binding:"required"`
}

// 发送消息请求
type SendMessageRequest struct {
	SessionID string `json:"session_id" binding:"required"`
	Content   string `json:"content"`
}

// AI 响应
type AIResponse struct {
	Answer  string       `json:"answer"`
	Sources []SourceInfo `json:"sources"`
	Warning string       `json:"warning,omitempty"`
}

type SourceInfo struct {
	Source       string  `json:"source"`
	SourceType   string  `json:"source_type"`
	Confidence   float64 `json:"confidence"`
	SemanticScore float64 `json:"semantic_score"`
}
