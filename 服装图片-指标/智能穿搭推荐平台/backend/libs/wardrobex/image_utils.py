"""图片处理工具（供 WardrobeX 与 StyleX 使用）(待补充)

职责：
    - 主色调提取（RGB列表）
    - 生成缩略图（受限最大边）

实现 TODO：
    1. 使用 Pillow/OpenCV 读取图片，异常要有清晰报错
    2. 颜色聚类可用 KMeans（sklearn）或简化直方图法
    3. 确保返回的颜色为整数 RGB 元组，便于前端展示
    4. 生成的缩略图文件命名规则与存放路径要统一
"""
from __future__ import annotations
from typing import List, Tuple

# NOTE: Implementation to be completed by Wardrobe Owner.

def extract_color_palette(image_path: str, k: int = 5) -> List[Tuple[int, int, int]]:
    """Return top-k RGB color tuples found in the image."""
    raise NotImplementedError


def generate_thumbnail(image_path: str, max_size: int = 512) -> str:
    """Create a resized thumbnail next to the original and return the thumbnail path."""
    raise NotImplementedError
