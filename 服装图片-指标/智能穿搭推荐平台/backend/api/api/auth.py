"""认证相关 API"""
from flask import request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from backend.api import auth_bp
from backend.api.utils import respond
from backend.libs.apix import success, error
from backend.models import db, User

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json() or {}
        
        # 验证必填字段
        required = {'username', 'email', 'password'}
        if not required.issubset(data):
            return respond(error('缺少必填字段', status=400))
        
        # 检查用户是否已存在
        if User.query.filter_by(username=data['username']).first():
            return respond(error('用户名已存在', status=400))
        
        if User.query.filter_by(email=data['email']).first():
            return respond(error('邮箱已被注册', status=400))
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        payload = success({'user': user.to_dict()}, message='注册成功', status=201)
        return respond(payload)
        
    except Exception as e:
        db.session.rollback()
        return respond(error(e))

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json() or {}
        
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            login_user(user)
            return respond(success({'user': user.to_dict()}, message='登录成功'))

        return respond(error('用户名或密码错误', status=401))
        
    except Exception as e:
        return respond(error(e))

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return respond(success(message='登出成功'))

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前登录用户信息"""
    return respond(success(current_user.to_dict(), message='获取成功'))
