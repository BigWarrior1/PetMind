package service

import (
	"errors"

	"petmind-backend/internal/model"
	"petmind-backend/internal/repository"

	"github.com/google/uuid"
)

var (
	ErrPetNotFound = errors.New("宠物不存在")
	ErrForbidden   = errors.New("无权限访问")
)

type PetService struct {
	petRepo *repository.PetRepository
}

func NewPetService(petRepo *repository.PetRepository) *PetService {
	return &PetService{petRepo: petRepo}
}

func (s *PetService) Create(userID uuid.UUID, req *model.CreatePetRequest) (*model.Pet, error) {
	pet := &model.Pet{
		UserID: userID,
		Name:   req.Name,
		Species: req.Species,
		Breed:  req.Breed,
		Age:    req.Age,
		Weight: req.Weight,
		Gender: req.Gender,
		Birthday: req.Birthday,
		Notes:  req.Notes,
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
	return s.petRepo.Delete(id, userID)
}
