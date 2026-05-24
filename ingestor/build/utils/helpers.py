"""
Helper utilities for Lambda functions
"""
import logging
import json
from datetime import datetime
from typing import Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def json_serial(obj: Any) -> str:
    """
    JSON serializer for objects not serializable by default
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format currency amount
    """
    if currency == "INR":
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:.2f}"
    return f"{amount:.2f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100
