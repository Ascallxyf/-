"""ApiX 响应工具

特点：
    - 统一 success/error 响应结构，自动附带 meta(语言、trace_id、时间戳)。
    - 轻量国际化消息字典，支持运行时注册自定义 key。
    - 异常转换：ValueError/PermissionError/ApiXError 等自动映射状态码与提示。
    - Debug 信息：在 Debug 环境或携带 `X-Debug-Mode: apix` 时附带错误上下文。
"""
from __future__ import annotations

from datetime import datetime
import os
import traceback
import uuid
from typing import Any, Dict, Optional, Union, List, MutableMapping

from flask import request, has_request_context, g


# ---------------- 国际化消息 ---------------- #


_DEFAULT_MESSAGES = {
    'zh': {
        'ok': '操作成功',
        'error': '操作失败',
        'validation_error': '数据验证失败',
        'not_found': '资源不存在',
        'unauthorized': '未授权访问',
        'forbidden': '无访问权限',
        'server_error': '服务器内部错误',
        'throttled': '请求过于频繁，请稍后再试',
    },
    'en': {
        'ok': 'Success',
        'error': 'Error',
        'validation_error': 'Validation failed',
        'not_found': 'Resource not found',
        'unauthorized': 'Unauthorized',
        'forbidden': 'Forbidden',
        'server_error': 'Server error',
        'throttled': 'Too many requests, please retry later',
    }
}


class MessageCatalog:
    def __init__(self, defaults: Optional[Dict[str, Dict[str, str]]] = None, fallback: str = 'zh'):
        self._messages: Dict[str, Dict[str, str]] = {}
        self.fallback = fallback
        defaults = defaults or {}
        for lang, mapping in defaults.items():
            self.register(lang, mapping)

    def register(self, lang: str, mapping: Dict[str, str]):
        bucket = self._messages.setdefault(lang.lower(), {})
        bucket.update(mapping)

    def resolve(self, key: str, lang: Optional[str]) -> str:
        lang = (lang or self.fallback).lower()
        candidates = self._expand_candidates(lang)
        for candidate in candidates:
            bucket = self._messages.get(candidate)
            if bucket and key in bucket:
                return bucket[key]
        return self._messages.get(self.fallback, {}).get(key, key)

    @staticmethod
    def _expand_candidates(lang: str) -> List[str]:
        parts = lang.split('-')
        return ['-'.join(parts[:i]) for i in range(len(parts), 0, -1)]


catalog = MessageCatalog(_DEFAULT_MESSAGES)


def register_messages(lang: str, mapping: Dict[str, str]):
    catalog.register(lang, mapping)


def get_language() -> str:
    if has_request_context():
        header = request.headers.get('Accept-Language', catalog.fallback)
        return header.split(',')[0].split('-')[0].lower()
    return catalog.fallback


def get_message(key: str, lang: Optional[str] = None) -> str:
    return catalog.resolve(key, lang or get_language())


# ---------------- 元数据与调试 ---------------- #


def generate_trace_id() -> str:
    return uuid.uuid4().hex


def _trace_id() -> str:
    if has_request_context():
        if hasattr(g, '_apix_trace_id'):
            return g._apix_trace_id
        header_tid = request.headers.get('X-Request-ID') or request.headers.get('X-Correlation-ID')
        g._apix_trace_id = header_tid or generate_trace_id()
        return g._apix_trace_id
    return generate_trace_id()


def _should_debug() -> bool:
    env_flag = os.getenv('APIX_DEBUG', '').lower() in {'1', 'true', 'yes'}
    if env_flag:
        return True
    if os.getenv('FLASK_ENV', 'production') != 'production':
        return True
    if has_request_context():
        return request.headers.get('X-Debug-Mode', '').lower() == 'apix'
    return False


def _debug_payload(exception: Optional[Exception] = None) -> Optional[Dict[str, Any]]:
    if not _should_debug():
        return None
    payload: Dict[str, Any] = {
        'env': os.getenv('FLASK_ENV', 'production'),
    }
    if has_request_context():
        payload['query'] = request.args.to_dict(flat=False)
        payload['path'] = request.path
    if exception:
        payload.update({
            'exception': exception.__class__.__name__,
            'message': str(exception),
            'traceback': traceback.format_exc(limit=5),
        })
    return payload


def _meta(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = {
        'lang': get_language(),
        'trace_id': _trace_id(),
        'timestamp': datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    }
    if has_request_context():
        rid = request.headers.get('X-Request-ID')
        if rid:
            meta['request_id'] = rid
    if extra:
        meta.update(extra)
    return meta


def _merge_details(details: Optional[MutableMapping[str, Any]]) -> Dict[str, Any]:
    return dict(details) if details else {}


# ---------------- 异常类型 ---------------- #


class ApiXError(Exception):
    def __init__(self, message: str, status: int = 400, *, details: Optional[Dict[str, Any]] = None, message_key: Optional[str] = None):
        super().__init__(message)
        self.status = status
        self.details = details or {}
        self.message_key = message_key


class ValidationException(ApiXError):
    def __init__(self, details: Dict[str, Any]):
        super().__init__(get_message('validation_error'), 400, details=details, message_key='validation_error')


# ---------------- 响应构造 ---------------- #


def build_response(
    *,
    status_label: str,
    code: int,
    message: str,
    data: Any = None,
    details: Optional[Dict[str, Any]] = None,
    debug_info: Optional[Dict[str, Any]] = None,
    meta_extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        'status': status_label,
        'message': message,
        'code': code,
        'meta': _meta(meta_extra),
    }
    if data is not None:
        payload['data'] = data
    if details:
        payload['details'] = details
    if debug_info:
        payload['debug'] = debug_info
    return payload


def success(
    data: Any = None,
    message: Optional[str] = None,
    status: int = 200,
    meta_extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return build_response(
        status_label='success',
        code=status,
        message=message or get_message('ok'),
        data=data,
        meta_extra=meta_extra,
    )


def error(
    message: Union[str, Exception],
    status: int = 400,
    details: Optional[Dict[str, Any]] = None,
    meta_extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    debug_info: Optional[Dict[str, Any]] = None
    resolved_details = _merge_details(details)

    if isinstance(message, ApiXError):
        status = message.status
        resolved_details.update(message.details)
        text = message.message if message.message else get_message(message.message_key or 'error')
    elif isinstance(message, Exception):
        exception = message
        if isinstance(exception, ValueError):
            status = 400
            text = get_message('validation_error')
        elif isinstance(exception, PermissionError):
            status = 403
            text = get_message('forbidden')
        else:
            status = 500
            text = get_message('server_error')
        resolved_details.setdefault('error_type', exception.__class__.__name__)
        debug_info = _debug_payload(exception)
    else:
        text = message or get_message('error')

    return build_response(
        status_label='error',
        code=status,
        message=text,
        details=resolved_details or None,
        debug_info=debug_info,
        meta_extra=meta_extra,
    )


def validation_error(errors: Dict[str, List[str]]) -> Dict[str, Any]:
    return error(ValidationException({'validation_errors': errors}))


def not_found(resource: str = 'resource') -> Dict[str, Any]:
    return error(get_message('not_found'), status=404, details={'resource': resource})


def unauthorized(details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return error(get_message('unauthorized'), status=401, details=details)


def forbidden(details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return error(get_message('forbidden'), status=403, details=details)


def server_error(details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return error(get_message('server_error'), status=500, details=details)


def throttled(retry_after: Optional[int] = None) -> Dict[str, Any]:
    details = {'retry_after': retry_after} if retry_after is not None else None
    return error(get_message('throttled'), status=429, details=details)
