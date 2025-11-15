# core.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
import sqlite3
import os
from .image_utils import extract_color_palette, generate_thumbnail


# 初始化数据库（ClothingItem 模型）
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "instance", "wardrobe.db")
def init_db():
    """初始化衣物表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clothing_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,  # 如上衣/裤子
            color TEXT NOT NULL,     # 存储为逗号分隔的 RGB 元组（如 "(255,255,255),(0,0,0)"）
            season TEXT NOT NULL,    # 如春季/夏季
            image_url TEXT NOT NULL, # 原图路径
            thumbnail_url TEXT       # 缩略图路径
        )
    ''')
    conn.commit()
    conn.close()
init_db()


def add_item(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """添加衣物条目（需确保 data 包含 name/category/season/image_url）"""
    # 1. 调用图片工具处理
    image_path = data["image_url"]
    colors = extract_color_palette(image_path)
    thumbnail_url = generate_thumbnail(image_path)
    # 颜色转为字符串存储
    color_str = ",".join([str(c) for c in colors])

    # 2. 数据入库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clothing_items (user_id, name, category, color, season, image_url, thumbnail_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data["name"],
        data["category"],
        color_str,
        data["season"],
        image_path,
        thumbnail_url
    ))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # 3. 返回结果
    return {
        "item_id": item_id,
        "user_id": user_id,
        **data,
        "color": colors,
        "thumbnail_url": thumbnail_url
    }


def update_item(item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """更新衣物条目"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 构造更新字段
    fields = []
    values = []
    for key in ["name", "category", "season"]:
        if key in data:
            fields.append(f"{key}=?")
            values.append(data[key])
    # 若更新了图片，重新处理
    if "image_url" in data:
        image_path = data["image_url"]
        colors = extract_color_palette(image_path)
        thumbnail_url = generate_thumbnail(image_path)
        fields.extend(["image_url=?", "color=?", "thumbnail_url=?"])
        values.extend([image_path, ",".join([str(c) for c in colors]), thumbnail_url])
    
    values.append(item_id)
    cursor.execute(f'''
        UPDATE clothing_items SET {", ".join(fields)} WHERE item_id=?
    ''', tuple(values))
    conn.commit()

    # 查询更新后的结果
    cursor.execute("SELECT * FROM clothing_items WHERE item_id=?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError("Item not found")
    return {
        "item_id": row[0],
        "user_id": row[1],
        "name": row[2],
        "category": row[3],
        "color": [eval(c) for c in row[4].split(",")],
        "season": row[5],
        "image_url": row[6],
        "thumbnail_url": row[7]
    }


def delete_item(item_id: int) -> None:
    """删除衣物条目"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clothing_items WHERE item_id=?", (item_id,))
    conn.commit()
    conn.close()


def list_items(user_id: int) -> List[Dict[str, Any]]:
    """列出用户的所有衣物"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clothing_items WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "item_id": row[0],
            "user_id": row[1],
            "name": row[2],
            "category": row[3],
            "color": [eval(c) for c in row[4].split(",")],
            "season": row[5],
            "image_url": row[6],
            "thumbnail_url": row[7]
        }
        for row in rows
    ]


def process_upload(file_path: str) -> Dict[str, Any]:
    """处理上传的图片，返回元信息"""
    colors = extract_color_palette(file_path)
    thumbnail_url = generate_thumbnail(file_path)
    # 获取图片宽高
    with Image.open(file_path) as img:
        width, height = img.size
    return {
        "image_url": file_path,
        "colors": colors,
        "mime": "image/jpeg",  # 简化处理，实际可通过 filetype 库识别
        "width": width,
        "height": height,
        "thumbnail_url": thumbnail_url
    }

from __future__ import annotations
from typing import Dict, Any, List, Optional

# NOTE: Implementation to be completed by Wardrobe Owner.

def add_item(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError


def update_item(item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError


def delete_item(item_id: int) -> None:
    raise NotImplementedError


def list_items(user_id: int) -> List[Dict[str, Any]]:
    raise NotImplementedError


def process_upload(file_path: str) -> Dict[str, Any]:
    """Extract metadata, generate thumbnail, return info for DB and frontend."""
    raise NotImplementedError

