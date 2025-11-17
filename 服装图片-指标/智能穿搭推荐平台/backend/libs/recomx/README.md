"""RecomX 推荐引擎模块使用指南

本文档详细说明 RecomX 模块的功能、API、使用示例和集成方法。
"""

# ============================================================================
# 1. 模块概览
# ============================================================================

"""
RecomX 是智能穿搭推荐平台的核心推荐引擎模块。

职责:
    - 基于用户画像和衣橱信息生成穿搭推荐
    - 管理推荐历史记录
    - 提供标准化的推荐 API

核心特性:
    ✓ 多上下文推荐 (场合、天气、季节、地点等)
    ✓ 推荐历史管理和持久化
    ✓ 置信度评分
    ✓ 风格分析
    ✓ 完整的错误处理和降级方案
"""

# ============================================================================
# 2. API 文档
# ============================================================================

"""
───────────────────────────────────────────────────────────────────────────────
2.1 recommend_outfit(user_id: int, context: dict) -> dict
───────────────────────────────────────────────────────────────────────────────

功能:
    生成个性化的穿搭推荐

参数:
    user_id: 用户ID (int)
    context: 推荐上下文字典，包含:
        - occasion (str): 场合
            常见值: '日常', '商务', '约会', '运动', '聚会', '度假'
            默认: '日常'
        
        - weather (str): 天气
            常见值: '晴天', '雨天', '雪天', '阴天', '风天', '冷'
            默认: '晴天'
        
        - season (str): 季节
            常见值: '春季', '夏季', '秋季', '冬季'
            默认: '春季'
        
        - location (str): 地点 (可选)
            常见值: '室内', '室外', '办公室', '购物', '聚会'
        
        - limit (int): 返回推荐数量 (可选)
            范围: 1-20
            默认: 5

返回:
    成功时 (status='success'):
        {
            'status': 'success',
            'items': [                           # 推荐的服装列表
                {
                    'id': 1,
                    'name': '白色T恤',
                    'category': '上装',
                    'color': '白色',
                    'image_url': '/static/uploads/...',
                    ...
                },
                ...
            ],
            'rationale': '根据场合和天气推荐...',  # 推荐理由
            'confidence': 0.85,                  # 置信度 (0-1)
            'style_analysis': {                  # 风格分析
                'dominant_style': '商务正式',
                'color_harmony': '和谐',
                'season_match': '完美'
            },
            'context': {                         # 推荐上下文
                'occasion': '商务',
                'weather': '晴天',
                'season': '春季',
                'timestamp': '2025-11-16T10:30:45.123456'
            },
            'total': 3                           # 返回的总数
        }
    
    失败时 (status='error'):
        {
            'status': 'error',
            'error': '用户不存在',               # 错误信息
            'error_code': 'USER_NOT_FOUND',     # 错误代码
            'items': [],
            'rationale': '',
            'confidence': 0.0,
            'style_analysis': {},
            'context': {}
        }

异常情况和错误代码:
    - USER_NOT_FOUND: 用户不存在
    - WARDROBE_EMPTY: 用户衣橱为空
    - RECOMMENDATION_FAILED: 推荐生成失败 (算法错误)
    - RECOMMENDATION_ERROR: 其他推荐错误

示例:
    from backend.libs.recomx import recommend_outfit
    
    # 基本推荐
    result = recommend_outfit(
        user_id=1,
        context={'occasion': '商务', 'weather': '晴天'}
    )
    
    # 详细推荐
    result = recommend_outfit(
        user_id=1,
        context={
            'occasion': '约会',
            'weather': '晴天',
            'season': '春季',
            'location': '室外',
            'limit': 5
        }
    )
    
    if result['status'] == 'success':
        print(f"推荐 {len(result['items'])} 件衣物")
        print(f"理由: {result['rationale']}")
        print(f"置信度: {result['confidence']:.1%}")
    else:
        print(f"推荐失败: {result['error']}")


───────────────────────────────────────────────────────────────────────────────
2.2 save_history(user_id: int, recommendation: dict) -> dict
───────────────────────────────────────────────────────────────────────────────

功能:
    将推荐结果持久化到数据库，以便后续追踪和分析

参数:
    user_id: 用户ID (int)
    recommendation: 推荐结果字典 (recommend_outfit 的返回值)

返回:
    成功时 (status='success'):
        {
            'history_id': 42,                     # 保存的记录ID
            'status': 'success',
            'saved_at': '2025-11-16T10:30:45...',  # 保存时间戳
            'message': '推荐历史已保存'
        }
    
    失败时 (status='failure'):
        {
            'history_id': None,
            'status': 'failure',
            'saved_at': None,
            'error': '保存失败: ...'              # 错误详情
        }

异常情况:
    - 推荐数据格式错误
    - 数据库连接异常 (自动回滚)
    - 字段缺失

示例:
    from backend.libs.recomx import recommend_outfit, save_history
    
    # 生成推荐
    rec_result = recommend_outfit(1, {'occasion': '约会'})
    
    # 保存推荐
    if rec_result['status'] == 'success':
        save_result = save_history(1, rec_result)
        if save_result['status'] == 'success':
            print(f"已保存到历史记录 (ID: {save_result['history_id']})")


───────────────────────────────────────────────────────────────────────────────
2.3 load_history(user_id: int, limit: int = 20) -> list[dict]
───────────────────────────────────────────────────────────────────────────────

功能:
    加载用户的推荐历史记录

参数:
    user_id: 用户ID (int)
    limit: 返回数量限制 (int, 1-100)
        默认: 20
        最大: 100 (超过会被限制)

返回:
    历史记录列表 (按时间倒序):
        [
            {
                'recommendation_id': 42,          # 记录ID
                'items': [1, 3, 5],               # 推荐的服装ID列表
                'context': {                      # 推荐上下文
                    'occasion': '约会',
                    'weather': '晴天',
                    'season': '春季'
                },
                'rationale': '根据约会场景推荐...',  # 推荐理由
                'confidence': 0.88,               # 置信度
                'created_at': '2025-11-16T10:30:45...',  # 创建时间
                'user_feedback': 'liked',         # 用户反馈 ('liked'|'disliked'|'neutral'|None)
                'feedback_reason': '很喜欢这个搭配',   # 反馈原因
                'recommendation_type': 'outfit'   # 推荐类型
            },
            ...
        ]
    
    异常时返回空列表 []

异常情况:
    - 用户不存在 → 返回 []
    - 数据库查询失败 → 返回 []
    - 用户没有历史记录 → 返回 []

示例:
    from backend.libs.recomx import load_history
    
    # 获取最近10条历史记录
    history = load_history(user_id=1, limit=10)
    
    print(f"共 {len(history)} 条历史记录")
    
    for rec in history:
        print(f"[{rec['created_at']}] {rec['context']['occasion']}: {rec['rationale']}")
        print(f"  服装: {rec['items']}")
        if rec['user_feedback']:
            print(f"  反馈: {rec['user_feedback']} - {rec['feedback_reason']}")
"""

