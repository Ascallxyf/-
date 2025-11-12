# ProfileX 模块入口
# 作用：对外暴露用户画像读取/更新与向量化能力，供 backend/api/user.py 使用。
# 对外API：get_profile, update_profile, compute_style_vector
# TODO（实现者）：
# - 对接数据库模型（UserProfile），保证字段与前端保持一致
# - 在 compute_style_vector 中定义稳定的向量维度与映射逻辑
# - 做好空值/异常输入的校验与错误抛出（ValueError）
from .core import get_profile, update_profile, compute_style_vector
