"""Utility functions for serializing data to JSON-compatible formats."""
from typing import Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


def serialize_for_json(obj: Any) -> Any:
    """
    Recursively convert non-JSON-serializable objects to JSON-compatible types.
    
    Handles:
    - date/datetime -> ISO format strings
    - Decimal -> float or string
    - UUID -> string
    - dict/list -> recursively process nested objects
    
    Args:
        obj: Object to serialize (can be any type)
        
    Returns:
        JSON-serializable version of the object
    """
    if obj is None:
        return None
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        # Convert Decimal to float for JSON compatibility
        # Use float() to preserve numeric type, but handle precision
        try:
            return float(obj)
        except (OverflowError, ValueError):
            # If conversion fails, return as string
            return str(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, set):
        return [serialize_for_json(item) for item in sorted(obj)]
    elif isinstance(obj, bytes):
        # Convert bytes to base64 string for JSON compatibility
        import base64
        return base64.b64encode(obj).decode('utf-8')
    else:
        # For other types, try to convert to string as fallback
        # This handles custom types, enums, etc.
        try:
            # Check if it's a basic JSON-serializable type
            import json
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # If not serializable, convert to string
            logger.debug(f"Converting non-serializable type {type(obj)} to string: {obj}")
            return str(obj)

