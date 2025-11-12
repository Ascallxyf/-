# 智能穿搭推荐平台

基于个体特征的智能衣橱系统和多模态知识图谱的服装推荐算法。

> **版本: v2.0 - 前后端分离架构**  
> 详见 [CHANGELOG.txt](CHANGELOG.txt) 了解版本更新详情。

## 📁 项目结构

```
智能穿搭推荐平台/
├── frontend/              # 前端资源
│   ├── templates/         # HTML 模板
│   └── static/            # CSS、JS、图片、上传文件
├── backend/               # 后端代码
│   ├── api/              # REST API 蓝图
│   ├── models/           # 数据库模型
│   ├── services/         # 业务逻辑
│   └── config/           # 配置管理
├── main.py               # 主入口
├── init_db.py            # 数据库初始化
├── requirements.txt      # 依赖
├── Dockerfile            # Docker 配置
└── CHANGELOG.txt         # 更新日志
```

## 系统架构

### 核心模块
1. **用户画像模块** (`backend/services/user_profiler.py`) - 基于个体特征建模
2. **智能衣橱模块** (`backend/api/wardrobe.py`) - 服装管理和分类
3. **推荐引擎模块** (`backend/services/recommendation_engine.py`) - 多模态知识图谱推荐
4. **风格分析模块** (`backend/services/style_analyzer.py`) - 色彩、款式、风格匹配
5. **场景适配模块** - 基于场景的穿搭建议

### 前后端分离架构 (v2.0)
- **前端** (`frontend/`): HTML 模板、CSS 样式、JavaScript 交互、静态资源
- **后端** (`backend/`): Flask API 蓝图、业务服务、数据库模型、配置管理
- **API 层**: 认证、衣橱管理、推荐服务、用户画像四大模块

### 技术栈
- **后端**: Python 3.11+ / Flask / SQLAlchemy
- **前端**: HTML5 / CSS3 / JavaScript (ES6+)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **图像处理**: OpenCV / PIL
- **机器学习**: scikit-learn / TensorFlow
- **容器化**: Docker / Docker Compose

## 快速开始

### 标准启动流程

```powershell
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖（首次运行）
pip install -r requirements.txt

# 3. 初始化数据库（首次运行）
python init_db.py

# 4. 启动应用
python main.py
```

### 一键启动

```powershell
# 使用便捷启动脚本（自动检查环境并启动）
python start.py
```

启动脚本会自动：
- 检查 Python 版本
- 安装缺失的依赖包
- 初始化数据库
- 启动应用服务器

### Docker 部署

```bash
# 方式一：使用 Docker Compose
docker-compose up -d

# 方式二：使用 Dockerfile
docker build -t fashion-rec .
docker run -p 5000:5000 fashion-rec
```

### 默认登录信息
- **用户名**: demo
- **密码**: demo123

### 访问地址
- 主页: http://localhost:5000
- 仪表板: http://localhost:5000/dashboard

## 🔧 环境配置

### 环境变量（可选）

创建 `.env` 文件配置环境变量：

```bash
FLASK_CONFIG=development      # 环境: development/production/testing
FLASK_HOST=0.0.0.0           # 主机地址
FLASK_PORT=5000              # 端口号
FLASK_DEBUG=True             # 调试模式
SECRET_KEY=your-secret-key   # 密钥（生产环境务必修改）
DATABASE_URL=sqlite:///wardrobe.db  # 数据库连接
```

### Git 工作流程

```bash
# 1. 克隆仓库
git clone <仓库URL>
cd 智能穿搭推荐平台

# 2. 创建功能分支
git checkout -b feature/新功能描述

# 3. 开发完成后提交
git add .
git commit -m "feat(模块): 添加新功能描述"
git push origin feature/新功能描述

# 4. 创建 Pull Request 进行代码审查
```

## 📋 版本历史

详见 [CHANGELOG.txt](CHANGELOG.txt) 查看完整更新日志。

**当前版本**: v2.0  
**发布日期**: 2025-11-11  
**主要更新**: 前后端分离架构重构

## 功能特点

### 个体特征分析
- 身材体型识别
- 肤色分析
- 个人偏好学习
- 穿搭风格定位

### 智能推荐算法
- 基于协同过滤的推荐
- 基于内容的推荐
- 多模态特征融合
- 知识图谱推理

### 场景适配
- 工作场合
- 休闲娱乐
- 正式场合
- 季节适配

## API接口

### 用户管理
- POST /api/user/register - 用户注册
- POST /api/user/login - 用户登录
- GET /api/user/profile - 获取用户信息

### 衣橱管理
- POST /api/wardrobe/add - 添加服装
- GET /api/wardrobe/list - 获取衣橱列表
- DELETE /api/wardrobe/{id} - 删除服装

### 推荐服务
- POST /api/recommend/outfit - 获取穿搭推荐
- POST /api/recommend/purchase - 购买建议
- POST /api/recommend/style - 风格推荐