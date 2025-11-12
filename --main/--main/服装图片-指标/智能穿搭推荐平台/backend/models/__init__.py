"""数据库模型模块"""
from .database import (
    db, User, UserProfile, ClothingItem, 
    Outfit, OutfitItem, Recommendation
)

__all__ = [
    'db', 'User', 'UserProfile', 'ClothingItem', 
    'Outfit', 'OutfitItem', 'Recommendation'
]
