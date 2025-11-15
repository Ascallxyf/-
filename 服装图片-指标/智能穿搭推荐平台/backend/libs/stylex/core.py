"""StyleX 核心实现（已补充）"""

职责：
    - 基于图片进行风格标签与调色板分析
    - 与 WardrobeX 的颜色提取保持一致或共享工具方法

对外契约：
    analyze_style(image_url: str | None = None, image_path: str | None = None) -> {tags, palette}
    extract_tags(image_path: str) -> list[str]

实现思路提示：
    1. 如果传入 image_url，需要先下载到临时文件再分析
    2. 调色板复用 extract_color_palette（避免重复逻辑）
    3. 标签提取可以先用文件名/元数据 + 颜色聚类的粗分类占位，后续再接模型
    4. 性能控制：避免在单次调用中加载大型深度模型（可延迟或缓存）

错误处理：
    - 文件不存在或读取失败 -> ValueError 或 RuntimeError
    - image_url 下载失败 -> ValueError（前端可提示 URL 无效）
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import requests
import tempfile
import os
from wardrobex.utils import extract_color_palette  # 假设WardrobeX提供颜色提取工具

# 临时占位：模拟标签提取（后续可替换为模型推理）
def _extract_tags_from_meta(image_path: str) -> List[str]:
    """从文件名、元数据或颜色粗聚类生成临时标签（占位逻辑）"""
    file_name = os.path.basename(image_path)
    # 示例：从文件名关键词、颜色聚类结果生成标签
    color_palette = extract_color_palette(image_path)
    color_tags = [f"color_{r}_{g}_{b}" for r, g, b in color_palette]
    name_tags = file_name.split('.')[0].split('_')
    return list(set(name_tags + color_tags))  # 去重后返回

def analyze_style(image_url: Optional[str] = None, image_path: Optional[str] = None) -> Dict[str, Any]:
    """
    分析图片的风格标签与调色板
    
    :param image_url: 图片的网络URL
    :param image_path: 本地图片路径
    :return: 包含'tags'（风格标签列表）和'palette'（RGB三元组列表）的字典
    :raises ValueError: 输入无效或下载失败时抛出
    :raises RuntimeError: 文件读取失败时抛出
    """
    # 校验输入：必须提供image_url或image_path之一
    if not image_url and not image_path:
        raise ValueError("必须提供image_url或image_path")
    
    # 处理image_url的情况：下载到临时文件
    if image_url:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()  # 若HTTP状态非200，抛出异常
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(response.content)
                temp_path = f.name
            # 后续分析使用临时文件路径
            image_path = temp_path
        except requests.RequestException as e:
            raise ValueError(f"图片URL下载失败: {str(e)}")
    
    # 校验本地文件是否存在
    if not os.path.exists(image_path):
        raise ValueError(f"文件不存在: {image_path}")
    
    # 提取调色板（复用WardrobeX的工具）
    palette = extract_color_palette(image_path)  # 输出格式：[(r, g, b), ...]，与WardrobeX一致
    
    # 提取风格标签
    tags = _extract_tags_from_meta(image_path)
    
    # 清理临时文件
    if 'temp_path' in locals():
        os.unlink(temp_path)
    
    return {
        "tags": tags,
        "palette": palette
    }

def extract_tags(image_path: str) -> List[str]:
    """
    提取图片的风格标签
    
    :param image_path: 本地图片路径
    :return: 风格标签列表
    :raises ValueError: 文件不存在时抛出
    :raises RuntimeError: 文件读取失败时抛出
    """
    if not os.path.exists(image_path):
        raise ValueError(f"文件不存在: {image_path}")
    return _extract_tags_from_meta(image_path)
from __future__ import annotations
from typing import Dict, Any, List, Optional

# NOTE: Implementation to be completed by Style Owner.

def analyze_style(image_url: Optional[str] = None, image_path: Optional[str] = None) -> Dict[str, Any]:
    raise NotImplementedError


def extract_tags(image_path: str) -> List[str]:
    raise NotImplementedError

