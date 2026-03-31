package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/viper"
)

// Config 应用配置
type Config struct {
	// JWT 配置
	JWTSecret string `mapstructure:"jwt_secret"`

	// 数据库配置
	DBType     string `mapstructure:"db_type"`
	DBPath     string `mapstructure:"db_path"`
	DBHost     string `mapstructure:"db_host"`
	DBPort     string `mapstructure:"db_port"`
	DBUser     string `mapstructure:"db_user"`
	DBPassword string `mapstructure:"db_password"`
	DBName     string `mapstructure:"db_name"`

	// AI 服务配置
	AIAPIURL string `mapstructure:"ai_api_url"`

	// 文件上传配置
	UploadDir string `mapstructure:"upload_dir"`

	// 服务器配置
	Port string `mapstructure:"port"`
}

// getExecutableDir 获取程序所在目录
// 用于定位配置文件等资源文件
func getExecutableDir() string {
	// 获取可执行文件路径
	exe, err := os.Executable()
	if err != nil {
		// 失败时降级到工作目录
		exe, _ = os.Getwd()
		return exe
	}
	return filepath.Dir(exe)
}

// Load 加载配置
// 优先级：环境变量 > 命令行标志 > 配置文件 > 默认值
func Load(configPath string) (*Config, error) {
	v := viper.New()

	// 设置配置文件名和类型
	v.SetConfigName("config")
	v.SetConfigType("yaml")

	// 添加配置文件搜索路径（按优先级排序）
	// 1. 程序所在目录（最优先，用于打包后的程序）
	execDir := getExecutableDir()
	v.AddConfigPath(execDir)
	v.AddConfigPath(filepath.Join(execDir, "config"))

	// 2. 当前工作目录（开发时使用）
	v.AddConfigPath(".")
	v.AddConfigPath("./config")

	// 3. 系统配置目录（生产环境）
	v.AddConfigPath("/etc/petmind/")

	// 如果指定了配置路径，添加它（最高优先级）
	if configPath != "" {
		v.AddConfigPath(configPath)
	}

	// 环境变量配置
	v.SetEnvPrefix("PETMIND")                                  // 环境变量前缀: PETMIND_JWT_SECRET
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))        // db.path -> DB_PATH
	v.AutomaticEnv()                                           // 允许环境变量覆盖

	// 配置键名（与 yaml/json 一致）
	v.SetDefault("jwt_secret", "your-secret-key-change-in-production")
	v.SetDefault("db_type", "sqlite")
	v.SetDefault("db_path", "./data/petmind.db")
	v.SetDefault("db_host", "localhost")
	v.SetDefault("db_port", "5432")
	v.SetDefault("db_user", "postgres")
	v.SetDefault("db_password", "postgres")
	v.SetDefault("db_name", "petmind")
	v.SetDefault("ai_api_url", "http://localhost:8000/api/v1")
	v.SetDefault("upload_dir", "./data/uploads")
	v.SetDefault("port", "8080")

	// 读取配置文件（忽略错误，允许只有环境变量的情况）
	if err := v.ReadInConfig(); err != nil {
		// 只在不是"文件未找到"错误时打印警告
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			fmt.Printf("警告: 读取配置文件失败: %v\n", err)
		}
	}

	// 解析配置到结构体
	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("解析配置失败: %w", err)
	}

	return &cfg, nil
}

// LoadDefault 使用默认路径加载配置
func LoadDefault() (*Config, error) {
	return Load("")
}
