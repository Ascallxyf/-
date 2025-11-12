"""
数据库初始化脚本
支持前后端分离架构
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径（使用 pathlib 计算）
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.models import db, User, UserProfile
from backend.config.config import config
from werkzeug.security import generate_password_hash

def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)
    
    # 创建应用实例
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app = create_app(config[config_name])
    
    with app.app_context():
        # 删除所有表
        print("\n[1/4] 删除旧表...")
        db.drop_all()
        print("✓ 旧表删除完成")
        
        # 创建所有表
        print("\n[2/4] 创建新表...")
        db.create_all()
        print("✓ 数据表创建完成")
        
        # 创建演示用户
        print("\n[3/4] 创建演示用户...")
        demo_user = User(
            username='demo',
            email='demo@example.com',
            password_hash=generate_password_hash('demo123')
        )
        db.session.add(demo_user)
        db.session.commit()
        print(f"✓ 演示用户创建成功 (用户名: demo, 密码: demo123)")
        
        # 创建用户画像
        print("\n[4/4] 创建用户画像...")
        demo_profile = UserProfile(
            user_id=demo_user.id,
            age=25,
            gender='女',
            height=165,
            weight=55,
            body_type='沙漏形',
            skin_tone='暖色调',
            lifestyle='都市白领',
            work_environment='办公室'
        )
        db.session.add(demo_profile)
        db.session.commit()
        print("✓ 用户画像创建成功")
        
        print("\n" + "=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        print(f"\n数据库位置: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"演示账号: demo / demo123\n")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}", file=sys.stderr)
        sys.exit(1)
