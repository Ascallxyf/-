"""Style analysis from image and metadata.
Contracts:
- analyze_style(image_url: str | None = None, image_path: str | None = None) -> dict {tags, palette}
- extract_tags(image_path: str) -> list[str]
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional

# NOTE: Implementation to be completed by Style Owner.

def analyze_style(image_url: Optional[str] = None, image_path: Optional[str] = None) -> Dict[str, Any]:
    raise NotImplementedError


def extract_tags(image_path: str) -> List[str]:
    raise NotImplementedError
