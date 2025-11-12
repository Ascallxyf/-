"""ApiX 统一响应封装

说明：
    - 统一成功/错误响应结构，方便前端处理与日志观测。
    - 后续可加入 trace_id、耗时等诊断信息。

约定结构：
    成功: { status: 'success', message: str, data: any, code: int }
    失败: { status: 'error', message: str, details: dict, code: int }

TODO：
    1. 增加国际化 message（根据 Accept-Language）
    2. 结合全局异常捕获，把异常统一转换为 error()
    3. 在开发态可附带调试字段（如 exception_class）
"""
from __future__ import annotations
from typing import Any, Dict, Optional


def success(data: Any = None, message: str = 'ok', status: int = 200) -> Dict[str, Any]:
    return {
        'status': 'success',
        'message': message,
        'data': data,
        'code': status,
    }


def error(message: str, status: int = 400, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        'status': 'error',
        'message': message,
        'details': details or {},
        'code': status,
    }