# ============================================================================
# 3. 使用示例
# ============================================================================

"""
───────────────────────────────────────────────────────────────────────────────
3.1 基本流程: 推荐 → 保存 → 加载
───────────────────────────────────────────────────────────────────────────────

from backend.libs.recomx import recommend_outfit, save_history, load_history

def complete_recommendation_workflow(user_id):
    '''完整的推荐工作流'''
    
    # 步骤1: 生成推荐
    print("正在生成推荐...")
    rec_result = recommend_outfit(
        user_id=user_id,
        context={
            'occasion': '约会',
            'weather': '晴天',
            'season': '春季'
        }
    )
    
    if rec_result['status'] != 'success':
        print(f"推荐失败: {rec_result['error']}")
        return
    
    # 步骤2: 保存推荐到历史
    print("正在保存历史...")
    save_result = save_history(user_id, rec_result)
    
    if save_result['status'] == 'success':
        print(f"推荐已保存 (ID: {save_result['history_id']})")
    
    # 步骤3: 加载历史记录
    print("正在加载历史...")
    history = load_history(user_id, limit=5)
    
    print(f"最近 {len(history)} 条推荐:")
    for h in history:
        print(f"  - {h['context']['occasion']}: {len(h['items'])} 件衣服")


───────────────────────────────────────────────────────────────────────────────
3.2 在 API 蓝图中集成 RecomX
───────────────────────────────────────────────────────────────────────────────

# backend/api/recommendation.py

from flask import request, jsonify, Blueprint
from flask_login import login_required, current_user
from backend.libs.recomx import recommend_outfit, save_history, load_history
from backend.libs.apix.responses import success, error

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/outfit', methods=['POST'])
@login_required
def get_recommendation():
    '''获取穿搭推荐'''
    try:
        data = request.get_json()
        
        # 调用 RecomX 推荐引擎
        result = recommend_outfit(
            user_id=current_user.id,
            context={
                'occasion': data.get('occasion', '日常'),
                'weather': data.get('weather', '晴天'),
                'season': data.get('season', '春季'),
                'limit': data.get('limit', 5)
            }
        )
        
        if result['status'] == 'success':
            # 保存到历史
            save_history(current_user.id, result)
            
            return jsonify(success(
                data={
                    'items': result['items'],
                    'rationale': result['rationale'],
                    'confidence': result['confidence']
                },
                message='推荐成功'
            )), 200
        else:
            return jsonify(error(
                message=result['error'],
                status=400
            )), 400
    
    except Exception as e:
        return jsonify(error(
            message=str(e),
            status=500
        )), 500


@recommendation_bp.route('/history', methods=['GET'])
@login_required
def get_recommendation_history():
    '''获取推荐历史'''
    try:
        limit = request.args.get('limit', 20, type=int)
        
        history = load_history(current_user.id, limit=limit)
        
        return jsonify(success(
            data={'history': history, 'total': len(history)},
            message='历史加载成功'
        )), 200
    
    except Exception as e:
        return jsonify(error(message=str(e), status=500)), 500


───────────────────────────────────────────────────────────────────────────────
3.3 在前端中调用 RecomX API
───────────────────────────────────────────────────────────────────────────────

// frontend/static/js/main.js

async function getRecommendation() {
    const occasion = document.getElementById('occasion').value;
    const weather = document.getElementById('weather').value;
    const season = document.getElementById('season').value;
    
    try {
        const response = await fetch('/api/recommend/outfit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                occasion,
                weather,
                season,
                limit: 5
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayRecommendations(data.data.items);
            console.log('推荐理由:', data.data.rationale);
        } else {
            alert('推荐失败: ' + data.message);
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}

function displayRecommendations(items) {
    const container = document.getElementById('recommendations');
    container.innerHTML = '';
    
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'recommendation-item';
        div.innerHTML = `
            <img src="${item.image_url}" alt="${item.name}">
            <h4>${item.name}</h4>
            <p>${item.category} - ${item.color}</p>
        `;
        container.appendChild(div);
    });
}
"""

