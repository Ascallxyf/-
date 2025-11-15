"""Common helpers for API blueprints."""
from __future__ import annotations

from typing import Dict, List

from flask import jsonify

from backend.libs.apix import ValidationResult


def respond(payload: Dict[str, object]):
    """Return a Flask response tuple from an ApiX payload."""
    return jsonify(payload), int(payload.get('code', 200))


def collect_validation_errors(result: ValidationResult) -> Dict[str, List[str]]:
    """Convert ValidationResult errors to {field: [messages]} structure."""
    errors: Dict[str, List[str]] = {}
    for entry in result.errors:
        errors.setdefault(entry.field, []).append(entry.message)
    return errors
