package repository

import (
	"petmind-backend/internal/model"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// AdminRepository 管理员专用仓储（分页查询、级联删除）
type AdminRepository struct {
	db *gorm.DB
}

func NewAdminRepository(db *gorm.DB) *AdminRepository {
	return &AdminRepository{db: db}
}

// ============ 用户管理 ============

// ListUsers 分页获取所有用户
func (r *AdminRepository) ListUsers(page, pageSize int) ([]model.User, int64, error) {
	var users []model.User
	var total int64

	r.db.Model(&model.User{}).Count(&total)

	offset := (page - 1) * pageSize
	if err := r.db.Order("created_at DESC").Offset(offset).Limit(pageSize).Find(&users).Error; err != nil {
		return nil, 0, err
	}

	return users, total, nil
}

// DeleteUser 删除用户（级联删除宠物、会话、消息）
func (r *AdminRepository) DeleteUser(userID uuid.UUID) error {
	return r.db.Transaction(func(tx *gorm.DB) error {
		// 获取该用户的所有宠物
		var pets []model.Pet
		if err := tx.Where("user_id = ?", userID).Find(&pets).Error; err != nil {
			return err
		}

		// 删除每个宠物的会话和消息
		for _, pet := range pets {
			// 获取该宠物的所有会话
			var sessions []model.Session
			if err := tx.Where("pet_id = ?", pet.ID).Find(&sessions).Error; err != nil {
				return err
			}

			for _, session := range sessions {
				// 删除会话消息
				if err := tx.Where("session_id = ?", session.ID).Delete(&model.Message{}).Error; err != nil {
					return err
				}
			}
			// 删除会话
			if err := tx.Where("pet_id = ?", pet.ID).Delete(&model.Session{}).Error; err != nil {
				return err
			}
		}

		// 删除该用户的宠物
		if err := tx.Where("user_id = ?", userID).Delete(&model.Pet{}).Error; err != nil {
			return err
		}

		// 获取该用户的所有会话（不含宠物）
		var sessions []model.Session
		if err := tx.Where("user_id = ? AND pet_id IS NULL", userID).Find(&sessions).Error; err != nil {
			return err
		}

		for _, session := range sessions {
			// 删除会话消息
			if err := tx.Where("session_id = ?", session.ID).Delete(&model.Message{}).Error; err != nil {
				return err
			}
		}
		// 删除会话
		if err := tx.Where("user_id = ? AND pet_id IS NULL", userID).Delete(&model.Session{}).Error; err != nil {
			return err
		}

		// 删除用户
		if err := tx.Delete(&model.User{}, userID).Error; err != nil {
			return err
		}

		return nil
	})
}

// ============ 宠物管理 ============

// ListPets 分页获取所有宠物
func (r *AdminRepository) ListPets(page, pageSize int) ([]model.Pet, int64, error) {
	var pets []model.Pet
	var total int64

	r.db.Model(&model.Pet{}).Count(&total)

	offset := (page - 1) * pageSize
	if err := r.db.Order("created_at DESC").Offset(offset).Limit(pageSize).Find(&pets).Error; err != nil {
		return nil, 0, err
	}

	return pets, total, nil
}

// DeletePet 删除宠物（级联删除会话、消息）
func (r *AdminRepository) DeletePet(petID uuid.UUID) error {
	return r.db.Transaction(func(tx *gorm.DB) error {
		// 获取该宠物的所有会话
		var sessions []model.Session
		if err := tx.Where("pet_id = ?", petID).Find(&sessions).Error; err != nil {
			return err
		}

		for _, session := range sessions {
			// 删除会话消息
			if err := tx.Where("session_id = ?", session.ID).Delete(&model.Message{}).Error; err != nil {
				return err
			}
		}
		// 删除会话
		if err := tx.Where("pet_id = ?", petID).Delete(&model.Session{}).Error; err != nil {
			return err
		}

		// 删除宠物
		if err := tx.Delete(&model.Pet{}, petID).Error; err != nil {
			return err
		}

		return nil
	})
}

// ============ 会话管理 ============

// ListSessions 分页获取所有会话
func (r *AdminRepository) ListSessions(page, pageSize int) ([]model.Session, int64, error) {
	var sessions []model.Session
	var total int64

	r.db.Model(&model.Session{}).Count(&total)

	offset := (page - 1) * pageSize
	if err := r.db.Order("updated_at DESC").Offset(offset).Limit(pageSize).Find(&sessions).Error; err != nil {
		return nil, 0, err
	}

	return sessions, total, nil
}

// GetSessionMessages 获取会话的所有消息
func (r *AdminRepository) GetSessionMessages(sessionID uuid.UUID) ([]model.Message, error) {
	var messages []model.Message
	if err := r.db.Where("session_id = ?", sessionID).Order("created_at ASC").Find(&messages).Error; err != nil {
		return nil, err
	}
	return messages, nil
}

// DeleteSession 删除会话（级联删除消息）
func (r *AdminRepository) DeleteSession(sessionID uuid.UUID) error {
	return r.db.Transaction(func(tx *gorm.DB) error {
		// 删除消息
		if err := tx.Where("session_id = ?", sessionID).Delete(&model.Message{}).Error; err != nil {
			return err
		}
		// 删除会话
		if err := tx.Delete(&model.Session{}, sessionID).Error; err != nil {
			return err
		}
		return nil
	})
}

// ============ 统计 ============

// GetStats 获取统计数据
func (r *AdminRepository) GetStats() (map[string]int64, error) {
	var userCount int64
	var petCount int64
	var sessionCount int64
	var messageCount int64

	r.db.Model(&model.User{}).Count(&userCount)
	r.db.Model(&model.Pet{}).Count(&petCount)
	r.db.Model(&model.Session{}).Count(&sessionCount)
	r.db.Model(&model.Message{}).Count(&messageCount)

	return map[string]int64{
		"users":    userCount,
		"pets":     petCount,
		"sessions": sessionCount,
		"messages": messageCount,
	}, nil
}
