#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能穿搭推荐平台启动脚本
提供便捷的启动方式和环境检查
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"当前版本：Python {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本检查通过：{version.major}.{version.minor}.{version.micro}")
    return True

def check_pip_version():
    """检查并升级pip版本"""
    print("检查pip版本...")
    try:
        # 检查pip版本
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ 当前pip版本：{result.stdout.strip()}")
            
            # 询问是否升级pip
            choice = input("是否升级pip到最新版本？(y/n，推荐选择y): ").lower()
            if choice == 'y' or choice == 'yes':
                print("正在升级pip...")
                upgrade_result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                                              capture_output=True, text=True, timeout=60)
                if upgrade_result.returncode == 0:
                    print("✅ pip升级成功")
                else:
                    print("⚠️ pip升级失败，但不影响使用")
            else:
                print("⚠️ 跳过pip升级")
        else:
            print("⚠️ 无法检查pip版本，继续...")
            
    except Exception as e:
        print(f"⚠️ pip检查时出错：{e}，继续...")

def check_dependencies():
    """检查依赖包是否已安装"""
    print("检查依赖包...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'werkzeug',
        'pillow',
        'opencv-python',
        'scikit-learn',
        'numpy',
        'tensorflow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """安装缺失的依赖包"""
    if not missing_packages:
        return True
    
    print(f"\n需要安装 {len(missing_packages)} 个依赖包...")
    print("正在安装依赖包，请稍候...")
    
    try:
        # 使用pip安装依赖
        cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
        if platform.system() == 'Windows':
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖包安装成功")
            return True
        else:
            print("❌ 依赖包安装失败")
            print("错误信息：", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 安装依赖包时出错：{e}")
        return False

def check_database():
    """检查数据库是否已初始化 (使用 pathlib)"""
    # 使用 instance 目录下的默认数据库，若未创建则提示初始化
    base_dir = Path(__file__).resolve().parent
    instance_dir = base_dir / 'instance'
    db_path = instance_dir / 'wardrobe.db'
    if db_path.exists():
        print(f"✅ 数据库文件存在: {db_path}")
        return True
    else:
        print(f"❌ 数据库文件不存在: {db_path}，需要初始化")
        return False

def initialize_database():
    """初始化数据库 (使用 pathlib 调用脚本)"""
    print("正在初始化数据库...")
    try:
        base_dir = Path(__file__).resolve().parent
        script_path = base_dir / 'init_db.py'
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 数据库初始化成功")
            return True
        else:
            print("❌ 数据库初始化失败")
            print("错误信息：", result.stderr)
            return False
    except Exception as e:
        print(f"❌ 数据库初始化时出错：{e}")
        return False

def start_application():
    """启动应用 (使用 pathlib 获取 app.py)"""
    print("\n" + "=" * 50)
    print("🚀 启动智能穿搭推荐平台...")
    print("=" * 50)
    try:
        base_dir = Path(__file__).resolve().parent
        app_script = base_dir / 'main.py'
        subprocess.run([sys.executable, str(app_script)])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动应用时出错：{e}")

def main():
    """主函数"""
    print("🎯 智能穿搭推荐平台 - 启动检查")
    print("="*50)
    
    # 1. 检查Python版本
    if not check_python_version():
        return
    
    # 2. 检查pip版本
    check_pip_version()
    
    # 3. 检查依赖包
    missing_packages = check_dependencies()
    
    # 4. 安装缺失的依赖包
    if missing_packages:
        choice = input(f"\n是否自动安装缺失的依赖包？(y/n): ").lower()
        if choice == 'y' or choice == 'yes':
            if not install_dependencies(missing_packages):
                print("请手动安装依赖包：pip install -r requirements.txt")
                return
        else:
            print("请手动安装依赖包：pip install -r requirements.txt")
            return
    
    # 5. 检查数据库
    if not check_database():
        choice = input("\n是否初始化数据库？(y/n): ").lower()
        if choice == 'y' or choice == 'yes':
            if not initialize_database():
                return
        else:
            print("请手动初始化数据库：python init_db.py")
            return
    
    # 6. 启动应用
    print("\n✅ 所有检查通过！")
    start_application()

if __name__ == '__main__':
    main()