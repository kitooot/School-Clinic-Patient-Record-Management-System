"""Utility helpers for patient data normalization."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Optional # For type hinting

# Normalize a mobile phone number to the standard +63 format.
def normalize_mobile(number: str) -> Optional[str]:
    """Format a raw phone number into the standardized +63 grouping."""
    if not number:
        return None

    digits = ''.join(ch for ch in str(number) if ch.isdigit())
    if digits.startswith('0') and len(digits) == 11:
        digits = '63' + digits[1:]
    elif digits.startswith('63') and len(digits) == 12:
        pass
    else:
        return None

    if len(digits) != 12 or not digits.startswith('63'):
        return None
    return f"+63 {digits[2:5]} {digits[5:8]} {digits[8:12]}"

# Normalize CSV column headers to a consistent lowercase identifier.
def normalize_column_name(column_name: str) -> str:
    """Normalize CSV column headers to a consistent lowercase identifier."""
    return ''.join(ch for ch in str(column_name).lower() if ch.isalnum())

# Convert arbitrary text into proper-case format for presentation.
def to_proper_case(value: str) -> str:
    """Convert arbitrary text into proper-case format for presentation."""
    if not value:
        return ''
    return str(value).strip().title()
