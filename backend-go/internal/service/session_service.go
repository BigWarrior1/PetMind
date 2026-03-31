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
	sessionRepo *repository.SessionRepository
}

func NewSessionService(sessionRepo *repository.SessionRepository) *SessionService {
	return &SessionService{sessionRepo: sessionRepo}
}

func (s *SessionService) Create(userID uuid.UUID, req *model.CreateSessionRequest) (*model.Session, error) {
	session := &model.Session{
		UserID: userID,
		PetID:  req.PetID,
		Title:  req.Title,
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
