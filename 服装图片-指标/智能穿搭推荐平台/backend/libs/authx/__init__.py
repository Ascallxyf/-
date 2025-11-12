# AuthX 模块入口
# 作用：对外暴露认证相关的高层API，供后端蓝图（backend/api/auth.py）调用。
# 包含功能：
# - 用户注册（密码加盐哈希并入库）
# - 用户登录（凭证校验 + 会话/Flask-Login 集成）
# - 当前用户信息获取
# - 端点鉴权装饰器（未登录拦截）
# 对外API：register_user, authenticate, get_current_user, require_auth
# TODO（实现者）：
# - 接入数据库模型与密码哈希库（Werkzeug/bcrypt）
# - 与 Flask-Login 的 login_user / logout_user 集成
# - 统一异常 -> 统一错误响应（可调用 apix.error）
from .core import register_user, authenticate, get_current_user, require_auth
