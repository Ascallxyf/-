"""Recommendation engine core.
Contracts:
- recommend_outfit(user_id: int, context: dict) -> dict {items: [...], rationale: str}
- save_history(user_id: int, recommendation: dict) -> dict
- load_history(user_id: int, limit: int = 20) -> list[dict]
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


def _create_error_response(error_msg: str) -> Dict[str, Any]:
    """创建标准错误响应"""
    return {
        'error': error_msg,
        'items': [],
        'rationale': '',
        'confidence': 0.0
    }


def _build_context_dict(occasion: str, weather: str, season: str, user_id: int) -> Dict[str, Any]:
    """构建上下文字典"""
    return {
        'occasion': occasion,
        'weather': weather,
        'season': season,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    }


def _extract_outfit_ids(items: List[Dict[str, Any]]) -> List[int]:
    """从推荐结果中提取服装ID列表"""
    if not items or not items[0].get('items'):
        return []
    return [item.get('id') for item in items[0]['items'] if item.get('id')]


def recommend_outfit(user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """生成穿搭推荐
    
    Args:
        user_id: 用户ID
        context: 推荐上下文 (occasion, weather, season, limit)
    
    Returns:
        推荐结果字典 (items, rationale, confidence, style_analysis, context)
    """
    try:
        from backend.models.database import User, ClothingItem
        from backend.services.recommendation_engine import RecommendationEngine
        
        # 验证用户
        user = User.query.get(user_id)
        if not user:
            return _create_error_response('用户不存在')
        
        # 验证衣橱
        clothing_items = ClothingItem.query.filter_by(user_id=user_id).all()
        if not clothing_items:
            return _create_error_response('衣橱为空，请先添加衣物')
        
        # 解析参数
        occasion = context.get('occasion', '日常')
        weather = context.get('weather', '晴天')
        season = context.get('season', '春季')
        limit = context.get('limit', 5)
        
        # 调用推荐引擎
        recommendations = RecommendationEngine().recommend_outfit(
            clothing_items=clothing_items,
            user_profile=user.profile,
            occasion=occasion,
            weather=weather,
            season=season
        )[:limit]
        
        # 构建响应
        first_rec = recommendations[0] if recommendations else {}
        return {
            'items': recommendations,
            'rationale': first_rec.get('reasoning', '未找到合适的推荐'),
            'confidence': first_rec.get('confidence', 0.0),
            'style_analysis': first_rec.get('style_analysis', {}),
            'context': _build_context_dict(occasion, weather, season, user_id)
        }
        
    except Exception as e:
        return _create_error_response(f'推荐生成失败: {str(e)}')


def save_history(user_id: int, recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """保存推荐历史记录
    
    Args:
        user_id: 用户ID
        recommendation: 推荐结果数据
    
    Returns:
        保存结果 (history_id, status, saved_at)
    """
    try:
        from backend.models.database import db, Recommendation
        
        # 提取数据
        context = recommendation.get('context', {})
        outfit_ids = _extract_outfit_ids(recommendation.get('items', []))
        
        # 创建并保存记录
        rec = Recommendation(
            user_id=user_id,
            recommendation_type='outfit',
            outfit_items=json.dumps(outfit_ids),
            occasion=context.get('occasion', '日常'),
            weather=context.get('weather', '晴天'),
            season=context.get('season', '春季'),
            confidence=recommendation.get('confidence', 0.0),
            reasoning=recommendation.get('rationale', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(rec)
        db.session.commit()
        
        return {
            'history_id': rec.id,
            'status': 'success',
            'saved_at': rec.created_at.isoformat(),
            'message': '推荐历史已保存'
        }
        
    except Exception as e:
        try:
            from backend.models.database import db
            db.session.rollback()
        except:
            pass
        
        return {
            'history_id': None,
            'status': 'failure',
            'saved_at': None,
            'error': f'保存失败: {str(e)}'
        }


def load_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """加载推荐历史记录
    
    Args:
        user_id: 用户ID
        limit: 返回数量（默认20条）
    
    Returns:
        历史记录列表
    """
    try:
        from backend.models.database import Recommendation
        
        recommendations = Recommendation.query.filter_by(
            user_id=user_id
        ).order_by(
            Recommendation.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'recommendation_id': rec.id,
                'items': json.loads(rec.outfit_items) if rec.outfit_items else [],
                'context': {
                    'occasion': rec.occasion,
                    'weather': rec.weather,
                    'season': rec.season
                },
                'rationale': rec.reasoning,
                'confidence': rec.confidence,
                'created_at': rec.created_at.isoformat() if rec.created_at else None,
                'user_feedback': rec.user_feedback,
                'feedback_reason': rec.feedback_reason,
                'recommendation_type': rec.recommendation_type
            }
            for rec in recommendations
        ]
        
    except Exception as e:
        return []


