""" 
Flask 应用主入口 - 后端 API 服务
重构后的前后端分离架构
"""  # 顶部模块文档字符串：说明本文件是应用主入口
from flask import Flask, request, jsonify, render_template, session  # 导入 Flask 核心类与常用对象（request/响应渲染）
from flask_sqlalchemy import SQLAlchemy  # 导入 SQLAlchemy 拓展（这里仅用于类型提示，实际 db 在 models 中）
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # 用户登录状态管理相关类与函数
from flask_cors import CORS  # 处理跨域请求的扩展
from werkzeug.security import generate_password_hash, check_password_hash  # 密码哈希与校验工具函数
from werkzeug.utils import secure_filename  # 上传文件名安全处理函数
from pathlib import Path  # 使用 pathlib 以统一和健壮地处理路径
import os  # 操作系统相关功能（路径、环境变量等）
import json  # JSON 编解码工具（视需求用于序列化）
from datetime import datetime  # 日期时间操作（可能用于记录时间戳）

# 导入后端模块：数据库模型与服务组件
from backend.models.database import db, User, ClothingItem, Outfit, UserProfile, Recommendation  # 引入数据库实例与各数据模型
from backend.services.recommendation_engine import RecommendationEngine  # 推荐引擎服务类
from backend.services.style_analyzer import StyleAnalyzer  # 风格分析服务类
from backend.services.user_profiler import UserProfiler  # 用户画像服务类
from backend.config.config import Config  # 配置类（默认使用 Config 基类）

def create_app(config_class=Config):  # 定义应用工厂函数，支持传入不同配置类
    """应用工厂函数"""  # 工厂函数文档：返回 Flask 应用实例
    # 计算项目根目录（.../智能穿搭推荐平台）
    _BASE_DIR = Path(__file__).resolve().parent.parent
    _TEMPLATES_DIR = _BASE_DIR / 'frontend' / 'templates'
    _STATIC_DIR = _BASE_DIR / 'frontend' / 'static'

    app = Flask(
        __name__,  # 创建 Flask 应用对象，__name__ 用于定位资源
        template_folder=str(_TEMPLATES_DIR),  # 指定模板目录（前端 HTML 所在位置）
        static_folder=str(_STATIC_DIR)  # 指定静态资源目录（CSS/JS/图片）
    )
    
    app.config.from_object(config_class)  # 从传入的配置类加载配置项（数据库、密钥等）
    
    db.init_app(app)  # 初始化 SQLAlchemy，将应用与数据库绑定
    CORS(app)  # 启用跨域支持，允许前端在不同源访问 API
    
    login_manager = LoginManager()  # 创建登录管理器实例
    login_manager.init_app(app)  # 将登录管理器与当前应用绑定
    login_manager.login_view = 'login'  # 设置未登录访问受限页面时跳转的视图名称（此处未实现对应视图）
    
    @login_manager.user_loader  # 注册用户加载回调，用于通过用户 ID 获取用户对象
    def load_user(user_id):  # 定义加载用户的函数，接收字符串形式的用户 ID
        return User.query.get(int(user_id))  # 通过主键查询用户并返回（未找到时返回 None）
    
    app.recommendation_engine = RecommendationEngine()  # 实例化推荐引擎并挂载到 app 对象便于全局访问
    app.style_analyzer = StyleAnalyzer()  # 实例化风格分析器并挂载到 app
    app.user_profiler = UserProfiler()  # 实例化用户画像分析器并挂载到 app
    
    from backend.api import auth_bp, wardrobe_bp, recommendation_bp, user_bp  # 延迟导入蓝图以避免循环依赖
    app.register_blueprint(auth_bp, url_prefix='/api/auth')  # 注册认证相关蓝图，统一前缀 /api/auth
    app.register_blueprint(wardrobe_bp, url_prefix='/api/wardrobe')  # 注册衣橱相关蓝图，前缀 /api/wardrobe
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommend')  # 注册推荐相关蓝图，前缀 /api/recommend
    app.register_blueprint(user_bp, url_prefix='/api/user')  # 注册用户画像相关蓝图，前缀 /api/user
    
    @app.route('/')  # 定义根路径路由（首页）
    def index():  # 处理根路径请求的视图函数
        """主页"""  # 函数文档：返回首页模板
        return render_template('index.html')  # 渲染并返回 index.html 模板
    
    @app.route('/dashboard')  # 定义仪表板页面路由
    @login_required  # 访问该路由需要登录，未登录将被重定向到 login_view
    def dashboard():  # 仪表板视图函数
        """仪表板"""  # 函数文档：返回仪表板页面
        return render_template('dashboard.html')  # 渲染并返回 dashboard.html 模板
    
    return app  # 返回已配置好的 Flask 应用实例

if __name__ == '__main__':  # 判断当前模块是否作为主程序运行
    app = create_app()  # 调用工厂函数创建应用实例（使用默认配置）
    app.run(debug=True, host='0.0.0.0', port=5000)  # 启动开发服务器，开启调试模式，监听所有网卡的5000端口
