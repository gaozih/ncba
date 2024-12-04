from .base import BaseModel, db
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(BaseModel):
    """管理员模型"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # 管理员操作记录
    uploaded_reports = db.relationship('Report', backref='uploader', lazy='dynamic',
                                     foreign_keys='Report.uploaded_by')
    admin_logs = db.relationship('AdminLog', backref='admin', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class AdminLog(BaseModel):
    """管理员操作日志"""
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # upload, delete, modify, etc.
    resource_type = db.Column(db.String(50))  # report, user, admin, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))