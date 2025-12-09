"""Search and filter helpers for the clinic system."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Callable, Optional, Tuple # Type hinting

# Module-level variables for search controls and callbacks.
_search_entry = None
_search_field_var = None
_search_field_options = {}
_refresh_callback: Optional[Callable[[], None]] = None

# Set up search controls and refresh behaviour.
def configure(
    *,
    search_entry,
    search_field_var,
    search_field_options,
    refresh_callback: Callable[[], None],
) -> None:
    """Set up search controls and refresh behaviour."""
    global _search_entry, _search_field_var, _search_field_options, _refresh_callback
    _search_entry = search_entry
    _search_field_var = search_field_var
    _search_field_options = dict(search_field_options)
    _refresh_callback = refresh_callback

# Get the current search field and term for filtering.
def get_filter() -> Tuple[Optional[str], Optional[str]]:
    """Return the current search field and term for filtering."""
    filter_field = None
    filter_term = None

    if _search_entry is not None and _search_field_var is not None:
        try:
            term = _search_entry.get().strip()
        except Exception:
            term = ""
        if term:
            selected_label = _search_field_var.get() if hasattr(_search_field_var, "get") else "Patient ID"
            filter_field = _search_field_options.get(selected_label, "patient_id")
            filter_term = term

    return filter_field, filter_term

# Handle changes in the search entry field.
def on_search_entry_change(event=None) -> None:  # pragma: no cover - UI callback
    if _refresh_callback is not None:
        _refresh_callback()

# Handle changes in the selected search field.
def on_search_field_change(choice) -> None:  # pragma: no cover - UI callback
    if _refresh_callback is not None:
        _refresh_callback()


__all__ = [
    "configure",
    "get_filter",
    "on_search_entry_change",
    "on_search_field_change",
]
