"""Selection helpers separated from the main system UI."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Optional # Type hinting

import customtkinter as ctk # For custom Tkinter widgets
from tkinter import END, MULTIPLE, Listbox, VERTICAL, messagebox # For listbox and message boxes
from tkinter import ttk # For themed widgets

from system_configs.config import ACCENT, CARD_BG, PRIMARY, SECONDARY, TEXT # Import color constants

# Module-level variables for selection context.
_patient_table = None
_root = None
_selection_action_var = None
_selection_menu_options = []

# Configure module-level context for selection handlers.
def configure(
    *,
    patient_table,
    root,
    selection_action_var,
    selection_menu_options,
) -> None:
    """Configure module-level context for selection handlers."""
    global _patient_table, _root, _selection_action_var, _selection_menu_options
    _patient_table = patient_table
    _root = root
    _selection_action_var = selection_action_var
    _selection_menu_options = list(selection_menu_options)

# Select all patients in the table.
def select_all_patients() -> None:
    if _patient_table is None:
        return

    items = _patient_table.get_children()
    if not items:
        messagebox.showinfo("Select All", "No patient records available to select.")
        return

    _patient_table.selection_set(items)
    _patient_table.focus(items[0])
    _patient_table.see(items[0])

# Clear all selected patients in the table.
def clear_selected_patients() -> None:
    if _patient_table is None:
        return

    selections = _patient_table.selection()
    if not selections:
        if _patient_table.get_children():
            messagebox.showinfo("Selection", "No patients are currently selected.")
        else:
            messagebox.showinfo("Selection", "No patient records available.")
        return
    _patient_table.selection_remove(selections)

# Select specific patients via a dialog.
def select_specific_patients() -> None:
    if _patient_table is None:
        return

    items = _patient_table.get_children()
    if not items:
        messagebox.showinfo("Select Patients", "No patient records available to select.")
        return

    records = []
    for item in items:
        values = _patient_table.item(item).get("values", [])
        if not values:
            continue
        patient_id = str(values[0])
        name = str(values[1]) if len(values) > 1 else ""
        records.append((item, patient_id, name))

    if not records:
        messagebox.showinfo("Select Patients", "No patient records available to select.")
        return

    selection_window = ctk.CTkToplevel()
    selection_window.title("Select Patients")
    selection_window.grab_set()
    selection_window.resizable(False, False)
    selection_window.configure(fg_color=ACCENT)
    if _root is not None:
        selection_window.transient(_root)
    selection_window.geometry("620x580")
    selection_window.grid_rowconfigure(0, weight=1)
    selection_window.grid_columnconfigure(0, weight=1)

    container = ctk.CTkFrame(selection_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24, sticky="nsew")
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(container, text="Select Patients", font=("Segoe UI", 18, "bold"), text_color=TEXT).grid(
        row=0, column=0, padx=12, pady=(6, 10), sticky="ew"
    )

    list_frame = ctk.CTkFrame(container, fg_color="transparent")
    list_frame.grid(row=1, column=0, sticky="nsew")
    list_frame.grid_columnconfigure(0, weight=1)
    list_frame.grid_rowconfigure(0, weight=1)

    scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL)
    scrollbar.grid(row=0, column=1, sticky="ns")

    listbox = Listbox(
        list_frame,
        selectmode=MULTIPLE,
        exportselection=False,
        width=52,
        height=18,
        font=("Segoe UI", 13),
    )
    listbox.grid(row=0, column=0, sticky="nsew")
    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    for record in records:
        item_id, patient_id, name = record
        display = f"{patient_id} - {name}" if name else patient_id
        listbox.insert(END, display)

    button_row = ctk.CTkFrame(container, fg_color="transparent")
    button_row.grid(row=2, column=0, padx=12, pady=(16, 4), sticky="ew")
    button_row.grid_columnconfigure((0, 1), weight=1)

    def _apply_selection():
        selections = listbox.curselection()
        if not selections:
            messagebox.showerror("Selection", "Please choose at least one patient.", parent=selection_window)
            return
        selected_items = [records[index][0] for index in selections]
        _patient_table.selection_set(selected_items)
        _patient_table.focus(selected_items[0])
        _patient_table.see(selected_items[0])
        selection_window.destroy()

    apply_button = ctk.CTkButton(
        button_row,
        text="Apply",
        command=_apply_selection,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=12,
        font=("Segoe UI", 13, "bold"),
    )
    apply_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

    cancel_button = ctk.CTkButton(
        button_row,
        text="Cancel",
        command=selection_window.destroy,
        fg_color="#95A5A6",
        hover_color="#7F8C8D",
        corner_radius=12,
        font=("Segoe UI", 13, "bold"),
    )
    cancel_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

#
def on_selection_action(choice: Optional[str]) -> None:
    if not choice or not _selection_menu_options:
        return

    if choice == _selection_menu_options[0]:
        return

    if choice == "Select Specific Patients":
        select_specific_patients()
    elif choice == "Select All Patients":
        select_all_patients()
    elif choice == "Clear Selection":
        clear_selected_patients()

    if _selection_action_var is not None:
        _selection_action_var.set(_selection_menu_options[0])


__all__ = [
    "configure",
    "select_all_patients",
    "clear_selected_patients",
    "select_specific_patients",
    "on_selection_action",
]
