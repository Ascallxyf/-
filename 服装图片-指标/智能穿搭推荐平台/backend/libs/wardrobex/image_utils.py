# image_utils.py
from __future__ import annotations
from typing import List, Tuple
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import os


def extract_color_palette(image_path: str, k: int = 5) -> List[Tuple[int, int, int]]:
    """提取图片的 top-k 主色调（RGB 元组）"""
    try:
        # 打开图片并转为 RGB 模式
        with Image.open(image_path).convert("RGB") as img:
            # 缩放图片加速处理
            img = img.resize((100, 100))
            # 转为像素数组 (n, 3)
            pixels = np.array(img).reshape(-1, 3)
            
            # KMeans 聚类提取主色
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(pixels)
            # 转为整数 RGB 元组
            colors = [tuple(map(int, color)) for color in kmeans.cluster_centers_]
            return colors
    except Exception as e:
        # 异常时返回空列表
        print(f"提取颜色失败: {e}")
        return []


def generate_thumbnail(image_path: str, max_size: int = 512) -> str:
    """生成缩略图，保存到原图片同目录，返回缩略图路径"""
    try:
        with Image.open(image_path) as img:
            # 按比例缩放（不超过 max_size）
            img.thumbnail((max_size, max_size))
            
            # 构造缩略图路径（原文件名后加 _thumb）
            dirname, filename = os.path.split(image_path)
            name, ext = os.path.splitext(filename)
            thumb_path = os.path.join(dirname, f"{name}_thumb{ext}")
            
            # 保存缩略图
            img.save(thumb_path)
            return thumb_path
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        return ""

from __future__ import annotations
from typing import List, Tuple

# NOTE: Implementation to be completed by Wardrobe Owner.

def extract_color_palette(image_path: str, k: int = 5) -> List[Tuple[int, int, int]]:
    """Return top-k RGB color tuples found in the image."""
    raise NotImplementedError


def generate_thumbnail(image_path: str, max_size: int = 512) -> str:
    """Create a resized thumbnail next to the original and return the thumbnail path."""
    raise NotImplementedError

