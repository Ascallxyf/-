"""
应用配置文件
Configuration for the application
使用 pathlib 统一路径，确保不同电脑/操作系统上的路径一致。
"""
import os
from pathlib import Path

# 项目根目录（.../智能穿搭推荐平台）
BASE_DIR: Path = Path(__file__).resolve().parents[2]
# 前端与实例目录
FRONTEND_DIR: Path = BASE_DIR / 'frontend'
TEMPLATES_DIR: Path = FRONTEND_DIR / 'templates'
STATIC_DIR: Path = FRONTEND_DIR / 'static'
UPLOADS_DIR: Path = STATIC_DIR / 'uploads'
INSTANCE_DIR: Path = BASE_DIR / 'instance'

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # 优先使用环境变量 DATABASE_URL，否则使用 instance 目录下的 sqlite 文件
    # 注意 sqlite 绝对路径 URI 需要使用正斜杠
    _default_sqlite_path = (INSTANCE_DIR / 'wardrobe.db')
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f"sqlite:///{_default_sqlite_path.resolve().as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 统一的上传目录（前端静态目录下）
    UPLOAD_FOLDER = str(UPLOADS_DIR)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # 创建上传目录
    @staticmethod
    def init_app(app):
        # 确保上传目录与 instance 目录存在
        Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/fashion_rec'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
