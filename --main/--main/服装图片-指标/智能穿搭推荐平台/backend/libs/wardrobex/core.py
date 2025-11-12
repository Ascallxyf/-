"""Wardrobe inventory and upload helpers.
Contracts:
- add_item(user_id: int, data: dict) -> dict
- update_item(item_id: int, data: dict) -> dict
- delete_item(item_id: int) -> None
- list_items(user_id: int) -> list[dict]
- process_upload(file_path: str) -> dict {image_url, colors, mime, width, height}
"""
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
