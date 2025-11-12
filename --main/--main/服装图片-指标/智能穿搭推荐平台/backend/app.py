"""
Flask 应用主入口 - 后端 API 服务
重构后的前后端分离架构
"""
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

# 导入后端模块
from backend.models.database import db, User, ClothingItem, Outfit, UserProfile, Recommendation
from backend.services.recommendation_engine import RecommendationEngine
from backend.services.style_analyzer import StyleAnalyzer
from backend.services.user_profiler import UserProfiler
from backend.config.config import Config

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__,
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 初始化服务
    app.recommendation_engine = RecommendationEngine()
    app.style_analyzer = StyleAnalyzer()
    app.user_profiler = UserProfiler()
    
    # 注册蓝图
    from backend.api import auth_bp, wardrobe_bp, recommendation_bp, user_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wardrobe_bp, url_prefix='/api/wardrobe')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommend')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # 前端路由
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """仪表板"""
        return render_template('dashboard.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
