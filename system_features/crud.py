"""Tkinter-backed patient CRUD helpers for the management system UI."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Callable, Iterable, Optional, Tuple # For type hinting

import customtkinter as ctk # For custom Tkinter widgets
from pymysql.err import IntegrityError # For handling database integrity errors
from tkinter import END, StringVar, W, messagebox # For message boxes
from tkinter import ttk # For themed Tkinter widgets

from system_configs.config import ACCENT, CARD_BG, PRIMARY, SECONDARY, TEXT # Import color constants

# Allowed column names for filtered lookups to avoid unsafe SQL fragments.
_ALLOWED_FILTER_COLUMNS = {
    "patient_id",
    "name",
    "mobile",
    "email",
    "address",
    "gender",
    "dob",
    "diagnosis",
    "visit_date",
}

# Date of Birth dropdown options
_DOB_MONTHS = ["Month"] + [str(i) for i in range(1, 13)]
_DOB_DAYS = ["Day"] + [str(i) for i in range(1, 32)]
_DOB_YEARS = ["Year"] + [str(i) for i in range(1990, 2031)]
_GENDER_OPTIONS = ["Male", "Female", "Other"]

# Module-level variables to hold UI widgets and helper callbacks
_patient_table = None
_cursor = None
_connection = None
_root = None
_fetch_patients: Optional[Callable[[Optional[str], Optional[str]], Iterable[Tuple]]] = None
_get_filter: Optional[Callable[[], Tuple[Optional[str], Optional[str]]]] = None
_get_current_date: Optional[Callable[[], str]] = None
_normalize_mobile: Optional[Callable[[str], Optional[str]]] = None
_to_proper_case: Optional[Callable[[str], str]] = None

# Configure module-level dependencies and UI widgets.
def configure(
    *,
    patient_table,
    cursor,
    connection,
    root,
    fetch_patients: Callable[[Optional[str], Optional[str]], Iterable[Tuple]],
    get_filter: Callable[[], Tuple[Optional[str], Optional[str]]],
    get_current_date: Callable[[], str],
    normalize_mobile: Callable[[str], Optional[str]],
    to_proper_case: Callable[[str], str],
) -> None:
    """Wire UI widgets and helper callbacks used by the CRUD routines."""
    global _patient_table, _cursor, _connection, _root
    global _fetch_patients, _get_filter, _get_current_date
    global _normalize_mobile, _to_proper_case

    _patient_table = patient_table
    _cursor = cursor
    _connection = connection
    _root = root
    _fetch_patients = fetch_patients
    _get_filter = get_filter
    _get_current_date = get_current_date
    _normalize_mobile = normalize_mobile
    _to_proper_case = to_proper_case

# Format a string value to proper case.
def _format_case(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if _to_proper_case is not None:
        return _to_proper_case(value)
    return value.title()

# Format and normalize a mobile number.
def _format_mobile(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if _normalize_mobile is None:
        return value
    normalized = _normalize_mobile(value)
    return normalized or ""

# Get the current visit date from the provided callback.
def _current_visit_date() -> str:
    if _get_current_date is None:
        return ""
    try:
        return _get_current_date()
    except Exception:
        return ""

# Ensure that the database connection is available.
def _ensure_db(parent) -> bool:
    if _cursor is None or _connection is None:
        messagebox.showerror("Error", "Database connection is not configured.", parent=parent)
        return False
    return True

# Fetch a patient record by patient ID.
def _fetch_patient_by_id(patient_id: str) -> Optional[Tuple]:
    if _cursor is None:
        return None
    try:
        _cursor.execute(
            "select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date "
            "from patient where patient_id=%s",
            (patient_id,),
        )
        return _cursor.fetchone()
    except Exception:
        return None

# Create a new top-level window with standard configurations.
def _create_window(title: str) -> ctk.CTkToplevel:
    window = ctk.CTkToplevel()
    window.grab_set()
    window.resizable(False, False)
    window.title(title)
    window.configure(fg_color=ACCENT)
    if _root is not None:
        window.transient(_root)
    return window

# Create a form container frame within a parent widget.
def _create_form_container(parent) -> ctk.CTkFrame:
    form_container = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=18)
    form_container.grid(row=0, column=0, padx=26, pady=24, sticky="nsew")
    form_container.grid_columnconfigure(0, weight=0)
    form_container.grid_columnconfigure(1, weight=1)
    return form_container

# Create Date of Birth input dropdowns for month, day, and year.
def _create_dob_inputs(parent) -> Tuple[ttk.Combobox, ttk.Combobox, ttk.Combobox]:
    dob_frame = ctk.CTkFrame(parent, fg_color="transparent")
    dob_frame.grid(row=6, column=1, padx=(0, 24), pady=8, sticky="ew")
    dob_frame.grid_columnconfigure((0, 1, 2), weight=1)

    month_entry = ttk.Combobox(dob_frame, values=_DOB_MONTHS, state="readonly", width=10)
    day_entry = ttk.Combobox(dob_frame, values=_DOB_DAYS, state="readonly", width=10)
    year_entry = ttk.Combobox(dob_frame, values=_DOB_YEARS, state="readonly", width=12)

    month_entry.grid(row=0, column=0, padx=2, pady=0, sticky="ew")
    day_entry.grid(row=0, column=1, padx=2, pady=0, sticky="ew")
    year_entry.grid(row=0, column=2, padx=2, pady=0, sticky="ew")

    month_entry.current(0)
    day_entry.current(0)
    year_entry.current(0)

    return month_entry, day_entry, year_entry

# Populate Date of Birth fields from a DOB string value.
def _populate_dob_fields(dob_value: str, month_entry, day_entry, year_entry) -> None:
    if dob_value and "/" in dob_value:
        parts = dob_value.split("/")
        if len(parts) == 3:
            month_val, day_val, year_val = parts
            month_entry.set(month_val.lstrip("0") or month_val)
            day_entry.set(day_val.lstrip("0") or day_val)
            year_entry.set(year_val)
            return
    month_entry.current(0)
    day_entry.current(0)
    year_entry.current(0)

# Collect filter criteria from the provided callback.
def _collect_filter() -> Tuple[Optional[str], Optional[str]]:
    if _get_filter is None:
        return None, None
    try:
        return _get_filter()
    except Exception:
        return None, None

# Display patient records in the table with optional filtering.
def show_patient() -> None:
    table = _patient_table
    if table is None:
        return

    for row in table.get_children():
        table.delete(row)

    filter_field, filter_term = _collect_filter()
    if filter_field not in _ALLOWED_FILTER_COLUMNS:
        filter_field = None
        filter_term = None

    rows: Iterable[Tuple] = ()
    try:
        if _fetch_patients is not None:
            rows = _fetch_patients(filter_field, filter_term) or ()
        elif _cursor is not None:
            query = (
                "select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date "
                "from patient"
            )
            params = []
            if filter_field and filter_term:
                query += f" where LOWER({filter_field}) LIKE %s"
                params.append(f"%{filter_term.lower()}%")
            query += " order by patient_id"
            _cursor.execute(query, tuple(params))
            rows = _cursor.fetchall()
    except Exception:
        rows = ()

    for index, record in enumerate(rows):
        values = ["" if value is None else str(value) for value in record]
        if len(values) > 2 and values[2]:
            mobile_value = _format_mobile(values[2])
            if mobile_value:
                values[2] = mobile_value
        table.insert("", "end", values=values, tags=("evenrow" if index % 2 == 0 else "oddrow",))

# Add a new patient record via a form window.
def add_patient() -> None:
    add_window = _create_window("Add Patient")
    form_container = _create_form_container(add_window)

    patient_id_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13), width=220)
    name_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    mobile_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13), placeholder_text="09XX XXX XXXX or +63 XXX XXX XXXX")
    email_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    address_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13), placeholder_text="St., Brgy., Municipality, Province")
    gender_var = StringVar(add_window, value=_GENDER_OPTIONS[0])
    gender_dropdown = ctk.CTkOptionMenu(form_container, values=_GENDER_OPTIONS, variable=gender_var, font=("Segoe UI", 13))

    ctk.CTkLabel(form_container, text="Patient ID", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=0, column=0, padx=(24, 16), pady=(18, 8), sticky=W
    )
    patient_id_entry.grid(row=0, column=1, padx=(0, 24), pady=(18, 8), sticky="ew")

    ctk.CTkLabel(form_container, text="Name", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=1, column=0, padx=(24, 16), pady=8, sticky=W
    )
    name_entry.grid(row=1, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Mobile No.", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=2, column=0, padx=(24, 16), pady=8, sticky=W
    )
    mobile_entry.grid(row=2, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Email", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=3, column=0, padx=(24, 16), pady=8, sticky=W
    )
    email_entry.grid(row=3, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Address", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=4, column=0, padx=(24, 16), pady=8, sticky=W
    )
    address_entry.grid(row=4, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Gender", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=5, column=0, padx=(24, 16), pady=8, sticky=W
    )
    gender_dropdown.grid(row=5, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Date of Birth", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=6, column=0, padx=(24, 16), pady=8, sticky=W
    )
    month_entry, day_entry, year_entry = _create_dob_inputs(form_container)

    ctk.CTkLabel(form_container, text="Diagnosis", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=7, column=0, padx=(24, 16), pady=8, sticky=W
    )
    diagnosis_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    diagnosis_entry.grid(row=7, column=1, padx=(0, 24), pady=8, sticky="ew")

    # Reset the form fields to their default states.
    def reset_form() -> None:
        patient_id_entry.delete(0, END)
        name_entry.delete(0, END)
        mobile_entry.delete(0, END)
        email_entry.delete(0, END)
        address_entry.delete(0, END)
        diagnosis_entry.delete(0, END)
        gender_var.set(_GENDER_OPTIONS[0])
        month_entry.current(0)
        day_entry.current(0)
        year_entry.current(0)
        patient_id_entry.focus_set()
    
    # Add the new patient record to the database.
    def add_data() -> None:
        if not _ensure_db(add_window):
            return

        patient_id_value = patient_id_entry.get().strip()
        name_value = name_entry.get().strip()
        mobile_value = mobile_entry.get().strip()
        email_value = email_entry.get().strip()
        address_value = address_entry.get().strip()
        gender_value = gender_var.get().strip()
        diagnosis_value = diagnosis_entry.get().strip()
        month_value = month_entry.get()
        day_value = day_entry.get()
        year_value = year_entry.get()

        if not patient_id_value or not patient_id_value.isdigit():
            messagebox.showerror("Error", "Patient ID should contain only numbers!", parent=add_window)
            return
        if not name_value:
            messagebox.showerror("Error", "Name is required.", parent=add_window)
            return
        if any(char.isdigit() for char in name_value):
            messagebox.showerror("Error", "Name cannot contain numbers!", parent=add_window)
            return
        if not mobile_value or not email_value or not address_value or not gender_value or not diagnosis_value:
            messagebox.showerror("Error", "All information are required!", parent=add_window)
            return
        if month_value in ("Month", "") or day_value in ("Day", "") or year_value in ("Year", ""):
            messagebox.showerror("Error", "Please complete the birth date fields.", parent=add_window)
            return

        formatted_mobile = mobile_value
        if _normalize_mobile is not None:
            normalized_mobile = _normalize_mobile(mobile_value)
            if not normalized_mobile:
                messagebox.showerror(
                    "Error",
                    "Mobile No. must follow the format +63 XXX XXX XXXX or 09XX XXX XXXX.",
                    parent=add_window,
                )
                return
            formatted_mobile = normalized_mobile

        dob_value = f"{month_value}/{day_value}/{year_value}"
        normalized_name = _format_case(name_value)
        normalized_address = _format_case(address_value)
        normalized_diagnosis = _format_case(diagnosis_value)
        visit_date = _current_visit_date()

        # Insert the new patient record into the database.
        try:
            _cursor.execute(
                (
                    "insert into patient (patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date) "
                    "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                ),
                (
                    patient_id_value,
                    normalized_name,
                    formatted_mobile,
                    email_value,
                    normalized_address,
                    gender_value,
                    dob_value,
                    normalized_diagnosis,
                    visit_date,
                ),
            )
            _connection.commit()
        except IntegrityError:
            messagebox.showerror("Error", "Patient ID already exists.", parent=add_window)
            return
        except Exception as exc:
            _connection.rollback()
            messagebox.showerror("Error", f"Failed to add patient: {exc}", parent=add_window)
            return

        messagebox.showinfo("Success", f"Patient ID {patient_id_value} added successfully!", parent=add_window)
        show_patient()
        if messagebox.askyesno("Confirm", "Clear the form for another entry?", parent=add_window):
            reset_form()
        else:
            add_window.destroy()

    ctk.CTkButton(
        form_container,
        text="Add Patient",
        command=add_data,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=14,
        font=("Segoe UI", 14, "bold"),
    ).grid(row=8, column=0, columnspan=2, padx=24, pady=(18, 10), sticky="ew")
    patient_id_entry.focus_set()

# Update an existing patient record via a form window.
def update_patient() -> None:
    table = _patient_table
    if table is None:
        return

    selections = table.selection()
    if not selections:
        messagebox.showerror("Error", "Please select a patient to update.")
        return
    if len(selections) > 1:
        messagebox.showerror("Error", "Please select only one patient to update.")
        return

    patient_item = selections[0]
    values = table.item(patient_item).get("values", [])
    if not values:
        messagebox.showerror("Error", "Unable to read the selected patient data.")
        return

    patient_id = str(values[0])
    record = _fetch_patient_by_id(patient_id)
    if record:
        record_values = ["" if value is None else str(value) for value in record]
    else:
        record_values = ["" if value is None else str(value) for value in values]
        record_values += [""] * (9 - len(record_values))

    update_window = _create_window(f"Update Patient {patient_id}")
    form_container = _create_form_container(update_window)

    patient_id_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13), width=220)
    patient_id_entry.insert(0, patient_id)
    patient_id_entry.configure(state="disabled")

    name_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    name_entry.insert(0, record_values[1])

    mobile_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13), placeholder_text="+63 000 000 0000")
    mobile_entry.insert(0, _format_mobile(record_values[2]) or record_values[2])

    email_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    email_entry.insert(0, record_values[3])

    address_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    address_entry.insert(0, record_values[4])

    gender_var = StringVar(update_window, value=record_values[5] or _GENDER_OPTIONS[0])
    gender_dropdown = ctk.CTkOptionMenu(form_container, values=_GENDER_OPTIONS, variable=gender_var, font=("Segoe UI", 13))

    ctk.CTkLabel(form_container, text="Patient ID", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=0, column=0, padx=(24, 16), pady=(18, 8), sticky=W
    )
    patient_id_entry.grid(row=0, column=1, padx=(0, 24), pady=(18, 8), sticky="ew")

    ctk.CTkLabel(form_container, text="Name", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=1, column=0, padx=(24, 16), pady=8, sticky=W
    )
    name_entry.grid(row=1, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Mobile No.", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=2, column=0, padx=(24, 16), pady=8, sticky=W
    )
    mobile_entry.grid(row=2, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Email", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=3, column=0, padx=(24, 16), pady=8, sticky=W
    )
    email_entry.grid(row=3, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Address", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=4, column=0, padx=(24, 16), pady=8, sticky=W
    )
    address_entry.grid(row=4, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Gender", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=5, column=0, padx=(24, 16), pady=8, sticky=W
    )
    gender_dropdown.grid(row=5, column=1, padx=(0, 24), pady=8, sticky="ew")

    ctk.CTkLabel(form_container, text="Date of Birth", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=6, column=0, padx=(24, 16), pady=8, sticky=W
    )
    month_entry, day_entry, year_entry = _create_dob_inputs(form_container)
    _populate_dob_fields(record_values[6], month_entry, day_entry, year_entry)

    ctk.CTkLabel(form_container, text="Diagnosis", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(
        row=7, column=0, padx=(24, 16), pady=8, sticky=W
    )
    diagnosis_entry = ctk.CTkEntry(form_container, font=("Segoe UI", 13))
    diagnosis_entry.grid(row=7, column=1, padx=(0, 24), pady=8, sticky="ew")
    diagnosis_entry.insert(0, record_values[7])

    # Persist the changes to the database.
    def persist_changes() -> None:
        if not _ensure_db(update_window):
            return

        name_value = name_entry.get().strip()
        mobile_value = mobile_entry.get().strip()
        email_value = email_entry.get().strip()
        address_value = address_entry.get().strip()
        gender_value = gender_var.get().strip()
        diagnosis_value = diagnosis_entry.get().strip()
        month_value = month_entry.get()
        day_value = day_entry.get()
        year_value = year_entry.get()

        if not name_value:
            messagebox.showerror("Error", "Name is required.", parent=update_window)
            return
        if any(char.isdigit() for char in name_value):
            messagebox.showerror("Error", "Name cannot contain numbers!", parent=update_window)
            return
        if not mobile_value or not email_value or not address_value or not gender_value or not diagnosis_value:
            messagebox.showerror("Error", "All fields are required before updating.", parent=update_window)
            return
        if month_value in ("Month", "") or day_value in ("Day", "") or year_value in ("Year", ""):
            messagebox.showerror("Error", "Please complete the birth date fields.", parent=update_window)
            return

        formatted_mobile = mobile_value
        if _normalize_mobile is not None:
            normalized_mobile = _normalize_mobile(mobile_value)
            if not normalized_mobile:
                messagebox.showerror("Error", "Enter a valid mobile number.", parent=update_window)
                return
            formatted_mobile = normalized_mobile

        dob_value = f"{month_value}/{day_value}/{year_value}"
        normalized_name = _format_case(name_value)
        normalized_address = _format_case(address_value)
        normalized_diagnosis = _format_case(diagnosis_value)
        visit_date = _current_visit_date()

        # Update the patient record in the database.
        try:
            _cursor.execute(
                (
                    "update patient set name=%s, mobile=%s, email=%s, address=%s, gender=%s, dob=%s, diagnosis=%s, visit_date=%s "
                    "where patient_id=%s"
                ),
                (
                    normalized_name,
                    formatted_mobile,
                    email_value,
                    normalized_address,
                    gender_value,
                    dob_value,
                    normalized_diagnosis,
                    visit_date,
                    patient_id,
                ),
            )
            _connection.commit()
        except Exception as exc:
            _connection.rollback()
            messagebox.showerror("Error", f"Failed to update patient: {exc}", parent=update_window)
            return

        messagebox.showinfo("Success", f"Patient ID {patient_id} updated successfully!", parent=update_window)
        update_window.destroy()
        show_patient()

    ctk.CTkButton(
        form_container,
        text="Update Patient",
        command=persist_changes,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=14,
        font=("Segoe UI", 14, "bold"),
    ).grid(row=8, column=0, columnspan=2, padx=24, pady=(18, 10), sticky="ew")

# Delete selected patient records from the database.
def delete_patient() -> None:
    table = _patient_table
    if table is None:
        return
    if not _ensure_db(_root or None):
        return

    selections = table.selection()
    if not selections:
        messagebox.showerror("Error", "Please select at least one patient to delete.")
        return

    patient_ids = []
    for item in selections:
        content = table.item(item)
        values = content.get("values", [])
        if values:
            patient_ids.append(str(values[0]))

    if not patient_ids:
        messagebox.showerror("Error", "Unable to read the selected patient data.")
        return

    if len(patient_ids) == 1:
        prompt = f"Do you want to delete patient {patient_ids[0]}?"
        title = "Delete Patient"
    else:
        prompt = f"Delete the {len(patient_ids)} selected patients? This cannot be undone."
        title = "Delete Patients"

    if not messagebox.askyesno(title, prompt):
        return

    try:
        for patient_id in patient_ids:
            _cursor.execute("delete from patient where patient_id=%s", (patient_id,))
        _connection.commit()
    except Exception as exc:
        _connection.rollback()
        messagebox.showerror("Error", f"Failed to delete selected patients: {exc}")
        return

    show_patient()
    if len(patient_ids) == 1:
        messagebox.showinfo("Deleted", f"Patient {patient_ids[0]} deleted successfully.")
    else:
        messagebox.showinfo("Deleted", f"Deleted {len(patient_ids)} patients successfully.")

# Show detailed information of the selected patient in a new window.
def show_patient_details(event=None):
    table = _patient_table
    if table is None:
        return

    selection = table.focus()
    if not selection:
        return

    content = table.item(selection)
    values = list(content.get("values", []))
    if not values:
        return

    patient_id = str(values[0])
    record = _fetch_patient_by_id(patient_id)
    if record:
        values = ["" if value is None else str(value) for value in record]

    detail_fields = [
        "Patient ID",
        "Name",
        "Mobile No.",
        "Email",
        "Address",
        "Gender",
        "Date of Birth",
        "Diagnosis",
        "Visit Date",
    ]
    display_values = values + [""] * (len(detail_fields) - len(values))

    if display_values and display_values[0] is not None:
        display_values[0] = str(display_values[0])
    if len(display_values) > 2 and display_values[2]:
        mobile_value = _format_mobile(display_values[2])
        if mobile_value:
            display_values[2] = mobile_value

    detail_window = _create_window(f"Patient {display_values[0]} Details")
    container = _create_form_container(detail_window)
    container.grid_columnconfigure(1, weight=1)

    for index, (field_name, field_value) in enumerate(zip(detail_fields, display_values)):
        ctk.CTkLabel(container, text=field_name, font=("Segoe UI", 15, "bold"), text_color=TEXT).grid(
            row=index, column=0, padx=(24, 16), pady=6, sticky=W
        )
        ctk.CTkLabel(
            container,
            text=field_value if field_value else "N/A",
            font=("Segoe UI", 13),
            text_color=TEXT,
            justify="left",
            anchor="w",
            wraplength=360,
        ).grid(row=index, column=1, padx=(0, 24), pady=6, sticky="ew")

    ctk.CTkButton(
        container,
        text="Close",
        command=detail_window.destroy,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        corner_radius=14,
        font=("Segoe UI", 13, "bold"),
    ).grid(row=len(detail_fields), column=0, columnspan=2, padx=24, pady=(12, 6), sticky="ew")


__all__ = [
    "configure",
    "show_patient",
    "add_patient",
    "update_patient",
    "delete_patient",
    "show_patient_details",
]
