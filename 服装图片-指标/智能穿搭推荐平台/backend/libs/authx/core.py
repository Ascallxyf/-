"""AuthX 核心实现 (待补充)

职责：封装用户注册 / 登录 / 当前用户获取 / 鉴权装饰器。

对外契约：
    register_user(username: str, email: str, password: str) -> dict {id, username, email}
    authenticate(username_or_email: str, password: str) -> dict {id, username, email}
    get_current_user() -> dict | None
    require_auth(fn) -> wrapped view function

输入输出说明：
    - 所有返回 dict 为“公开用户信息”不可含敏感哈希。
    - 登录/注册失败统一抛出 PermissionError / ValueError，由蓝图转换为标准响应。

错误模式：
    ValueError       参数校验失败
    PermissionError  鉴权失败（账号不存在/密码错误/未登录访问受限端点）
    RuntimeError     系统级错误（数据库连接等）

实现 TODO：
    1. 集成数据库模型(User)与密码哈希（Werkzeug generate_password_hash / check_password_hash）
    2. 使用 Flask-Login 的 login_user / logout_user / current_user
    3. require_auth 装饰器：未登录抛 PermissionError 或返回统一错误结构
    4. 统一异常到 apix.error()（在实际蓝图代码中处理）
    5. 可选：扩展 JWT 支持（生成与验证函数），降低对会话的耦合

性能与安全注意：
    - 密码哈希配置合适的 method 与 salt
    - 防止用户枚举：登录失败信息模糊化（“用户名或密码错误”）
"""
from __future__ import annotations
from typing import Optional, Callable, Any, Dict
from functools import wraps

# NOTE: Implementation to be completed by Auth Owner.

def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user and return public fields.
    Should hash password (e.g., Werkzeug or bcrypt) and persist via SQLAlchemy.
    """
    raise NotImplementedError


def authenticate(username_or_email: str, password: str) -> Dict[str, Any]:
    """Verify credentials and log user in via Flask-Login's login_user.
    Returns public user dict on success; raise PermissionError otherwise.
    """
    raise NotImplementedError


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return current user info if logged in; otherwise None."""
    raise NotImplementedError


def require_auth(fn: Callable) -> Callable:
    """Decorator to enforce authentication for API endpoints."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # if not current_user.is_authenticated: raise PermissionError("login required")
        raise NotImplementedError
    return wrapper
