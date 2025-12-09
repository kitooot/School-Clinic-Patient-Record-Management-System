"""Import and export features split from the main system module."""
from __future__ import annotations # Ensure compatibility with future Python versions

import os # For file system operations
from typing import Callable, Optional # For type hinting

import customtkinter as ctk # For custom Tkinter widgets
import pandas # For data manipulation
from pymysql.err import IntegrityError # For handling database integrity errors
from tkinter import filedialog, messagebox # For file dialogs and message boxes

from system_configs.config import ACCENT, CARD_BG, PRIMARY, SECONDARY, TEXT # Import color constants
from system_configs.helpers import normalize_column_name as _default_normalize_column_name # Import default helper function
from system_configs.helpers import normalize_mobile as _default_normalize_mobile # Import default helper function
from system_configs.helpers import to_proper_case as _default_to_proper_case # Import default helper function
from system_configs.import_service import REQUIRED_COLUMNS as DEFAULT_REQUIRED_COLUMNS # Import default required columns

# Module-level variables to hold dependencies
_cursor = None
_connection = None
_root = None
_refresh_callback: Optional[Callable[[], None]] = None
_has_openpyxl = False
_fpdf_cls = None
_figure_cls = None
_export_records = None
_export_analytics = None
_normalize_mobile = _default_normalize_mobile
_normalize_column_name = _default_normalize_column_name
_to_proper_case = _default_to_proper_case

# Configure module-level dependencies.
def configure(
    *,
    cursor,
    connection,
    root,
    refresh_callback: Callable[[], None],
    has_openpyxl: bool,
    fpdf_cls,
    figure_cls,
    export_records_fn: Callable[[object, str], None],
    export_analytics_fn: Callable[[object, str, object, object, str, str], None],
    normalize_mobile: Callable[[str], Optional[str]] = _default_normalize_mobile,
    normalize_column_name: Callable[[str], str] = _default_normalize_column_name,
    to_proper_case: Callable[[str], str] = _default_to_proper_case,
) -> None:
    """Configure module-level dependencies."""
    global _cursor, _connection, _root, _refresh_callback
    global _has_openpyxl, _fpdf_cls, _figure_cls
    global _export_records, _export_analytics
    global _normalize_mobile, _normalize_column_name, _to_proper_case

    _cursor = cursor
    _connection = connection
    _root = root
    _refresh_callback = refresh_callback
    _has_openpyxl = has_openpyxl
    _fpdf_cls = fpdf_cls
    _figure_cls = figure_cls
    _export_records = export_records_fn
    _export_analytics = export_analytics_fn
    _normalize_mobile = normalize_mobile
    _normalize_column_name = normalize_column_name
    _to_proper_case = to_proper_case

