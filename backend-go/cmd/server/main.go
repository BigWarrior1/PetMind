package main

import (
	"log"

	"petmind-backend/internal/config"
	"petmind-backend/internal/handler"
	"petmind-backend/internal/repository"
	"petmind-backend/internal/router"
	"petmind-backend/internal/service"
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
	adminRepo := repository.NewAdminRepository(db)

	// 初始化 Service
	authService := service.NewAuthService(userRepo, cfg.JWTSecret)
	petService := service.NewPetService(petRepo, sessionRepo)
	sessionService := service.NewSessionService(sessionRepo, messageRepo)
	messageService := service.NewMessageService(messageRepo, sessionRepo, petRepo, store)
	aiService := service.NewAIService(cfg.AIAPIURL)
	messageService.SetAIService(aiService)

	// 初始化 Handler
	authHandler := handler.NewAuthHandler(authService, cfg.AdminSecret)
	petHandler := handler.NewPetHandler(petService)
	sessionHandler := handler.NewSessionHandler(sessionService)
	messageHandler := handler.NewMessageHandler(messageService, sessionService)
	adminHandler := handler.NewAdminHandler(adminRepo)

	// 设置路由
	r := router.SetupRouter(authHandler, petHandler, sessionHandler, messageHandler, adminHandler, cfg.UploadDir, cfg.JWTSecret)

	// 启动服务
	log.Printf("服务器启动: http://localhost:%s", cfg.Port)
	r.Run(":" + cfg.Port)
}
