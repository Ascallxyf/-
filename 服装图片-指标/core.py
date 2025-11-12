"""Recommendation engine core.
Contracts:
- recommend_outfit(user_id: int, context: dict) -> dict {items: [...], rationale: str}
- save_history(user_id: int, recommendation: dict) -> dict
- load_history(user_id: int, limit: int = 20) -> list[dict]
"""
from __future__ import annotations
from typing import Dict, Any, List
import json
from datetime import datetime

def recommend_outfit(user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """生成穿搭推荐
    
    Args:
        user_id: 用户ID
        context: 推荐上下文，包含:
            - occasion: 场合 (工作/约会/聚会/运动/日常)
            - weather: 天气 (晴天/雨天/雪天等)
            - season: 季节 (春季/夏季/秋季/冬季)
            - limit: 返回推荐数量 (默认5)
    
    Returns:
        推荐结果字典:
            - items: 推荐的衣物组合列表
            - rationale: 推荐理由
            - confidence: 置信度
            - style_analysis: 风格分析
            - context: 推荐时的上下文
    """
    try:
        # 导入依赖（延迟导入避免循环依赖）
        from backend.models.database import db, User, ClothingItem, UserProfile
        from backend.services.recommendation_engine import RecommendationEngine
        
        # 获取用户数据
        user = User.query.get(user_id)
        if not user:
            return {
                'error': '用户不存在',
                'items': [],
                'rationale': '',
                'confidence': 0.0
            }
        
        # 获取用户衣橱
        clothing_items = ClothingItem.query.filter_by(user_id=user_id).all()
        if not clothing_items:
            return {
                'error': '衣橱为空，请先添加衣物',
                'items': [],
                'rationale': '无法生成推荐：衣橱中没有衣物',
                'confidence': 0.0
            }
        
        # 获取用户档案
        user_profile = user.profile
        
        # 解析上下文参数
        occasion = context.get('occasion', '日常')
        weather = context.get('weather', '晴天')
        season = context.get('season', '春季')
        limit = context.get('limit', 5)
        
        # 调用推荐引擎
        engine = RecommendationEngine()
        recommendations = engine.recommend_outfit(
            clothing_items=clothing_items,
            user_profile=user_profile,
            occasion=occasion,
            weather=weather,
            season=season
        )
        
        # 限制返回数量
        recommendations = recommendations[:limit]
        
        # 格式化输出
        if recommendations:
            result = {
                'items': recommendations,
                'rationale': recommendations[0].get('reasoning', '') if recommendations else '',
                'confidence': recommendations[0].get('confidence', 0.0) if recommendations else 0.0,
                'style_analysis': recommendations[0].get('style_analysis', {}) if recommendations else {},
                'context': {
                    'occasion': occasion,
                    'weather': weather,
                    'season': season,
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        else:
            result = {
                'items': [],
                'rationale': '未找到合适的推荐',
                'confidence': 0.0,
                'style_analysis': {},
                'context': {
                    'occasion': occasion,
                    'weather': weather,
                    'season': season,
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        
        return result
        
    except Exception as e:
        return {
            'error': f'推荐生成失败: {str(e)}',
            'items': [],
            'rationale': '',
            'confidence': 0.0
        }


def save_history(user_id: int, recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """保存推荐历史记录
    
    Args:
        user_id: 用户ID
        recommendation: 推荐结果数据，包含:
            - items: 推荐的衣物组合
            - context: 推荐上下文
            - rationale: 推荐理由
            - confidence: 置信度
    
    Returns:
        保存结果字典:
            - history_id: 历史记录ID
            - status: 保存状态 (success/failure)
            - saved_at: 保存时间戳
    """
    try:
        # 导入依赖
        from backend.models.database import db, Recommendation
        
        # 提取推荐数据
        items = recommendation.get('items', [])
        context = recommendation.get('context', {})
        rationale = recommendation.get('rationale', '')
        confidence = recommendation.get('confidence', 0.0)
        
        # 提取第一个推荐组合的服装ID列表
        outfit_items = []
        if items and len(items) > 0:
            first_recommendation = items[0]
            if 'items' in first_recommendation:
                outfit_items = [item.get('id') for item in first_recommendation['items'] if 'id' in item]
        
        # 创建推荐记录
        rec = Recommendation(
            user_id=user_id,
            recommendation_type='outfit',
            outfit_items=json.dumps(outfit_items),
            occasion=context.get('occasion', '日常'),
            weather=context.get('weather', '晴天'),
            season=context.get('season', '春季'),
            confidence=confidence,
            reasoning=rationale,
            created_at=datetime.utcnow()
        )
        
        # 保存到数据库
        db.session.add(rec)
        db.session.commit()
        
        return {
            'history_id': rec.id,
            'status': 'success',
            'saved_at': rec.created_at.isoformat(),
            'message': '推荐历史已保存'
        }
        
    except Exception as e:
        # 回滚事务
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
        limit: 返回的历史记录数量（默认20条）
    
    Returns:
        历史记录列表，每条记录包含:
            - recommendation_id: 推荐记录ID
            - items: 推荐的衣物组合ID列表
            - context: 推荐上下文
            - rationale: 推荐理由
            - confidence: 置信度
            - created_at: 创建时间
            - user_feedback: 用户反馈
    """
    try:
        # 导入依赖
        from backend.models.database import Recommendation
        
        # 查询推荐历史
        recommendations = Recommendation.query.filter_by(
            user_id=user_id
        ).order_by(
            Recommendation.created_at.desc()
        ).limit(limit).all()
        
        # 格式化输出
        history_list = []
        for rec in recommendations:
            history_list.append({
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
            })
        
        return history_list
        
    except Exception as e:
        # 返回空列表并记录错误
        return []
