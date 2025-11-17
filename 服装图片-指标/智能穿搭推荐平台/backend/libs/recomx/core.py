"""RecomX 推荐引擎核心模块

职责: 穿搭推荐、推荐历史管理

对外契约:
    recommend_outfit(user_id: int, context: dict) -> dict
        {
            'items': list[dict],           # 推荐的服装组合
            'rationale': str,              # 推荐理由
            'confidence': float,           # 置信度 (0-1)
            'style_analysis': dict,        # 风格分析结果
            'context': dict,               # 推荐上下文
            'status': 'success'|'error'
        }
    
    save_history(user_id: int, recommendation: dict) -> dict
        {'history_id': int, 'status': 'success'|'failure', 'saved_at': str}
    
    load_history(user_id: int, limit: int = 20) -> list[dict]
        [{'recommendation_id': int, 'items': [...], 'context': {...}, ...}]

错误处理:
    - 用户不存在: 返回错误响应
    - 衣橱为空: 返回友好提示
    - 推荐失败: 返回 error 状态和具体错误信息
    - 数据库异常: 自动回滚事务

性能优化:
    - 延迟导入避免循环依赖
    - 批量处理推荐项
    - 异常捕获不中断整体流程
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# 辅助函数
# ============================================================================

def _create_error_response(error_msg: str, error_code: str = 'RECOMMENDATION_ERROR') -> Dict[str, Any]:
    """创建标准错误响应
    
    Args:
        error_msg: 错误消息
        error_code: 错误代码
    
    Returns:
        标准化错误响应字典
    """
    return {
        'status': 'error',
        'error': error_msg,
        'error_code': error_code,
        'items': [],
        'rationale': '',
        'confidence': 0.0,
        'style_analysis': {},
        'context': {}
    }


def _build_context_dict(
    occasion: str, 
    weather: str, 
    season: str, 
    location: Optional[str] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """构建推荐上下文字典
    
    Args:
        occasion: 场合 (e.g. '商务会议', '日常休闲', '约会')
        weather: 天气 (e.g. '晴', '雨', '雪')
        season: 季节 (e.g. '春', '夏', '秋', '冬')
        location: 地点 (可选，e.g. '室内', '室外')
        user_id: 用户ID (可选)
    
    Returns:
        上下文字典
    """
    ctx = {
        'occasion': occasion,
        'weather': weather,
        'season': season,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if location:
        ctx['location'] = location
    if user_id:
        ctx['user_id'] = user_id
    
    return ctx


def _extract_outfit_ids(items: List[Dict[str, Any]]) -> List[int]:
    """从推荐结果中提取服装ID列表
    
    Args:
        items: 推荐的服装条目列表
    
    Returns:
        服装ID列表
    """
    if not items:
        return []
    
    return [
        item.get('id') for item in items 
        if isinstance(item, dict) and item.get('id')
    ]


def _format_outfit_items(items: List[Any]) -> List[Dict[str, Any]]:
    """格式化推荐的衣服条目
    
    Args:
        items: 原始衣服条目（ORM 对象或字典）
    
    Returns:
        格式化的字典列表
    """
    formatted = []
    
    for item in items:
        if hasattr(item, 'to_dict'):
            # ORM 模型对象
            formatted.append(item.to_dict())
        elif isinstance(item, dict):
            # 已经是字典
            formatted.append(item)
        else:
            logger.warning(f'Unknown item type: {type(item)}')
    
    return formatted


# ============================================================================
# 核心 API
# ============================================================================

def recommend_outfit(user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """生成穿搭推荐
    
    核心流程:
    1. 验证用户存在性
    2. 检查衣橱是否有足够的衣服
    3. 解析推荐上下文（场合、天气、季节等）
    4. 调用推荐引擎生成推荐
    5. 格式化返回结果
    
    Args:
        user_id: 用户ID
        context: 推荐上下文字典，应包含:
            - occasion (str): 场合，默认 '日常'
            - weather (str): 天气，默认 '晴天'
            - season (str): 季节，默认 '春季'
            - location (str): 地点，可选
            - limit (int): 返回推荐数量，默认 5
    
    Returns:
        推荐结果字典，包含:
            - status: 'success' 或 'error'
            - items: 推荐的服装条目列表
            - rationale: 推荐理由字符串
            - confidence: 推荐置信度 (0.0 - 1.0)
            - style_analysis: 风格分析结果
            - context: 推荐上下文
        
        失败时返回:
            - status: 'error'
            - error: 错误消息
            - error_code: 错误代码
            - items: 空列表
            - 其他字段为空/默认值
    
    Raises:
        无直接抛异常，所有异常捕获并返回 error 状态
    
    示例:
        >>> result = recommend_outfit(
        ...     user_id=1,
        ...     context={
        ...         'occasion': '商务会议',
        ...         'weather': '晴天',
        ...         'season': '春季',
        ...         'limit': 5
        ...     }
        ... )
        >>> if result['status'] == 'success':
        ...     for item in result['items']:
        ...         print(f"推荐: {item['name']}")
    """
    try:
        # 延迟导入避免循环依赖
        from backend.models.database import User, ClothingItem
        from backend.services.recommendation_engine import RecommendationEngine
        
        # ─────────────────────────────────────────────────────────────────
        # 步骤1: 验证用户
        # ─────────────────────────────────────────────────────────────────
        user = User.query.get(user_id)
        if not user:
            logger.warning(f'User {user_id} not found')
            return _create_error_response('用户不存在', 'USER_NOT_FOUND')
        
        # ─────────────────────────────────────────────────────────────────
        # 步骤2: 检查衣橱
        # ─────────────────────────────────────────────────────────────────
        clothing_items = ClothingItem.query.filter_by(user_id=user_id).all()
        
        if not clothing_items:
            logger.info(f'User {user_id} has empty wardrobe')
            return _create_error_response(
                '衣橱为空，请先添加衣物',
                'WARDROBE_EMPTY'
            )
        
        # ─────────────────────────────────────────────────────────────────
        # 步骤3: 解析推荐参数
        # ─────────────────────────────────────────────────────────────────
        occasion = context.get('occasion', '日常')
        weather = context.get('weather', '晴天')
        season = context.get('season', '春季')
        location = context.get('location')
        limit = int(context.get('limit', 5))
        
        # ─────────────────────────────────────────────────────────────────
        # 步骤4: 调用推荐引擎
        # ─────────────────────────────────────────────────────────────────
        rec_engine = RecommendationEngine()
        
        recommendations = rec_engine.recommend_outfit(
            clothing_items=clothing_items,
            user_profile=user.profile,
            occasion=occasion,
            weather=weather,
            season=season
        )
        
        # 限制返回数量
        recommendations = recommendations[:limit]
        
        # ─────────────────────────────────────────────────────────────────
        # 步骤5: 格式化响应
        # ─────────────────────────────────────────────────────────────────
        if recommendations:
            first_rec = recommendations[0]
            rationale = first_rec.get('reasoning', '基于你的风格和场合推荐')
            confidence = first_rec.get('confidence', 0.8)
            style_analysis = first_rec.get('style_analysis', {})
        else:
            rationale = '未找到合适的推荐，请添加更多衣物'
            confidence = 0.0
            style_analysis = {}
        
        # 构建响应
        response = {
            'status': 'success',
            'items': _format_outfit_items(recommendations),
            'rationale': rationale,
            'confidence': float(confidence),
            'style_analysis': style_analysis,
            'context': _build_context_dict(occasion, weather, season, location, user_id),
            'total': len(recommendations)
        }
        
        logger.info(
            f'Recommendation generated for user {user_id}: '
            f'{len(recommendations)} items, confidence={confidence}'
        )
        
        return response
        
    except Exception as e:
        error_msg = f'推荐生成失败: {str(e)}'
        logger.exception(f'Error in recommend_outfit(user_id={user_id}): {error_msg}')
        return _create_error_response(error_msg, 'RECOMMENDATION_FAILED')


def save_history(user_id: int, recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """保存推荐历史记录
    
    核心流程:
    1. 验证输入数据
    2. 从推荐结果提取关键信息
    3. 创建 Recommendation 数据库记录
    4. 提交事务
    5. 返回保存结果
    
    Args:
        user_id: 用户ID
        recommendation: 推荐结果数据，应包含:
            - items: 推荐的服装列表
            - rationale: 推荐理由
            - confidence: 置信度
            - context: 推荐上下文 (occasion, weather, season)
    
    Returns:
        保存结果字典，包含:
            - history_id: 保存的推荐记录 ID (成功时)
            - status: 'success' 或 'failure'
            - saved_at: 保存时间戳 (成功时)
            - message: 结果信息
            - error: 错误信息 (失败时)
    
    示例:
        >>> rec_result = recommend_outfit(1, {'occasion': '约会'})
        >>> save_result = save_history(1, rec_result)
        >>> print(f"Saved with ID: {save_result['history_id']}")
    """
    try:
        # 延迟导入
        from backend.models.database import db, Recommendation
        
        # ─────────────────────────────────────────────────────────────────
        # 验证输入
        # ─────────────────────────────────────────────────────────────────
        if not recommendation or not isinstance(recommendation, dict):
            logger.warning('Invalid recommendation data provided')
            return {
                'history_id': None,
                'status': 'failure',
                'saved_at': None,
                'error': '推荐数据格式错误'
            }
        
        # ─────────────────────────────────────────────────────────────────
        # 提取数据
        # ─────────────────────────────────────────────────────────────────
        context = recommendation.get('context', {})
        items = recommendation.get('items', [])
        outfit_ids = _extract_outfit_ids(items)
        
        # ─────────────────────────────────────────────────────────────────
        # 创建记录
        # ─────────────────────────────────────────────────────────────────
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
        
        # ─────────────────────────────────────────────────────────────────
        # 提交事务
        # ─────────────────────────────────────────────────────────────────
        db.session.add(rec)
        db.session.commit()
        
        logger.info(
            f'Recommendation history saved: '
            f'user_id={user_id}, rec_id={rec.id}, items={len(outfit_ids)}'
        )
        
        return {
            'history_id': rec.id,
            'status': 'success',
            'saved_at': rec.created_at.isoformat(),
            'message': '推荐历史已保存'
        }
        
    except Exception as e:
        # 事务回滚
        try:
            from backend.models.database import db
            db.session.rollback()
        except:
            pass
        
        error_msg = f'保存失败: {str(e)}'
        logger.exception(f'Error in save_history(user_id={user_id}): {error_msg}')
        
        return {
            'history_id': None,
            'status': 'failure',
            'saved_at': None,
            'error': error_msg
        }


def load_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """加载推荐历史记录
    
    核心流程:
    1. 查询该用户的所有推荐历史
    2. 按时间倒序排列
    3. 限制返回数量
    4. 格式化输出
    
    Args:
        user_id: 用户ID
        limit: 返回数量限制，默认 20（最大 100）
    
    Returns:
        历史记录列表，每条包含:
            - recommendation_id: 记录 ID
            - items: 推荐的服装 ID 列表
            - context: 推荐上下文 (occasion, weather, season, location)
            - rationale: 推荐理由
            - confidence: 置信度
            - created_at: 创建时间戳
            - user_feedback: 用户反馈 (liked|disliked|neutral|None)
            - feedback_reason: 反馈原因
            - recommendation_type: 推荐类型
        
        异常时返回空列表 []
    
    示例:
        >>> history = load_history(user_id=1, limit=10)
        >>> for rec in history:
        ...     print(f"[{rec['created_at']}] {rec['rationale']}")
    """
    try:
        # 延迟导入
        from backend.models.database import Recommendation
        
        # ─────────────────────────────────────────────────────────────────
        # 查询历史记录
        # ─────────────────────────────────────────────────────────────────
        limit = min(int(limit), 100)  # 最多返回 100 条
        
        recommendations = Recommendation.query.filter_by(
            user_id=user_id
        ).order_by(
            Recommendation.created_at.desc()
        ).limit(limit).all()
        
        logger.info(f'Loaded {len(recommendations)} history records for user {user_id}')
        
        # ─────────────────────────────────────────────────────────────────
        # 格式化输出
        # ─────────────────────────────────────────────────────────────────
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
        error_msg = f'加载历史失败: {str(e)}'
        logger.exception(f'Error in load_history(user_id={user_id}): {error_msg}')
        return []


