from functools import wraps
from flask import request, jsonify, current_app
import re
from datetime import datetime, timedelta
import redis
import jwt
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

# Redis连接
redis_client = redis.Redis(
    host=current_app.config['REDIS_HOST'],
    port=current_app.config['REDIS_PORT'],
    password=current_app.config['REDIS_PASSWORD']
)

class SecurityMiddleware:
    # IP限流
    @staticmethod
    def rate_limit(requests_per_minute=60):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                ip = request.remote_addr
                key = f'rate_limit:{ip}'
                
                # 获取当前请求次数
                requests = redis_client.get(key)
                if requests is None:
                    redis_client.setex(key, 60, 1)
                elif int(requests) >= requests_per_minute:
                    return jsonify({'error': '请求过于频繁，请稍后再试'}), 429
                else:
                    redis_client.incr(key)
                
                return f(*args, **kwargs)
            return wrapped
        return decorator

    # XSS防护
    @staticmethod
    def xss_protection():
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                if request.is_json:
                    data = request.get_json()
                    if SecurityMiddleware._contains_xss(data):
                        return jsonify({'error': '检测到恶意内容'}), 400
                return f(*args, **kwargs)
            return wrapped
        return decorator

    @staticmethod
    def _contains_xss(data):
        if isinstance(data, dict):
            return any(SecurityMiddleware._contains_xss(v) for v in data.values())
        elif isinstance(data, list):
            return any(SecurityMiddleware._contains_xss(item) for item in data)
        elif isinstance(data, str):
            xss_patterns = [
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'onerror=',
                r'onclick=',
                r'eval\(',
            ]
            return any(re.search(pattern, data, re.I) for pattern in xss_patterns)
        return False

    # JWT Token黑名单
    @staticmethod
    def check_token_blacklist():
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                verify_jwt_in_request()
                token = request.headers.get('Authorization').split(' ')[1]
                
                if redis_client.sismember('token_blacklist', token):
                    return jsonify({'error': '无效的token'}), 401
                    
                return f(*args, **kwargs)
            return wrapped
        return decorator

# 密码强度检查
def check_password_strength(password):
    if len(password) < 8:
        return False, '密码长度至少8位'
    
    if not re.search(r'[A-Z]', password):
        return False, '密码必须包含大写字母'
    
    if not re.search(r'[a-z]', password):
        return False, '密码必须包含小写字母'
    
    if not re.search(r'\d', password):
        return False, '密码必须包含数字'
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, '密码必须包含特殊字符'
    
    return True, '密码强度合格'

# 文件安全检查
def check_file_security(file):
    # 检查文件大小
    if len(file.read()) > current_app.config['MAX_CONTENT_LENGTH']:
        return False, '文件大小超过限制'
    file.seek(0)  # 重置文件指针
    
    # 检查文件类型
    allowed_types = {
        'application/pdf': [b'%PDF-']
    }
    
    content_type = file.content_type
    if content_type not in allowed_types:
        return False, '不支持的文件类型'
    
    # 检查文件头
    header = file.read(4)
    file.seek(0)
    if not any(header.startswith(sig) for sig in allowed_types[content_type]):
        return False, '文件格式不正确'
    
    return True, '文件检查通过'

# 手机号验证
def validate_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone)) 