package repository

import (
	"fmt"
	"log"
	"os"
	"path/filepath"

	"petmind-backend/internal/config"
	"petmind-backend/internal/model"

	"github.com/google/uuid"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func InitDB(cfg *config.Config) (*gorm.DB, error) {
	// 确保目录存在
	dir := filepath.Dir(cfg.DBPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("创建数据库目录失败: %w", err)
	}

	// 连接数据库
	db, err := gorm.Open(sqlite.Open(cfg.DBPath), &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("连接数据库失败: %w", err)
	}

	// 自动迁移
	if err := db.AutoMigrate(
		&model.User{},
		&model.Pet{},
		&model.Session{},
		&model.Message{},
	); err != nil {
		return nil, fmt.Errorf("数据库迁移失败: %w", err)
	}

	log.Printf("数据库初始化成功: %s", cfg.DBPath)
	return db, nil
}

// User Repository

type UserRepository struct {
	db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) Create(user *model.User) error {
	user.ID = uuid.New()
	return r.db.Create(user).Error
}

func (r *UserRepository) GetByID(id uuid.UUID) (*model.User, error) {
	var user model.User
	if err := r.db.First(&user, "id = ?", id).Error; err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) GetByUsername(username string) (*model.User, error) {
	var user model.User
	if err := r.db.First(&user, "username = ?", username).Error; err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) GetByEmail(email string) (*model.User, error) {
	var user model.User
	if err := r.db.First(&user, "email = ?", email).Error; err != nil {
		return nil, err
	}
	return &user, nil
}

// Pet Repository

type PetRepository struct {
	db *gorm.DB
}

func NewPetRepository(db *gorm.DB) *PetRepository {
	return &PetRepository{db: db}
}

func (r *PetRepository) Create(pet *model.Pet) error {
	pet.ID = uuid.New()
	return r.db.Create(pet).Error
}

func (r *PetRepository) GetByID(id uuid.UUID) (*model.Pet, error) {
	var pet model.Pet
	if err := r.db.First(&pet, "id = ?", id).Error; err != nil {
		return nil, err
	}
	return &pet, nil
}

func (r *PetRepository) List(userID uuid.UUID) ([]model.Pet, error) {
	var pets []model.Pet
	if err := r.db.Where("user_id = ?", userID).Order("created_at DESC").Find(&pets).Error; err != nil {
		return nil, err
	}
	return pets, nil
}

func (r *PetRepository) GetByUserAndName(userID uuid.UUID, name string) (*model.Pet, error) {
	var pet model.Pet
	if err := r.db.Where("user_id = ? AND name = ?", userID, name).First(&pet).Error; err != nil {
		return nil, err
	}
	return &pet, nil
}

func (r *PetRepository) Update(pet *model.Pet) error {
	return r.db.Save(pet).Error
}

func (r *PetRepository) Delete(id uuid.UUID, userID uuid.UUID) error {
	return r.db.Where("id = ? AND user_id = ?", id, userID).Delete(&model.Pet{}).Error
}

// Session Repository

type SessionRepository struct {
	db *gorm.DB
}

func NewSessionRepository(db *gorm.DB) *SessionRepository {
	return &SessionRepository{db: db}
}

func (r *SessionRepository) Create(session *model.Session) error {
	session.ID = uuid.New()
	return r.db.Create(session).Error
}

func (r *SessionRepository) GetByID(id uuid.UUID) (*model.Session, error) {
	var session model.Session
	if err := r.db.First(&session, "id = ?", id).Error; err != nil {
		return nil, err
	}
	return &session, nil
}

func (r *SessionRepository) List(userID uuid.UUID) ([]model.Session, error) {
	var sessions []model.Session
	if err := r.db.Where("user_id = ?", userID).Order("updated_at DESC").Find(&sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}

func (r *SessionRepository) Delete(id uuid.UUID, userID uuid.UUID) error {
	return r.db.Where("id = ? AND user_id = ?", id, userID).Delete(&model.Session{}).Error
}

func (r *SessionRepository) Update(session *model.Session) error {
	return r.db.Save(session).Error
}

func (r *SessionRepository) GetByUserAndPet(userID uuid.UUID, petID uuid.UUID) (*model.Session, error) {
	var session model.Session
	if err := r.db.Where("user_id = ? AND pet_id = ?", userID, petID).First(&session).Error; err != nil {
		return nil, err
	}
	return &session, nil
}

func (r *SessionRepository) DeleteByPetID(petID uuid.UUID, userID uuid.UUID) error {
	return r.db.Where("pet_id = ? AND user_id = ?", petID, userID).Delete(&model.Session{}).Error
}

// Message Repository

type MessageRepository struct {
	db *gorm.DB
}

func NewMessageRepository(db *gorm.DB) *MessageRepository {
	return &MessageRepository{db: db}
}

func (r *MessageRepository) Create(msg *model.Message) error {
	msg.ID = uuid.New()
	return r.db.Create(msg).Error
}

func (r *MessageRepository) ListBySession(sessionID uuid.UUID) ([]model.Message, error) {
	var messages []model.Message
	if err := r.db.Where("session_id = ?", sessionID).Order("created_at ASC").Find(&messages).Error; err != nil {
		return nil, err
	}
	return messages, nil
}

func (r *MessageRepository) DeleteBySessionID(sessionID uuid.UUID) error {
	return r.db.Where("session_id = ?", sessionID).Delete(&model.Message{}).Error
}

// File Store

type FileStore struct {
	baseDir string
}

func NewFileStore(baseDir string) *FileStore {
	os.MkdirAll(baseDir, 0755)
	return &FileStore{baseDir: baseDir}
}

func (f *FileStore) Save(userID, sessionID, filename string, data []byte) (string, error) {
	dir := filepath.Join(f.baseDir, userID, sessionID)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return "", err
	}

	ext := filepath.Ext(filename)
	newFilename := fmt.Sprintf("%s%s", uuid.New().String(), ext)
	path := filepath.Join(dir, newFilename)

	if err := os.WriteFile(path, data, 0644); err != nil {
		return "", err
	}

	return path, nil
}
