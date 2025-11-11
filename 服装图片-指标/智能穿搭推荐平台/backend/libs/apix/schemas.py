"""Lightweight validation and (de)serialization schemas.
Avoids external deps; replace with pydantic/marshmallow later if desired.
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
