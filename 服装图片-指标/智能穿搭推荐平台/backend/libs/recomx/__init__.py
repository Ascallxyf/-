"""RecomX 推荐引擎模块入口

对外暴露三个核心 API:
    - recommend_outfit(user_id: int, context: dict) -> dict
    - save_history(user_id: int, recommendation: dict) -> dict
    - load_history(user_id: int, limit: int = 20) -> list[dict]

使用示例:
    from backend.libs.recomx import recommend_outfit, save_history, load_history
    
    # 生成推荐
    result = recommend_outfit(
        user_id=1,
        context={'occasion': '约会', 'weather': '晴天', 'season': '春季'}
    )
    
    # 保存历史
    if result['status'] == 'success':
        save_result = save_history(1, result)
    
    # 加载历史
    history = load_history(1, limit=10)

内部实现细节在 core.py，对外隐藏。
"""

from .core import recommend_outfit, save_history, load_history

__all__ = ['recommend_outfit', 'save_history', 'load_history']
