# StyleX 模块入口
# 作用：对外暴露风格分析的高层API，供 backend/api/recommendation.py 使用。
# 对外API：analyze_style, extract_tags
# TODO（实现者）：
# - 兼容 image_url 与 image_path 两种输入方式
# - 输出与 WardrobeX 的颜色格式一致（RGB整数三元组）
from .core import analyze_style, extract_tags
