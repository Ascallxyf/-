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
