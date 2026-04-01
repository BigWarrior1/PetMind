package service

import (
	"errors"

	"petmind-backend/internal/model"
	"petmind-backend/internal/repository"

	"github.com/google/uuid"
)

var (
	ErrPetNotFound  = errors.New("宠物不存在")
	ErrForbidden    = errors.New("无权限访问")
	ErrPetNameExists = errors.New("该宠物名字已存在")
)

type PetService struct {
	petRepo     *repository.PetRepository
	sessionRepo *repository.SessionRepository
}

func NewPetService(petRepo *repository.PetRepository, sessionRepo *repository.SessionRepository) *PetService {
	return &PetService{petRepo: petRepo, sessionRepo: sessionRepo}
}

func (s *PetService) Create(userID uuid.UUID, req *model.CreatePetRequest) (*model.Pet, error) {
	// 检查是否已存在同名宠物
	existing, err := s.petRepo.GetByUserAndName(userID, req.Name)
	if err == nil && existing != nil {
		return nil, ErrPetNameExists
	}

	pet := &model.Pet{
		UserID:   userID,
		Name:     req.Name,
		Species:  req.Species,
		Breed:    req.Breed,
		Age:      req.Age,
		Weight:   req.Weight,
		Gender:   req.Gender,
		Birthday: req.Birthday,
		Notes:    req.Notes,
	}

	if err := s.petRepo.Create(pet); err != nil {
		return nil, err
	}

	return pet, nil
}

func (s *PetService) List(userID uuid.UUID) ([]model.Pet, error) {
	return s.petRepo.List(userID)
}

func (s *PetService) Get(id uuid.UUID, userID uuid.UUID) (*model.Pet, error) {
	pet, err := s.petRepo.GetByID(id)
	if err != nil {
		return nil, ErrPetNotFound
	}

	if pet.UserID != userID {
		return nil, ErrForbidden
	}

	return pet, nil
}

func (s *PetService) Update(id uuid.UUID, userID uuid.UUID, req *model.UpdatePetRequest) (*model.Pet, error) {
	pet, err := s.Get(id, userID)
	if err != nil {
		return nil, err
	}

	// 更新字段
	if req.Name != "" {
		pet.Name = req.Name
	}
	if req.Species != "" {
		pet.Species = req.Species
	}
	if req.Breed != "" {
		pet.Breed = req.Breed
	}
	if req.Age != "" {
		pet.Age = req.Age
	}
	if req.Weight != "" {
		pet.Weight = req.Weight
	}
	if req.Gender != "" {
		pet.Gender = req.Gender
	}
	if req.Birthday != "" {
		pet.Birthday = req.Birthday
	}
	if req.Notes != "" {
		pet.Notes = req.Notes
	}

	if err := s.petRepo.Update(pet); err != nil {
		return nil, err
	}

	return pet, nil
}

func (s *PetService) Delete(id uuid.UUID, userID uuid.UUID) error {
	// 先删除该宠物关联的会话
	if s.sessionRepo != nil {
		s.sessionRepo.DeleteByPetID(id, userID)
	}
	return s.petRepo.Delete(id, userID)
}
