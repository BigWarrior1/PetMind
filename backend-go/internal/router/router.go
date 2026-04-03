package router

import (
	"petmind-backend/internal/handler"
	"petmind-backend/internal/middleware"

	"github.com/gin-gonic/gin"
)

// SetupRouter 配置路由并返回 Gin 引擎
func SetupRouter(
	authHandler *handler.AuthHandler,
	petHandler *handler.PetHandler,
	sessionHandler *handler.SessionHandler,
	messageHandler *handler.MessageHandler,
	uploadDir string,
	jwtSecret string,
) *gin.Engine {
	r := gin.Default()

	// 中间件
	r.Use(middleware.CORS())
	r.Use(middleware.Logger())

	// 静态文件服务（上传的图片）
	r.Static("/uploads", uploadDir)

	// API 路由
	api := r.Group("/api/v1")
	{
		// 认证
		auth := api.Group("/auth")
		{
			auth.POST("/register", authHandler.Register)
			auth.POST("/login", authHandler.Login)
		}

		// 需要认证的路由
		protected := api.Group("")
		protected.Use(middleware.Auth(jwtSecret))
		{
			// 宠物档案
			pets := protected.Group("/pets")
			{
				pets.GET("", petHandler.List)
				pets.POST("", petHandler.Create)
				pets.GET("/:id", petHandler.Get)
				pets.PUT("/:id", petHandler.Update)
				pets.DELETE("/:id", petHandler.Delete)
			}

			// 会话
			sessions := protected.Group("/sessions")
			{
				sessions.GET("", sessionHandler.List)
				sessions.POST("", sessionHandler.Create)
				sessions.GET("/:id", sessionHandler.Get)
				sessions.DELETE("/:id", sessionHandler.Delete)
			}

			// 消息
			messages := protected.Group("/messages")
			{
				messages.GET("/session/:session_id", messageHandler.ListBySession)
				messages.POST("", messageHandler.Send)
				messages.POST("/stream", messageHandler.SendStream)
				messages.POST("/image", messageHandler.SendImage)
			}
		}
	}

	// 健康检查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	return r
}
