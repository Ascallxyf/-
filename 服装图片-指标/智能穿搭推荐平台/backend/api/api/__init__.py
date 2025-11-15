"""
API 蓝图模块
将原 app.py 中的路由分离到各个蓝图
"""
from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
wardrobe_bp = Blueprint('wardrobe', __name__)
recommendation_bp = Blueprint('recommendation', __name__)
user_bp = Blueprint('user', __name__)

# 导入路由处理函数
from . import auth, wardrobe, recommendation, user

__all__ = ['auth_bp', 'wardrobe_bp', 'recommendation_bp', 'user_bp']
