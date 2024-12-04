from .base import BaseModel, db
import os

class Report(BaseModel):
    """报告模型"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    mime_type = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    
    # 元数据
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))
    
    # 状态
    status = db.Column(db.String(20), default='active')  # active, archived, deleted
    
    # 访问记录
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    last_viewed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Report {self.filename}>'
    
    @property
    def file_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOAD_FOLDER'], self.filename)
    
    def increment_view_count(self):
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()
        db.session.commit()
    
    def increment_download_count(self):
        self.download_count += 1
        db.session.commit()

class ReportAccess(BaseModel):
    """报告访问记录"""
    __tablename__ = 'report_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_type = db.Column(db.String(20))  # view, download
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    
    report = db.relationship('Report', backref=db.backref('access_logs', lazy='dynamic')) 