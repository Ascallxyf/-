"""Image utilities used by wardrobe and style analysis."""
from __future__ import annotations
from typing import List, Tuple

# NOTE: Implementation to be completed by Wardrobe Owner.

def extract_color_palette(image_path: str, k: int = 5) -> List[Tuple[int, int, int]]:
    """Return top-k RGB color tuples found in the image."""
    raise NotImplementedError


def generate_thumbnail(image_path: str, max_size: int = 512) -> str:
    """Create a resized thumbnail next to the original and return the thumbnail path."""
    raise NotImplementedError
