"""
智能穿搭推荐平台 - 主入口文件
Main entry point for Smart Fashion Recommendation Platform

重构后的前后端分离架构
- frontend/: 前端模板和静态文件
- backend/: 后端 API 和业务逻辑
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径（使用 pathlib 计算）
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.config.config import config

# 从环境变量获取配置类型，默认为 development
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config[config_name])

if __name__ == '__main__':
    # 开发服务器配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════════════╗
    ║   智能穿搭推荐平台 - Fashion Recommendation   ║
    ╠═══════════════════════════════════════════════╣
    ║  配置环境: {config_name:30} ║
    ║  运行地址: http://{host}:{port}            ║
    ║  调试模式: {'开启' if debug else '关闭':30} ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
