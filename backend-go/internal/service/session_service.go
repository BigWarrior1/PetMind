package service

import (
	"errors"
	"time"

	"petmind-backend/internal/model"
	"petmind-backend/internal/repository"

	"github.com/google/uuid"
)

var (
	ErrSessionNotFound = errors.New("会话不存在")
)

type SessionService struct {
	sessionRepo  *repository.SessionRepository
	messageRepo *repository.MessageRepository
}

func NewSessionService(sessionRepo *repository.SessionRepository, messageRepo *repository.MessageRepository) *SessionService {
	return &SessionService{sessionRepo: sessionRepo, messageRepo: messageRepo}
}

func (s *SessionService) Create(userID uuid.UUID, req *model.CreateSessionRequest) (*model.Session, error) {
	// 如果是宠物专属对话，检查是否已存在
	if req.PetID != nil {
		existing, err := s.sessionRepo.GetByUserAndPet(userID, *req.PetID)
		if err == nil && existing != nil {
			// 已存在该宠物会话，返回已有会话
			return existing, nil
		}
	}

	session := &model.Session{
		UserID: userID,
		PetID:  req.PetID,
		Title:  req.Title,
	}

	// 如果没有提供标题，设置默认标题
	if session.Title == "" {
		session.Title = "新对话"
	}

	if err := s.sessionRepo.Create(session); err != nil {
		return nil, err
	}

	return session, nil
}

func (s *SessionService) List(userID uuid.UUID) ([]model.Session, error) {
	return s.sessionRepo.List(userID)
}

func (s *SessionService) Get(id uuid.UUID, userID uuid.UUID) (*model.Session, error) {
	session, err := s.sessionRepo.GetByID(id)
	if err != nil {
		return nil, ErrSessionNotFound
	}

	if session.UserID != userID {
		return nil, ErrForbidden
	}

	return session, nil
}

func (s *SessionService) Delete(id uuid.UUID, userID uuid.UUID) error {
	// 先删除该会话的所有消息
	if s.messageRepo != nil {
		s.messageRepo.DeleteBySessionID(id)
	}
	return s.sessionRepo.Delete(id, userID)
}

func (s *SessionService) UpdateUpdatedAt(id uuid.UUID) error {
	session, err := s.sessionRepo.GetByID(id)
	if err != nil {
		return err
	}
	session.UpdatedAt = time.Now()
	return s.sessionRepo.Update(session)
}

// UpdateTitle 更新会话标题
func (s *SessionService) UpdateTitle(id uuid.UUID, userID uuid.UUID, title string) error {
	session, err := s.sessionRepo.GetByID(id)
	if err != nil {
		return ErrSessionNotFound
	}

	if session.UserID != userID {
		return ErrForbidden
	}

	session.Title = title
	session.UpdatedAt = time.Now()
	return s.sessionRepo.Update(session)
}

// CheckAccess 验证用户是否有权访问该会话
func (s *SessionService) CheckAccess(sessionID, userID uuid.UUID) error {
	session, err := s.sessionRepo.GetByID(sessionID)
	if err != nil {
		return ErrSessionNotFound
	}

	if session.UserID != userID {
		return ErrForbidden
	}

	return nil
}