# Export data (records or analytics) based on user selection.
def export_data(figure_primary: str, figure_secondary: str) -> None:  # pragma: no cover - UI callback
    export_window = ctk.CTkToplevel()
    export_window.title("Export Options")
    export_window.grab_set()
    export_window.resizable(False, False)
    export_window.configure(fg_color=ACCENT)
    if _root is not None:
        export_window.transient(_root)

    container = ctk.CTkFrame(export_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24)
    container.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(container, text="Choose what to export", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=0, column=0, padx=12, pady=(6, 12), sticky="ew"
    )

    choice_var = ctk.StringVar(value="records")

    ctk.CTkRadioButton(
        container,
        text="Patient Records (Excel)",
        value="records",
        variable=choice_var,
        font=("Segoe UI", 13),
        text_color=TEXT,
    ).grid(row=1, column=0, padx=12, pady=4, sticky="w")

    ctk.CTkRadioButton(
        container,
        text="Patient Analytics (PDF)",
        value="analytics",
        variable=choice_var,
        font=("Segoe UI", 13),
        text_color=TEXT,
    ).grid(row=2, column=0, padx=12, pady=4, sticky="w")

    button_row = ctk.CTkFrame(container, fg_color="transparent")
    button_row.grid(row=3, column=0, padx=12, pady=(18, 4), sticky="ew")
    button_row.grid_columnconfigure((0, 1), weight=1)

    # Perform the export based on user selection.
    def _perform_export():
        selection = choice_var.get()
        export_window.destroy()

        if selection == "records":
            if not _has_openpyxl:
                messagebox.showerror(
                    "Missing Dependency",
                    'Excel export requires the "openpyxl" package. Install it with "pip install openpyxl" and try again.',
                )
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
            )
            if not file_path:
                return
            try:
                _export_records(_cursor, file_path)
            except ValueError as exc:
                messagebox.showinfo("Export", str(exc))
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to export Excel file: {exc}")
            else:
                messagebox.showinfo("Success", f"Export completed: {file_path}")
        else:
            if _fpdf_cls is None:
                messagebox.showerror(
                    "Missing Dependency",
                    'Analytics export to PDF requires the "fpdf" package. Install it with "pip install fpdf" and try again.',
                )
                return
            if _figure_cls is None:
                messagebox.showerror(
                    "Missing Dependency",
                    'Analytics export to PDF requires the "matplotlib" package. Install it with "pip install matplotlib" and try again.',
                )
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
            )
            if not file_path:
                return
            try:
                _export_analytics(_cursor, file_path, _fpdf_cls, _figure_cls, figure_primary, figure_secondary)
            except ValueError as exc:
                messagebox.showinfo("Export", str(exc))
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to export PDF: {exc}")
            else:
                messagebox.showinfo("Success", f"Export completed: {file_path}")

    ctk.CTkButton(
        button_row,
        text="Export",
        command=_perform_export,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=12,
        font=("Segoe UI", 13, "bold"),
    ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

    ctk.CTkButton(
        button_row,
        text="Cancel",
        command=export_window.destroy,
        fg_color="#95A5A6",
        hover_color="#7F8C8D",
        corner_radius=12,
        font=("Segoe UI", 13, "bold"),
    ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

# Import patient data from an Excel or CSV file.
def import_data(required_columns=None) -> None:  # pragma: no cover - UI callback
    filepath = filedialog.askopenfilename(
        title="Import Patient Data",
        filetypes=[
            ("Excel Files", "*.xlsx;*.xlsm;*.xltx;*.xltm"),
            ("CSV Files", "*.csv"),
            ("All Files", "*.*"),
        ],
    )
    if not filepath:
        return

    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    try:
        if ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
            if not _has_openpyxl:
                messagebox.showerror(
                    "Missing Dependency",
                    'Excel import requires the "openpyxl" package. Install it with "pip install openpyxl" and try again.',
                )
                return
            data_frame = pandas.read_excel(filepath, dtype=str)
        else:
            data_frame = pandas.read_csv(filepath, dtype=str)
    except Exception as exc:
        messagebox.showerror("Error", f"Unable to read the selected file: {exc}")
        return

    if data_frame.empty:
        messagebox.showinfo("Import", "The selected file does not contain any records.")
        return

    normalized_to_original = {
        _normalize_column_name(col): col for col in data_frame.columns
    }

    required_columns = required_columns or DEFAULT_REQUIRED_COLUMNS

    resolved_columns = {}
    missing_fields = []
    for field, normalized in required_columns.items():
        if normalized in normalized_to_original:
            resolved_columns[field] = normalized_to_original[normalized]
        else:
            missing_fields.append(field)

    if missing_fields:
        pretty_missing = ", ".join(field.replace("_", " ").title() for field in missing_fields)
        messagebox.showerror("Error", f"Missing required columns in file: {pretty_missing}")
        return

    # Helper to get value from row with proper handling.
    def get_value(row, field):
        value = row[resolved_columns[field]]
        if pandas.isna(value):
            return ""
        return str(value).strip()

    # Perform the import operation.
    inserted = 0
    skipped = 0
    error_samples = []
    field_labels = {
        "patient_id": "patient ID",
        "name": "name",
        "mobile": "mobile number",
        "email": "email",
        "address": "address",
        "gender": "gender",
        "dob": "date of birth",
        "diagnosis": "diagnosis",
        "visit_date": "visit date",
    }

    for idx, row in data_frame.iterrows():
        excel_row = idx + 2
        patient_id = get_value(row, "patient_id")
        name = get_value(row, "name")
        mobile = get_value(row, "mobile")
        email_value = get_value(row, "email")
        address_value = get_value(row, "address")
        gender_value = get_value(row, "gender")
        dob_value = get_value(row, "dob")
        diagnosis_value = get_value(row, "diagnosis")
        visit_date_value = get_value(row, "visit_date")

        required_values = {
            "patient_id": patient_id,
            "name": name,
            "mobile": mobile,
            "email": email_value,
            "address": address_value,
            "gender": gender_value,
            "dob": dob_value,
            "diagnosis": diagnosis_value,
            "visit_date": visit_date_value,
        }

        missing_values = [field_labels[key] for key, value in required_values.items() if not value]
        if missing_values:
            skipped += 1
            if len(error_samples) < 5:
                missing_text = ", ".join(missing_values)
                error_samples.append(f"Row {excel_row}: Missing {missing_text}.")
            continue

        formatted_mobile = _normalize_mobile(mobile)
        if not formatted_mobile:
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(
                    f"Row {excel_row}: Mobile number must follow +63 000 000 0000 format."
                )
            continue

        name = _to_proper_case(name)
        address_value = _to_proper_case(address_value)
        diagnosis_value = _to_proper_case(diagnosis_value)

        try:
            query = (
                "insert into patient ("
                "patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date"
                ") values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            _cursor.execute(
                query,
                (
                    patient_id,
                    name,
                    formatted_mobile,
                    email_value,
                    address_value,
                    gender_value,
                    dob_value,
                    diagnosis_value,
                    visit_date_value,
                ),
            )
            _connection.commit()
            inserted += 1
        except IntegrityError:
            _connection.rollback()
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f"Row {excel_row}: Patient ID already exists.")
        except Exception as exc:
            _connection.rollback()
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f"Row {excel_row}: {exc}")

    if _refresh_callback is not None:
        _refresh_callback()

    summary_message = f"Imported {inserted} record(s)."
    if skipped:
        summary_message += f"\nSkipped {skipped} record(s)."
    if error_samples:
        summary_message += "\n\nSample issues:\n" + "\n".join(error_samples)

    messagebox.showinfo("Import Complete", summary_message)


__all__ = [
    "configure",
    "export_data",
    "import_data",
]
