"""ApiX Schemas 与验证工具

特点：
    - ValidationResult 支持错误与警告并可抛出 ValidationException。
    - 复用 `_require_field` / `_validate_enum` / `_validate_list` 辅助函数，避免重复代码。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Iterable, Callable

from .responses import ValidationException, get_message


@dataclass
class ValidationError:
    """验证错误详情"""
    field: str
    code: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {
            'field': self.field,
            'code': self.code,
            'message': self.message
        }


@dataclass
class WardrobeItemSchema:
    name: str
    category: str
    color: Optional[str] = None
    season: Optional[str] = None
    image_url: Optional[str] = None

    # 枚举值定义
    VALID_CATEGORIES = {'上装', '下装', '外套', '鞋子', '配饰', '连衣裙'}
    VALID_SEASONS = {'春季', '夏季', '秋季', '冬季', '通用'}
    VALID_COLORS = {'红色', '橙色', '黄色', '绿色', '蓝色', '紫色', '粉色', '白色', '黑色', '灰色', '棕色'}


@dataclass
class ProfileSchema:
    age: Optional[int] = None
    gender: Optional[str] = None
    styles: List[str] = field(default_factory=list)
    occasions: List[str] = field(default_factory=list)
    colors_preferred: List[str] = field(default_factory=list)

    # 枚举值定义
    VALID_GENDERS = {'男', '女', '其他'}


@dataclass
class RecommendationContextSchema:
    occasion: Optional[str] = None
    weather: Optional[str] = None
    location: Optional[str] = None


class ValidationResult:
    """验证结果封装"""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.data: Optional[Any] = None

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, code: str, message: str):
        self.errors.append(ValidationError(field, code, message))

    def add_warning(self, field: str, code: str, message: str):
        self.warnings.append(ValidationError(field, code, message))

    def raise_for_errors(self) -> 'ValidationResult':
        if not self.is_valid():
            raise ValidationException({
                'validation_errors': [e.to_dict() for e in self.errors],
                'warnings': [w.to_dict() for w in self.warnings],
            })
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            'valid': self.is_valid(),
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'data': self.data
        }


def _require_field(
    result: ValidationResult,
    data: Dict[str, Any],
    field: str,
    *,
    allow_blank: bool = False,
    max_length: Optional[int] = None,
):
    value = data.get(field)
    if value is None:
        result.add_error(field, 'required', f'{field} {get_message("validation_error")}')
        return None
    if isinstance(value, str):
        if not allow_blank and not value.strip():
            result.add_error(field, 'required', f'{field} 不能为空')
            return None
        if max_length and len(value) > max_length:
            result.add_error(field, 'too_long', f'{field} 不能超过 {max_length} 个字符')
    return value


def _validate_enum(result: ValidationResult, field: str, value: Optional[str], enum: Iterable[str]):
    if value is None:
        return
    if value not in enum:
        readable = ', '.join(sorted(enum))
        result.add_error(field, 'invalid_choice', f'{field} 必须是: {readable}')


def _validate_list(
    result: ValidationResult,
    data: Dict[str, Any],
    field: str,
    *,
    max_items: int = 20,
    validator: Optional[Callable[[str], bool]] = None,
):
    value = data.get(field)
    if value is None:
        data[field] = []
        return
    if not isinstance(value, list):
        result.add_error(field, 'invalid_type', f'{field} 必须是数组')
        return
    if len(value) > max_items:
        result.add_warning(field, 'too_many', f'{field} 最多 {max_items} 条，已截断')
        del value[max_items:]
    cleaned: List[str] = []
    for item in value:
        if not isinstance(item, str):
            result.add_error(field, 'invalid_type', f'{field} 只能包含字符串')
            continue
        text = item.strip()
        if not text:
            continue
        if validator and not validator(text):
            result.add_error(field, 'invalid_value', f'{field} 包含无效值: {text}')
            continue
        cleaned.append(text)
    data[field] = cleaned


def validate_wardrobe_item(data: Dict[str, Any]) -> ValidationResult:
    """验证衣橱物品数据"""
    result = ValidationResult()

    name = _require_field(result, data, 'name', max_length=50)
    if name:
        data['name'] = name.strip()

    category = _require_field(result, data, 'category')
    _validate_enum(result, 'category', category, WardrobeItemSchema.VALID_CATEGORIES)

    _validate_enum(result, 'color', data.get('color'), WardrobeItemSchema.VALID_COLORS)
    _validate_enum(result, 'season', data.get('season'), WardrobeItemSchema.VALID_SEASONS)

    # 如果验证通过，创建 Schema 对象
    if result.is_valid():
        result.data = WardrobeItemSchema(**data)

    return result


def validate_profile(data: Dict[str, Any]) -> ValidationResult:
    """验证用户画像数据"""
    result = ValidationResult()

    # 可选字段验证
    if 'age' in data and data['age'] is not None:
        if not isinstance(data['age'], int) or data['age'] < 1 or data['age'] > 120:
            result.add_error('age', 'invalid_range', '年龄必须是1-120之间的整数')

    if 'gender' in data and data['gender']:
        _validate_enum(result, 'gender', data['gender'], ProfileSchema.VALID_GENDERS)

    _validate_list(result, data, 'styles')
    _validate_list(result, data, 'occasions')
    _validate_list(result, data, 'colors_preferred', validator=lambda c: c in WardrobeItemSchema.VALID_COLORS)

    # 如果验证通过，创建 Schema 对象
    if result.is_valid():
        result.data = ProfileSchema(**data)

    return result


def validate_recommendation_context(data: Dict[str, Any]) -> ValidationResult:
    """验证推荐上下文数据"""
    result = ValidationResult()

    for field_name in ['occasion', 'weather', 'location']:
        value = data.get(field_name)
        if value and len(value) > 50:
            result.add_warning(field_name, 'too_long', f'{field_name} 超过 50 字符，已截断')
            data[field_name] = value[:50]

    if result.is_valid():
        result.data = RecommendationContextSchema(**data)

    return result
