"""ApiX Schemas (轻量版)

说明：
    - 提供最小的 dataclass Schema，用于与前端字段保持一致。
    - 通过 validate_* 函数做基本存在性与结构校验。
    - 后续可平滑迁移至 pydantic/marshmallow 获得更强的类型/格式验证。

当前字段与前端 main.js 使用的字段映射：
    WardrobeItemSchema: name, category, color, season, image_url
    ProfileSchema: age, gender, styles, occasions, colors_preferred
    RecommendationContextSchema: occasion, weather, location

TODO：
    1. 增加更严格的类型/长度/枚举值校验
    2. 为 validate_* 增加错误码支持（而非仅抛 ValueError）
    3. 可选：统一返回 errors 列表结构，便于前端展示多个问题
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class WardrobeItemSchema:
    name: str
    category: str
    color: Optional[str] = None
    season: Optional[str] = None
    image_url: Optional[str] = None

@dataclass
class ProfileSchema:
    age: Optional[int] = None
    gender: Optional[str] = None
    styles: List[str] = field(default_factory=list)
    occasions: List[str] = field(default_factory=list)
    colors_preferred: List[str] = field(default_factory=list)

@dataclass
class RecommendationContextSchema:
    occasion: Optional[str] = None
    weather: Optional[str] = None
    location: Optional[str] = None

# naive validators (expand as needed)

def validate_wardrobe_item(data: Dict[str, Any]) -> WardrobeItemSchema:
    if 'name' not in data or 'category' not in data:
        raise ValueError('name and category are required')
    return WardrobeItemSchema(**{k: data.get(k) for k in ['name','category','color','season','image_url']})


def validate_profile(data: Dict[str, Any]) -> ProfileSchema:
    return ProfileSchema(**{k: data.get(k) for k in ['age','gender','styles','occasions','colors_preferred']})


def validate_recommendation_context(data: Dict[str, Any]) -> RecommendationContextSchema:
    return RecommendationContextSchema(**{k: data.get(k) for k in ['occasion','weather','location']})