# ============================================================================
# 4. 与其他模块的关系
# ============================================================================

"""
┌───────────────────────────────────────────────────────────────────────────┐
│ RecomX 依赖关系图                                                         │
└───────────────────────────────────────────────────────────────────────────┘

RecomX (recommend_outfit/save_history/load_history)
    │
    ├─→ backend.models.database
    │       - User (用户模型)
    │       - UserProfile (用户画像)
    │       - ClothingItem (衣橱单品)
    │       - Recommendation (推荐历史)
    │
    ├─→ backend.services.recommendation_engine
    │       - RecommendationEngine 类
    │       - recommend_outfit() 方法 (核心算法)
    │
    └─→ backend.api.recommendation (客户端)
            - GET /api/recommend/outfit
            - GET /api/recommend/history

主要调用方:
    - API 蓝图 (backend/api/recommendation.py)
    - 前端 JavaScript (frontend/static/js/main.js)
    - 其他模块测试和集成场景

被调用的服务:
    - RecommendationEngine (recommend_outfit 核心算法)
    - ProfileX (用户画像，在 RecommendationEngine 中使用)
    - WardrobeX (衣橱数据，在推荐前验证)
"""

# ============================================================================
# 5. 常见场景和最佳实践
# ============================================================================

"""
───────────────────────────────────────────────────────────────────────────────
场景1: 首次推荐 (冷启动)
───────────────────────────────────────────────────────────────────────────────

问题: 新用户还没有完整的画像或衣橱

解决方案:
    1. 检查衣橱是否为空
    2. 降级推荐策略:
        - 只用基础衣橱信息推荐
        - 返回通用搭配建议
        - 提示用户补充画像信息

示例代码:
    result = recommend_outfit(new_user_id, context)
    
    if result['status'] == 'error':
        if result['error_code'] == 'WARDROBE_EMPTY':
            # 推荐基础服装列表或引导用户添加衣物
            return suggest_basic_outfits()


───────────────────────────────────────────────────────────────────────────────
场景2: 精准推荐 (已有完整数据)
───────────────────────────────────────────────────────────────────────────────

条件: 用户有完整画像 + 足够衣橱 + 历史反馈

最佳实践:
    1. 利用全部上下文字段
    2. 使用用户反馈改进推荐
    3. 追踪推荐置信度

示例代码:
    result = recommend_outfit(
        user_id,
        context={
            'occasion': '商务',
            'weather': '雨天',
            'season': '秋季',
            'location': '办公室'
        }
    )
    
    if result['confidence'] > 0.8:
        save_history(user_id, result)
        # 置信度高，保存推荐


───────────────────────────────────────────────────────────────────────────────
场景3: 获取推荐理由和反馈
───────────────────────────────────────────────────────────────────────────────

使用场景: 用户想了解为什么推荐这些衣服

示例代码:
    result = recommend_outfit(user_id, context)
    
    print(result['rationale'])  # 推荐理由
    print(result['style_analysis'])  # 风格分析细节
    print(result['confidence'])  # 置信度
    
    # 用户反馈
    if user_likes_recommendation:
        save_history(user_id, result)  # 保存供算法学习


───────────────────────────────────────────────────────────────────────────────
场景4: 大量推荐请求
───────────────────────────────────────────────────────────────────────────────

问题: 高并发下性能问题

优化建议:
    1. 使用缓存 (Redis) 缓存最近的推荐
    2. 异步保存历史 (Celery 后台任务)
    3. 限流保护
    4. 推荐引擎内部优化 (见 CHANGELOG)

示例代码:
    # 使用缓存
    cache_key = f'rec_{user_id}_{occasion}_{season}'
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    result = recommend_outfit(user_id, context)
    cache.set(cache_key, result, timeout=3600)  # 缓存1小时
    
    # 异步保存历史
    save_history.delay(user_id, result)  # Celery 异步任务
"""

