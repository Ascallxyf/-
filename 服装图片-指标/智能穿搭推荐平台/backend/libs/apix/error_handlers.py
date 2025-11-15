"""ApiX 全局异常处理"""
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException, NotFound, Unauthorized, Forbidden, BadRequest, TooManyRequests
import logging

# 尝试导入 SQLAlchemy 异常，如果失败则跳过
try:
    from sqlalchemy.exc import SQLAlchemyError  # type: ignore
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    SQLAlchemyError = Exception

from .responses import (
    error,
    server_error,
    not_found,
    unauthorized,
    forbidden,
    throttled,
    ApiXError,
)

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask):
    """注册全局异常处理器到 Flask 应用"""

    @app.errorhandler(ApiXError)
    def handle_apix_error(e: ApiXError):
        return jsonify(error(e)), e.status

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        """处理 Werkzeug HTTP 异常"""
        if isinstance(e, NotFound):
            return jsonify(not_found()), e.code
        if isinstance(e, Unauthorized):
            return jsonify(unauthorized()), e.code
        if isinstance(e, Forbidden):
            return jsonify(forbidden()), e.code
        if isinstance(e, TooManyRequests):
            retry_after = getattr(e, 'retry_after', None)
            return jsonify(throttled(retry_after)), e.code
        if isinstance(e, BadRequest):
            return jsonify(error(getattr(e, 'description', str(e)), status=e.code)), e.code
        return jsonify(error(
            message=e.description or str(e),
            status=e.code
        )), e.code

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        """处理 SQLAlchemy 数据库异常"""
        if not HAS_SQLALCHEMY:
            return handle_generic_exception(e)

        logger.error(f"Database error: {str(e)}", exc_info=True)
        return jsonify(server_error(
            details={'error_type': 'database_error'}
        )), 500

    @app.errorhandler(ValueError)
    def handle_value_error(e: ValueError):
        """处理值错误"""
        return jsonify(error(e, 400)), 400

    @app.errorhandler(PermissionError)
    def handle_permission_error(e: PermissionError):
        return jsonify(forbidden({'reason': str(e)})), 403

    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception):
        """处理所有其他未捕获的异常"""
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        return jsonify(server_error({'exception': e.__class__.__name__})), 500


def create_error_response_from_exception(e: Exception, status: int = 500) -> dict:
    """从异常创建错误响应"""
    return error(e, status)