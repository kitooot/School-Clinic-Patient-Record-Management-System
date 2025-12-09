"""Sorting helpers for patient records."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Callable, Iterable, Optional, Sequence, Tuple # Type hinting

import customtkinter as ctk # For custom Tkinter widgets
from tkinter import messagebox  # For message boxes

from system_configs.config import ACCENT, CARD_BG, PRIMARY, SECONDARY, TEXT # Import color constants

# Module-level variables for sorting context.
_cursor = None
_sort_field_options = {}
_sort_field_labels = {}
_date_sort_fields: Sequence[str] = ()
_root = None
_refresh_callback: Optional[Callable[[], None]] = None

current_sort_field = "patient_id"
current_sort_order = "ASC"

# Configure module-level dependencies and callbacks.
def configure(
    *,
    cursor,
    sort_field_options,
    sort_field_labels,
    date_sort_fields,
    root,
    refresh_callback: Callable[[], None],
) -> None:
    """Configure module-level dependencies and callbacks."""
    global _cursor, _sort_field_options, _sort_field_labels, _date_sort_fields, _root, _refresh_callback
    _cursor = cursor
    _sort_field_options = dict(sort_field_options)
    _sort_field_labels = dict(sort_field_labels)
    _date_sort_fields = tuple(date_sort_fields)
    _root = root
    _refresh_callback = refresh_callback

# Fetch patients applying optional filters and the current sort state.
def fetch_patients(filter_field: Optional[str], filter_term: Optional[str]) -> Iterable[Tuple]:
    """Retrieve patients applying optional filters and the current sort state."""
    global current_sort_field, current_sort_order

    if _cursor is None:
        return []

    sort_field = current_sort_field if current_sort_field in _sort_field_options.values() else "patient_id"
    sort_order = current_sort_order if current_sort_order in ("ASC", "DESC") else "ASC"

    query = (
        "select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date "
        "from patient"
    )
    params = []

    if filter_field and filter_term:
        query += f" where LOWER({filter_field}) LIKE %s"
        params.append(f"%{filter_term.lower()}%")

    if sort_field == "patient_id":
        numeric_expr = "CASE WHEN patient_id REGEXP '^[0-9]+$' THEN CAST(patient_id AS UNSIGNED) ELSE NULL END"
        query += (
            f" order by ({numeric_expr} IS NULL) ASC, "
            f"{numeric_expr} {sort_order}, patient_id {sort_order}"
        )
    elif sort_field in _date_sort_fields:
        query += f" order by STR_TO_DATE({sort_field}, '%m/%d/%Y') {sort_order}"
    else:
        query += f" order by {sort_field} {sort_order}"

    _cursor.execute(query, tuple(params))
    return _cursor.fetchall()

# Open a dialog to select sorting options.
def open_sort_dialog():  # pragma: no cover - UI callback
    sort_window = ctk.CTkToplevel()
    sort_window.title("Sort Patients")
    sort_window.grab_set()
    sort_window.resizable(False, False)
    sort_window.configure(fg_color=ACCENT)
    if _root is not None:
        sort_window.transient(_root)

    container = ctk.CTkFrame(sort_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24)
    container.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(container, text="Sort By", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=0, column=0, padx=12, pady=(6, 8), sticky="ew"
    )

    field_var = ctk.StringVar(value=_sort_field_labels.get(current_sort_field, "Patient ID"))
    field_menu = ctk.CTkOptionMenu(
        container,
        values=list(_sort_field_options.keys()),
        variable=field_var,
        font=("Segoe UI", 13),
        fg_color=SECONDARY,
        button_color=SECONDARY,
        button_hover_color=PRIMARY,
    )
    field_menu.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

    ctk.CTkLabel(container, text="Order", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=2, column=0, padx=12, pady=(12, 8), sticky="ew"
    )

    order_var = ctk.StringVar(value="Ascending" if current_sort_order == "ASC" else "Descending")
    order_menu = ctk.CTkOptionMenu(
        container,
        values=["Ascending", "Descending"],
        variable=order_var,
        font=("Segoe UI", 13),
        fg_color=SECONDARY,
        button_color=SECONDARY,
        button_hover_color=PRIMARY,
    )
    order_menu.grid(row=3, column=0, padx=12, pady=(0, 16), sticky="ew")

    button_frame = ctk.CTkFrame(container, fg_color="transparent")
    button_frame.grid(row=4, column=0, padx=12, pady=(6, 0), sticky="ew")
    button_frame.grid_columnconfigure((0, 1), weight=1)

    # Apply the selected sorting options.
    def apply_sort():
        global current_sort_field, current_sort_order
        current_sort_field = _sort_field_options.get(field_var.get(), "patient_id")
        current_sort_order = "ASC" if order_var.get() == "Ascending" else "DESC"
        sort_window.destroy()
        if _refresh_callback is not None:
            _refresh_callback()

    apply_button = ctk.CTkButton(
        button_frame,
        text="Apply",
        command=apply_sort,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=12,
        font=("Segoe UI", 13, "bold"),
    )
    apply_button.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")

    cancel_button = ctk.CTkButton(
        button_frame,
        text="Cancel",
        command=sort_window.destroy,
        fg_color="#95A5A6",
        hover_color="#7F8C8D",
        corner_radius=12,
        font=("Segoe UI", 13, "bold"),
    )
    cancel_button.grid(row=0, column=1, padx=(6, 0), pady=4, sticky="ew")


__all__ = [
    "configure",
    "fetch_patients",
    "open_sort_dialog",
    "current_sort_field",
    "current_sort_order",
]
