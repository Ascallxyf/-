"""User Profile library.
Contracts:
- get_profile(user_id: int) -> dict
- update_profile(user_id: int, data: dict) -> dict
- compute_style_vector(profile: dict) -> list[float]
"""
from __future__ import annotations
from typing import Dict, Any, List

# NOTE: Implementation to be completed by Profile Owner.

def get_profile(user_id: int) -> Dict[str, Any]:
    """Fetch profile from DB and return as dict."""
    raise NotImplementedError


def update_profile(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and persist profile updates, returning updated profile dict."""
    raise NotImplementedError


def compute_style_vector(profile: Dict[str, Any]) -> List[float]:
    """Project profile preferences into a numeric vector for recommendation input."""
    raise NotImplementedError
