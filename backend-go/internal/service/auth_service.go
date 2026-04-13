package service

import (
	"errors"
	"time"

	"petmind-backend/internal/model"
	"petmind-backend/internal/repository"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

var (
	ErrUserNotFound       = errors.New("用户不存在")
	ErrInvalidPassword    = errors.New("密码错误")
	ErrUserAlreadyExists  = errors.New("用户已存在")
)

type AuthService struct {
	userRepo   *repository.UserRepository
	jwtSecret string
}

func NewAuthService(userRepo *repository.UserRepository, jwtSecret string) *AuthService {
	return &AuthService{
		userRepo:   userRepo,
		jwtSecret: jwtSecret,
	}
}

func (s *AuthService) Register(req *model.RegisterRequest) (*model.User, error) {
	// 检查用户名是否存在
	if _, err := s.userRepo.GetByUsername(req.Username); err == nil {
		return nil, ErrUserAlreadyExists
	}

	// 检查邮箱是否存在
	if _, err := s.userRepo.GetByEmail(req.Email); err == nil {
		return nil, ErrUserAlreadyExists
	}

	// 加密密码
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	user := &model.User{
		Username: req.Username,
		Email:    req.Email,
		Password: string(hashedPassword),
	}

	if err := s.userRepo.Create(user); err != nil {
		return nil, err
	}

	return user, nil
}

func (s *AuthService) Login(req *model.LoginRequest) (*model.LoginResponse, error) {
	user, err := s.userRepo.GetByUsername(req.Username)
	if err != nil {
		return nil, ErrUserNotFound
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		return nil, ErrInvalidPassword
	}

	// 生成 JWT（包含 role）
	token, err := s.generateToken(user.ID, user.Role)
	if err != nil {
		return nil, err
	}

	return &model.LoginResponse{
		Token: token,
		User:  *user,
	}, nil
}

// AdminRegister 管理员注册
func (s *AuthService) AdminRegister(req *model.AdminRegisterRequest, adminSecret string) (*model.LoginResponse, error) {
	// 验证管理员密钥
	if req.AdminSecret != adminSecret {
		return nil, errors.New("管理员密钥错误")
	}

	// 检查用户名是否存在
	if _, err := s.userRepo.GetByUsername(req.Username); err == nil {
		return nil, ErrUserAlreadyExists
	}

	// 检查邮箱是否存在
	if _, err := s.userRepo.GetByEmail(req.Email); err == nil {
		return nil, ErrUserAlreadyExists
	}

	// 加密密码
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	user := &model.User{
		Username: req.Username,
		Email:    req.Email,
		Password: string(hashedPassword),
		Role:     "admin",
	}

	if err := s.userRepo.Create(user); err != nil {
		return nil, err
	}

	// 生成 JWT（包含 role）
	token, err := s.generateToken(user.ID, user.Role)
	if err != nil {
		return nil, err
	}

	return &model.LoginResponse{
		Token: token,
		User:  *user,
	}, nil
}

// AdminLogin 管理员登录
func (s *AuthService) AdminLogin(req *model.AdminLoginRequest) (*model.LoginResponse, error) {
	user, err := s.userRepo.GetByUsername(req.Username)
	if err != nil {
		return nil, ErrUserNotFound
	}

	if user.Role != "admin" {
		return nil, errors.New("该用户不是管理员")
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		return nil, ErrInvalidPassword
	}

	// 生成 JWT（包含 role）
	token, err := s.generateToken(user.ID, user.Role)
	if err != nil {
		return nil, err
	}

	return &model.LoginResponse{
		Token: token,
		User:  *user,
	}, nil
}

func (s *AuthService) generateToken(userID uuid.UUID, role string) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID.String(),
		"role":    role,
		"exp":     time.Now().Add(7 * 24 * time.Hour).Unix(), // 7天过期
		"iat":     time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(s.jwtSecret))
}

func (s *AuthService) ValidateToken(tokenString string) (uuid.UUID, string, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		return []byte(s.jwtSecret), nil
	})

	if err != nil || !token.Valid {
		return uuid.Nil, "", errors.New("无效的token")
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return uuid.Nil, "", errors.New("无效的token claims")
	}

	userIDStr, ok := claims["user_id"].(string)
	if !ok {
		return uuid.Nil, "", errors.New("无效的user_id")
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		return uuid.Nil, "", errors.New("无效的user_id")
	}

	role, _ := claims["role"].(string)
	if role == "" {
		role = "user"
	}

	return userID, role, nil
}
