"""Auth library wrapping Flask-Login flows.
Contracts:
- register_user(username: str, email: str, password: str) -> dict {id, username, email}
- authenticate(username_or_email: str, password: str) -> dict {id, username, email}
- get_current_user() -> dict | None
- require_auth(fn) -> wrapped view function
Error modes: ValueError on validation; PermissionError on auth; RuntimeError on system issues.
"""
from __future__ import annotations
from typing import Optional, Callable, Any, Dict
from functools import wraps

# NOTE: Implementation to be completed by Auth Owner.

def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user and return public fields.
    Should hash password (e.g., Werkzeug or bcrypt) and persist via SQLAlchemy.
    """
    raise NotImplementedError


def authenticate(username_or_email: str, password: str) -> Dict[str, Any]:
    """Verify credentials and log user in via Flask-Login's login_user.
    Returns public user dict on success; raise PermissionError otherwise.
    """
    raise NotImplementedError


def get_current_user() -> Optional[Dict[str, Any]]:
    """Return current user info if logged in; otherwise None."""
    raise NotImplementedError


def require_auth(fn: Callable) -> Callable:
    """Decorator to enforce authentication for API endpoints."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # if not current_user.is_authenticated: raise PermissionError("login required")
        raise NotImplementedError
    return wrapper
