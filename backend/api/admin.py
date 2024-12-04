from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
from models.admin import Admin
from models.user import User, Report
import os

admin_bp = Blueprint('admin', __name__)

# 管理员登录
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        token = create_access_token(identity={'id': admin.id, 'type': 'admin'})
        return jsonify({'token': token})
    
    return jsonify({'error': '用户名或密码错误'}), 401

# 上传报告
@admin_bp.route('/reports/upload', methods=['POST'])
@jwt_required()
def upload_report():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
        
    file = request.files['file']
    phone = request.form.get('phone')
    
    if not file or not phone:
        return jsonify({'error': '参数不完整'}), 400
        
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        report = Report(
            filename=filename,
            user_id=user.id,
            upload_time=datetime.utcnow()
        )
        db.session.add(report)
        db.session.commit()
        
        return jsonify({'message': '上传成功'})
    
    return jsonify({'error': '不支持的文件类型'}), 400

# 查询用户报告
@admin_bp.route('/reports/search', methods=['GET'])
@jwt_required()
def search_reports():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'error': '请提供手机号'}), 400
        
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
        
    reports = Report.query.filter_by(user_id=user.id).order_by(Report.upload_time.desc()).all()
    return jsonify({
        'reports': [{
            'id': report.id,
            'filename': report.filename,
            'upload_time': report.upload_time.isoformat()
        } for report in reports]
    })

# 删除报告
@admin_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    try:
        # 删除文件
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # 删除数据库记录
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除失败'}), 500

# 获取用户列表
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.phone.like(f'%{search}%'))
        
    pagination = query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [{
            'id': user.id,
            'phone': user.phone,
            'reports_count': len(user.reports),
            'last_report': user.reports[-1].upload_time.isoformat() if user.reports else None
        } for user in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

# 删除用户
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # 验证是否是超级管理员
    current_user = get_jwt_identity()
    admin = Admin.query.get(current_user['id'])
    if not admin.is_super_admin:
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        # 删除用户的所有报告文件
        for report in user.reports:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 删除用户及其所有报告记录
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除失败'}), 500

# 获取管理员列表
@admin_bp.route('/admins', methods=['GET'])
@jwt_required()
def get_admins():
    # 验证是否是超级管理员
    current_user = get_jwt_identity()
    admin = Admin.query.get(current_user['id'])
    if not admin.is_super_admin:
        return jsonify({'error': '权限不足'}), 403
    
    admins = Admin.query.all()
    return jsonify({
        'admins': [{
            'id': admin.id,
            'username': admin.username,
            'is_super_admin': admin.is_super_admin,
            'created_at': admin.created_at.isoformat(),
            'last_login': admin.last_login.isoformat() if admin.last_login else None
        } for admin in admins]
    })

# 添加管理员
@admin_bp.route('/admins', methods=['POST'])
@jwt_required()
def add_admin():
    # 验证是否是超级管理员
    current_user = get_jwt_identity()
    admin = Admin.query.get(current_user['id'])
    if not admin.is_super_admin:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    is_super_admin = data.get('is_super_admin', False)
    
    if Admin.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    new_admin = Admin(username=username, is_super_admin=is_super_admin)
    new_admin.set_password(password)
    
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({'message': '添加成功'})

# 删除管理员
@admin_bp.route('/admins/<int:admin_id>', methods=['DELETE'])
@jwt_required()
def delete_admin(admin_id):
    # 验证是否是超级管理员
    current_user = get_jwt_identity()
    admin = Admin.query.get(current_user['id'])
    if not admin.is_super_admin:
        return jsonify({'error': '权限不足'}), 403
    
    if admin_id == current_user['id']:
        return jsonify({'error': '不能删除自己'}), 400
    
    target_admin = Admin.query.get_or_404(admin_id)
    db.session.delete(target_admin)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}) 