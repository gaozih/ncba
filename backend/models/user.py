from .base import BaseModel, db

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # 关联关系
    reports = db.relationship('Report', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    verification_codes = db.relationship('VerificationCode', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.phone}>'

class VerificationCode(BaseModel):
    """验证码模型"""
    __tablename__ = 'verification_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at 