from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from datetime import datetime, timedelta
from config import config
import hashlib
from api.admin import admin_bp
from security import SecurityMiddleware, check_password_strength, check_file_security, validate_phone
from flask_cors import CORS
from flask_talisman import Talisman

app = Flask(__name__)
app.config.from_object(config['default'])

db = SQLAlchemy(app)
jwt = JWTManager(app)

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": app.config['CORS_METHODS'],
        "allow_headers": app.config['CORS_ALLOW_HEADERS']
    }
})

# 配置安全头
Talisman(app,
    force_https=True,
    strict_transport_security=True,
    session_cookie_secure=True,
    content_security_policy=app.config['SECURITY_HEADERS']['Content-Security-Policy']
)

# 全局错误处理
@app.errorhandler(Exception)
def handle_error(error):
    if isinstance(error, HTTPException):
        return jsonify({'error': error.description}), error.code
    
    current_app.logger.error(f'Unhandled error: {str(error)}')
    return jsonify({'error': '服务器内部错误'}), 500

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    reports = db.relationship('Report', backref='user', lazy=True)

# 报告模型
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    phone = request.json.get('phone')
    code = request.json.get('code')
    
    # 验证验证码
    if verify_code(phone, code):
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone)
            db.session.add(user)
            db.session.commit()
        
        token = create_access_token(identity=user.id)
        return jsonify({'token': token})
    
    return jsonify({'error': '验证码错误'}), 401

# 上传报告接口
@app.route('/api/admin/upload_report', methods=['POST'])
@jwt_required()
@SecurityMiddleware.check_token_blacklist()
def upload_report():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
        
    file = request.files['file']
    phone = request.form.get('phone')
    
    # 验证手机号
    if not validate_phone(phone):
        return jsonify({'error': '无效的手机号'}), 400
    
    # 检查文件安全性
    is_safe, message = check_file_security(file)
    if not is_safe:
        return jsonify({'error': message}), 400
    
    if file and allowed_file(file.filename):
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        report = Report(filename=filename, user_id=user.id)
        db.session.add(report)
        db.session.commit()
        
        return jsonify({'message': '上传成功'})

# 获取报告列表接口
@app.route('/api/reports', methods=['GET'])
@jwt_required()
def get_reports():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
        
    reports = Report.query.filter_by(user_id=current_user_id).order_by(Report.upload_time.desc()).all()
    
    return jsonify({
        'reports': [{
            'id': report.id,
            'filename': report.filename,
            'upload_time': report.upload_time.isoformat()
        } for report in reports]
    })

# 下载报告接口
@app.route('/api/reports/<int:report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    current_user_id = get_jwt_identity()
    report = Report.query.get_or_404(report_id)
    
    if report.user_id != current_user_id:
        return jsonify({'error': '无权访问'}), 403
        
    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            report.filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': '文件不存在'}), 404

# PDF预览接口
@app.route('/api/reports/<int:report_id>/preview', methods=['GET'])
@jwt_required()
def preview_report(report_id):
    current_user_id = get_jwt_identity()
    report = Report.query.get_or_404(report_id)
    
    if report.user_id != current_user_id:
        return jsonify({'error': '无权访问'}), 403
    
    try:
        # 生成临时预览链接
        timestamp = datetime.utcnow().timestamp()
        token = hashlib.sha256(f"{report_id}:{timestamp}:{app.config['JWT_SECRET_KEY']}".encode()).hexdigest()
        
        preview_url = f"{app.config['PDF_VIEWER_URL']}?file={app.config['API_BASE_URL']}/api/reports/view/{report_id}/{token}"
        
        return jsonify({
            'previewUrl': preview_url
        })
        
    except Exception as e:
        return jsonify({'error': '生成预览链接失败'}), 500

# PDF文件访问接口（供预览使用）
@app.route('/api/reports/view/<int:report_id>/<token>', methods=['GET'])
def view_report(report_id, token):
    # 验证token
    timestamp = datetime.utcnow().timestamp()
    expected_token = hashlib.sha256(f"{report_id}:{timestamp}:{app.config['JWT_SECRET_KEY']}".encode()).hexdigest()
    
    if token != expected_token:
        return jsonify({'error': '无效的访问链接'}), 403
    
    try:
        report = Report.query.get_or_404(report_id)
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            report.filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': '文件不存在'}), 404

# 注册管理员蓝图
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# 管理后台首页
@app.route('/admin')
def admin_index():
    return render_template('admin/index.html')

if __name__ == '__main__':
    app.run(debug=True) 