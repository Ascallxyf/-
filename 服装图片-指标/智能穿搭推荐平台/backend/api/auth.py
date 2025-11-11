"""
认证相关 API
"""
from flask import request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from backend.api import auth_bp
from backend.models import db, User

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': '缺少必填字段'}), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            login_user(user)
            return jsonify({
                'message': '登录成功',
                'user': user.to_dict()
            }), 200
        
        return jsonify({'error': '用户名或密码错误'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'message': '登出成功'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前登录用户信息"""
    return jsonify(current_user.to_dict()), 200
