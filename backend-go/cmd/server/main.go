package main

import (
	"log"

	"petmind-backend/internal/config"
	"petmind-backend/internal/handler"
	"petmind-backend/internal/middleware"
	"petmind-backend/internal/repository"
	"petmind-backend/internal/service"

	"github.com/gin-gonic/gin"
)

func main() {
	// 加载配置
	cfg, err := config.LoadDefault()
	if err != nil {
		log.Fatalf("配置加载失败: %v", err)
	}

	// 初始化数据库
	db, err := repository.InitDB(cfg)
	if err != nil {
		log.Fatalf("数据库初始化失败: %v", err)
	}

	// 初始化存储
	store := repository.NewFileStore(cfg.UploadDir)

	// 初始化 Repository
	userRepo := repository.NewUserRepository(db)
	petRepo := repository.NewPetRepository(db)
	sessionRepo := repository.NewSessionRepository(db)
	messageRepo := repository.NewMessageRepository(db)

	// 初始化 Service
	authService := service.NewAuthService(userRepo, cfg.JWTSecret)
	petService := service.NewPetService(petRepo, sessionRepo)
	sessionService := service.NewSessionService(sessionRepo, messageRepo)
	messageService := service.NewMessageService(messageRepo, sessionRepo, petRepo, store)
	aiService := service.NewAIService(cfg.AIAPIURL)
	messageService.SetAIService(aiService)

	// 初始化 Handler
	authHandler := handler.NewAuthHandler(authService)
	petHandler := handler.NewPetHandler(petService)
	sessionHandler := handler.NewSessionHandler(sessionService)
	messageHandler := handler.NewMessageHandler(messageService, sessionService)

	// 启动 Gin
	r := gin.Default()

	// 中间件
	r.Use(middleware.CORS())
	r.Use(middleware.Logger())

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
		protected.Use(middleware.Auth(cfg.JWTSecret))
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

	// 启动服务
	log.Printf("服务器启动: http://localhost:%s", cfg.Port)
	r.Run(":" + cfg.Port)
}
