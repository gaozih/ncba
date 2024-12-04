import os

class Config:
    # 基础配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'reports.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-please-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24小时
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # 短信验证码配置
    SMS_CODE_EXPIRE = 300  # 验证码有效期（秒）
    
    # 跨域配置
    CORS_ORIGINS = ['http://localhost:8080']  # 允许跨域的域名列表
    
    # PDF预览配置
    PDF_VIEWER_URL = 'https://mozilla.github.io/pdf.js/web/viewer.html'  # 使用Mozilla的PDF.js
    API_BASE_URL = 'http://your_api_domain'  # 生产环境需要改为实际域名
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # 安全头配置
    SECURITY_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:8080']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    
    # 登录安全配置
    LOGIN_ATTEMPT_LIMIT = 5
    LOGIN_ATTEMPT_TIMEOUT = 300  # 5分钟
    PASSWORD_MIN_LENGTH = 8

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    # 生产环境特定配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 