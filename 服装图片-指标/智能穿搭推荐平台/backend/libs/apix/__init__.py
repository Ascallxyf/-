# ApiX 模块入口
# 作用：统一的请求/响应契约封装，避免各蓝图重复验证与返回结构拼装。
# 对外API：schemas 中的各 Schema 与 validate_*，responses 中的 success / error。
# TODO（实现者）：
# - 后续可替换为 pydantic/marshmallow 提升校验与类型提示
# - 增加更细颗粒的错误码与国际化（i18n）支持
from .schemas import WardrobeItemSchema, ProfileSchema, RecommendationContextSchema
from .responses import success, error
