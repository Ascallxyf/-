# RecomX 模块入口
# 作用：对外暴露穿搭推荐与历史记录相关的高层API。
# 对外API：recommend_outfit, save_history, load_history
# TODO（实现者）：
# - 先实现规则/打分法 baseline，再逐步替换为 ML/深度模型
# - 保存推荐历史的最小字段（时间、items、rationale、context）
from .core import recommend_outfit, save_history, load_history