# ============================================================================
# 6. 故障排查
# ============================================================================

"""
───────────────────────────────────────────────────────────────────────────────
常见问题排查
───────────────────────────────────────────────────────────────────────────────

问题1: 返回 error_code='USER_NOT_FOUND'
  原因: 用户不存在或被删除
  排查: 验证 user_id 有效性
  解决: 处理认证、创建新用户


问题2: 返回 error_code='WARDROBE_EMPTY'
  原因: 用户衣橱中没有衣物
  排查: 检查 ClothingItem 是否存在
  解决: 引导用户添加衣物


问题3: confidence 很低 (< 0.5)
  原因: 衣服很少、画像不完整、搭配困难
  排查: 检查衣橱数量和类型多样性
  解决: 建议用户补充衣物


问题4: 返回为空列表 items=[]
  原因: 推荐引擎未找到合适搭配
  排查: 检查 season/occasion 过滤条件
  解决: 放宽过滤条件或增加衣物


问题5: 保存历史失败 (status='failure')
  原因: 数据库连接问题
  排查: 检查数据库状态、事务锁
  解决: 重试、检查数据库日志


───────────────────────────────────────────────────────────────────────────────
调试工具
───────────────────────────────────────────────────────────────────────────────

1. 运行测试:
    python backend/libs/recomx/test_recomx.py
    
    或使用 pytest:
    pytest backend/libs/recomx/test_recomx.py -v

2. 启用日志:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('backend.libs.recomx.core')
    
    result = recommend_outfit(user_id, context)
    # 查看详细日志

3. 数据库查询:
    # 检查推荐历史
    from backend.models.database import Recommendation
    
    history = Recommendation.query.filter_by(user_id=1).all()
    for h in history:
        print(h.to_dict())
"""

# ============================================================================
# 7. 性能指标
# ============================================================================

"""
推荐性能目标:

Operation           | Baseline | Target | Notes
────────────────────┼──────────┼────────┼────────────────────────────
recommend_outfit    | 500ms    | <200ms | 依赖服务层算法优化
save_history        | 50ms     | <50ms  | 数据库写入
load_history        | 100ms    | <100ms | 数据库查询

瓶颈分析:
    1. recommend_outfit: 推荐算法 (RecommendationEngine)
    2. 数据库: 大量衣物查询
    3. 网络: API 响应时间

优化方向:
    1. 缓存常见推荐
    2. 异步后台任务
    3. 推荐引擎算法优化 (见 CHANGELOG 的 TODO 列表)
"""

# ============================================================================
# 8. 版本历史
# ============================================================================

"""
RecomX 更新日志:

v2.1 (2025-11-16) - 完整实现
    ✓ 推荐引擎接口层完成
    ✓ 历史记录管理
    ✓ 完整错误处理
    ✓ 代码文档和示例
    ✓ 单元测试

v2.0 (2025-11-12) - 初始发布
    ✓ 基本推荐功能骨架

待实现 (v2.2+):
    □ 个性化算法优化 (机器学习)
    □ 实时推荐 (WebSocket)
    □ A/B 测试框架
    □ 推荐多样性优化
    □ 可观测性增强 (metrics/tracing)
"""
