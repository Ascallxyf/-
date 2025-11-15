# ApiX 模块入口
# 作用：统一的请求/响应契约封装，避免各蓝图重复验证与返回结构拼装。
# 对外API：schemas 中的各 Schema 与 validate_*，responses 中的 success / error 等。
from .schemas import (
    WardrobeItemSchema,
    ProfileSchema,
    RecommendationContextSchema,
    ValidationResult,
    ValidationError,
    validate_wardrobe_item,
    validate_profile,
    validate_recommendation_context
)
from .responses import (
    success,
    error,
    validation_error,
    not_found,
    unauthorized,
    server_error,
    forbidden,
    throttled,
    get_message,
    get_language,
    register_messages,
    generate_trace_id,
    build_response,
    ApiXError,
    ValidationException,
)
from .error_handlers import (
    register_error_handlers,
    create_error_response_from_exception
)

__all__ = [
    # Schemas
    'WardrobeItemSchema',
    'ProfileSchema',
    'RecommendationContextSchema',
    'ValidationResult',
    'ValidationError',

    # Validators
    'validate_wardrobe_item',
    'validate_profile',
    'validate_recommendation_context',

    # Responses
    'success',
    'error',
    'validation_error',
    'not_found',
    'unauthorized',
    'server_error',
    'forbidden',
    'throttled',

    # Utilities
    'get_message',
    'get_language',
    'register_messages',
    'generate_trace_id',
    'build_response',

    # Exceptions
    'ApiXError',
    'ValidationException',

    # Error Handlers
    'register_error_handlers',
    'create_error_response_from_exception'
]
