from tkinter import *  # Main GUI library
import time  # Time-related functions
import os  # Operating system interfaces
from tkinter import ttk, messagebox, filedialog  # GUI widgets and dialogs
from pymysql.err import IntegrityError  # Specific database error
import pandas  # Data manipulation library
import customtkinter as ctk  # Custom themed tkinter
from PIL import ImageTk, Image  # Image handling
import importlib  # Dynamic module importing

from system_configs.config import (  # Database and UI configuration
    PRIMARY,
    SECONDARY,
    BG,
    ACCENT,
    TEXT,
    TABLE_BG,
    SIDEBAR_BG,
    HEADER_BG,
    CARD_BG,
    SIDEBAR_SIDE,
    SEARCH_FIELD_OPTIONS,
    SORT_FIELD_OPTIONS,
    SORT_FIELD_LABELS,
    DATE_SORT_FIELDS,
    SELECTION_MENU_OPTIONS,
)

from system_configs.analytics_service import compute_analytics, create_analytics_figures, load_all_patients #  Importing analytics functions
from system_configs.database import db_connection, db_cursor # Database connection and cursor
from system_configs.export_service import export_patient_analytics_pdf, export_patient_records_excel # Export functions
from system_configs.helpers import normalize_column_name, normalize_mobile, to_proper_case # Helper functions
from system_configs.import_service import import_patient_dataframe # Import function

# Initialize database connection and cursor
try:
    FPDF = importlib.import_module('fpdf').FPDF
except (ImportError, AttributeError):
    FPDF = None

# Attempt to import matplotlib for plotting
try:
    matplotlib = importlib.import_module('matplotlib')
    matplotlib.use('TkAgg')
    Figure = importlib.import_module('matplotlib.figure').Figure
    FigureCanvasTkAgg = importlib.import_module('matplotlib.backends.backend_tkagg').FigureCanvasTkAgg
except Exception:
    Figure = None
    FigureCanvasTkAgg = None
    matplotlib = None

# Check for openpyxl for Excel export
try:
    importlib.import_module('openpyxl')
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# Initialize sorting and search variables
current_sort_field = 'patient_id'
current_sort_order = 'ASC'
search_field_var = None
search_entry = None
selection_action_var = None

_normalize_mobile = normalize_mobile
_normalize_column_name = normalize_column_name
_to_proper_case = to_proper_case

# Load all patients from the database.
def _load_all_patients():
    return load_all_patients(db_cursor)

# Compute analytics data from patient records.
def _compute_analytics():
    rows = _load_all_patients()
    return compute_analytics(rows)

# Create analytics figures for PDF export.
def _create_analytics_figures(analytics):
    return create_analytics_figures(analytics, Figure, PRIMARY, SECONDARY)


# Present export options for staff to download records or analytics.
def Export_data():
    export_window = ctk.CTkToplevel()
    export_window.title('Export Options')
    export_window.grab_set()
    export_window.resizable(False, False)
    export_window.configure(fg_color=ACCENT)
    export_window.transient(root)

    container = ctk.CTkFrame(export_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24)
    container.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(container, text='Choose what to export', font=('Segoe UI', 16, 'bold'), text_color=TEXT).grid(
        row=0, column=0, padx=12, pady=(6, 12), sticky='ew'
    )

    choice_var = ctk.StringVar(value='records')

    records_radio = ctk.CTkRadioButton(
        container, text='Patient Records (Excel)', value='records', variable=choice_var,
        font=('Segoe UI', 13), text_color=TEXT
    )
    records_radio.grid(row=1, column=0, padx=12, pady=4, sticky='w')

    analytics_radio = ctk.CTkRadioButton(
        container, text='Patient Analytics (PDF)', value='analytics', variable=choice_var,
        font=('Segoe UI', 13), text_color=TEXT
    )
    analytics_radio.grid(row=2, column=0, padx=12, pady=4, sticky='w')

    button_row = ctk.CTkFrame(container, fg_color='transparent')
    button_row.grid(row=3, column=0, padx=12, pady=(18, 4), sticky='ew')
    button_row.grid_columnconfigure((0, 1), weight=1)

    # Handle the selected export action and persist files as needed.
    def _perform_export():
        selection = choice_var.get()
        export_window.destroy()

        if selection == 'records':
            if not HAS_OPENPYXL:
                messagebox.showerror(
                    'Missing Dependency',
                    'Excel export requires the "openpyxl" package. Install it with "pip install openpyxl" and try again.'
                )
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel Files', '*.xlsx')]
            )
            if not file_path:
                return
            try:
                export_patient_records_excel(db_cursor, file_path)
            except ValueError as exc:
                messagebox.showinfo('Export', str(exc))
            except Exception as exc:
                messagebox.showerror('Error', f'Failed to export Excel file: {exc}')
            else:
                messagebox.showinfo('Success', f'Export completed: {file_path}')
        else:
            if FPDF is None:
                messagebox.showerror(
                    'Missing Dependency',
                    'Analytics export to PDF requires the "fpdf" package. Install it with "pip install fpdf" and try again.'
                )
                return
            if Figure is None:
                messagebox.showerror(
                    'Missing Dependency',
                    'Analytics export to PDF requires the "matplotlib" package. Install it with "pip install matplotlib" and try again.'
                )
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension='.pdf',
                filetypes=[('PDF Files', '*.pdf')]
            )
            if not file_path:
                return
            try:
                export_patient_analytics_pdf(db_cursor, file_path, FPDF, Figure, PRIMARY, SECONDARY)
            except ValueError as exc:
                messagebox.showinfo('Export', str(exc))
            except Exception as exc:
                messagebox.showerror('Error', f'Failed to export PDF: {exc}')
            else:
                messagebox.showinfo('Success', f'Export completed: {file_path}')

    export_button = ctk.CTkButton(
        button_row, text='Export', command=_perform_export, fg_color=SECONDARY,
        hover_color=PRIMARY, corner_radius=12, font=('Segoe UI', 13, 'bold')
    )
    export_button.grid(row=0, column=0, padx=(0, 6), sticky='ew')

    cancel_button = ctk.CTkButton(
        button_row, text='Cancel', command=export_window.destroy, fg_color='#95A5A6',
        hover_color='#7F8C8D', corner_radius=12, font=('Segoe UI', 13, 'bold')
    )
    cancel_button.grid(row=0, column=1, padx=(6, 0), sticky='ew')


# Populate the treeview widget with normalized patient data.
def _populate_table(rows):
    """Refresh treeview content and apply alternating row colors."""
    patient_table.delete(*patient_table.get_children())
    for index, row in enumerate(rows):
        row_values = list(row)
        if len(row_values) > 1:
            row_values[1] = _to_proper_case(row_values[1])
        if len(row_values) > 4:
            row_values[4] = _to_proper_case(row_values[4])
        if len(row_values) > 7:
            row_values[7] = _to_proper_case(row_values[7])
        if len(row_values) > 2:
            formatted_mobile = _normalize_mobile(row_values[2])
            if formatted_mobile:
                row_values[2] = formatted_mobile
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        patient_table.insert('', END, values=row_values, tags=(tag,))


    # Retrieve patient rows honoring current filters and sort preferences.
def _fetch_patients(filter_field=None, filter_term=None):
    global current_sort_field, current_sort_order
    sort_field = current_sort_field if current_sort_field in SORT_FIELD_OPTIONS.values() else 'patient_id'
    sort_order = current_sort_order if current_sort_order in ('ASC', 'DESC') else 'ASC'

    query = (
        'select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date '
        'from patient'
    )
    params = []

    if filter_field and filter_term:
        query += f' where LOWER({filter_field}) LIKE %s'
        params.append(f"%{filter_term.lower()}%")

    if sort_field == 'patient_id':
        numeric_expr = "CASE WHEN patient_id REGEXP '^[0-9]+$' THEN CAST(patient_id AS UNSIGNED) ELSE NULL END"
        query += (
            f" order by ({numeric_expr} IS NULL) ASC, "
            f"{numeric_expr} {sort_order}, patient_id {sort_order}"
        )
    elif sort_field in DATE_SORT_FIELDS:
        query += f' order by STR_TO_DATE({sort_field}, "%m/%d/%Y") {sort_order}'
    else:
        query += f' order by {sort_field} {sort_order}'

    mycursor.execute(query, tuple(params))
    return mycursor.fetchall()


# Allow mouse wheel scrolling for readonly comboboxes.
def _bind_combobox_scroll(combobox, options):
    # Adjust readonly combobox selection when user scrolls.
    def _on_mousewheel(event):
        if not options:
            return 'break'

        current_value = combobox.get()
        try:
            index = options.index(current_value)
        except ValueError:
            index = 0

        step = -1 if event.delta > 0 else 1
        new_index = max(0, min(len(options) - 1, index + step))
        combobox.set(options[new_index])
        return 'break'

    combobox.bind('<MouseWheel>', _on_mousewheel)


# Present the update dialog for editing patient information.
def Update_patient():
    selected_items = patient_table.selection()
    if not selected_items:
        messagebox.showerror('Error', 'Please select a patient to update.')
        return

    if len(selected_items) > 1:
        messagebox.showerror(
            'Error',
            'Update Patient is available only when a single patient is selected. Please adjust your selection.'
        )
        return

    selection = selected_items[0]

    content = patient_table.item(selection)
    list_data = content.get('values', [])
    if not list_data:
        messagebox.showerror('Error', 'Unable to read the selected patient data.')
        return

    patient_id = str(list_data[0])

    # Fetch existing patient data from the database.
    try:
        mycursor.execute(
            'select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date '
            'from patient where patient_id=%s', (patient_id,)
        )
        record = mycursor.fetchone()
        if record:
            list_data = ['' if value is None else str(value) for value in record]
            patient_id = list_data[0]
    except Exception:
        record = None

    update_window = ctk.CTkToplevel()
    update_window.title('Update Patient')
    update_window.grab_set()
    update_window.resizable(False, False)
    update_window.configure(fg_color=ACCENT)

    form_container = ctk.CTkFrame(update_window, fg_color=CARD_BG, corner_radius=18)
    form_container.grid(row=0, column=0, padx=26, pady=24)
    form_container.grid_columnconfigure(0, weight=0)
    form_container.grid_columnconfigure(1, weight=1)

    patientIdLabel = ctk.CTkLabel(form_container, text='Patient ID', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    patientIdLabel.grid(row=0, column=0, padx=(24, 16), pady=(18, 8), sticky=W)
    patientIdEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13), state='disabled')
    patientIdEntry.grid(row=0, column=1, padx=(0, 24), pady=(18, 8), sticky='ew')

    nameLabel = ctk.CTkLabel(form_container, text='Name', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    nameLabel.grid(row=1, column=0, padx=(24, 16), pady=8, sticky=W)
    nameEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    nameEntry.grid(row=1, column=1, padx=(0, 24), pady=8, sticky='ew')

    mobileLabel = ctk.CTkLabel(form_container, text='Mobile No.', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    mobileLabel.grid(row=2, column=0, padx=(24, 16), pady=8, sticky=W)
    mobileEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13), placeholder_text='+63 000 000 0000')
    mobileEntry.grid(row=2, column=1, padx=(0, 24), pady=8, sticky='ew')

    emailLabel = ctk.CTkLabel(form_container, text='Email', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    emailLabel.grid(row=3, column=0, padx=(24, 16), pady=8, sticky=W)
    emaileEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    emaileEntry.grid(row=3, column=1, padx=(0, 24), pady=8, sticky='ew')

    addressLabel = ctk.CTkLabel(form_container, text='Street Address', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    addressLabel.grid(row=4, column=0, padx=(24, 16), pady=8, sticky=W)
    addressEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    addressEntry.grid(row=4, column=1, padx=(0, 24), pady=8, sticky='ew')

    barangayLabel = ctk.CTkLabel(form_container, text='Barangay', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    barangayLabel.grid(row=5, column=0, padx=(24, 16), pady=8, sticky=W)
    barangayEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    barangayEntry.grid(row=5, column=1, padx=(0, 24), pady=8, sticky='ew')

    municipalityLabel = ctk.CTkLabel(form_container, text='Municipality', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    municipalityLabel.grid(row=6, column=0, padx=(24, 16), pady=8, sticky=W)
    municipalityEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    municipalityEntry.grid(row=6, column=1, padx=(0, 24), pady=8, sticky='ew')

    provinceLabel = ctk.CTkLabel(form_container, text='Province', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    provinceLabel.grid(row=7, column=0, padx=(24, 16), pady=8, sticky=W)
    provinceEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    provinceEntry.grid(row=7, column=1, padx=(0, 24), pady=8, sticky='ew')

    genderLabel = ctk.CTkLabel(form_container, text='Gender', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    genderLabel.grid(row=8, column=0, padx=(24, 16), pady=8, sticky=W)
    genderOptions = ['Male', 'Female', 'Other']
    genderVar = StringVar(update_window)
    genderDropdown = ctk.CTkOptionMenu(form_container, values=genderOptions, variable=genderVar, font=('Segoe UI', 13))
    genderDropdown.grid(row=8, column=1, padx=(0, 24), pady=8, sticky='ew')

    bdayLabel = ctk.CTkLabel(form_container, text='Date of Birth', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    bdayLabel.grid(row=9, column=0, padx=(24, 16), pady=8, sticky=W)

    months = ['Month'] + [str(i) for i in range(1, 13)]
    dates = ['Day'] + [str(i) for i in range(1, 32)]
    years = ['Year'] + [str(i) for i in range(1990, 2031)]

    dob_frame = ctk.CTkFrame(form_container, fg_color='transparent')
    dob_frame.grid(row=9, column=1, padx=(0, 24), pady=8, sticky='ew')
    dob_frame.grid_columnconfigure((0, 1, 2), weight=1)

    bdayMonthEntry = ttk.Combobox(dob_frame, values=months, state='readonly', width=10)
    bdayMonthEntry.grid(row=0, column=0, padx=2, pady=0, sticky='ew')
    bdayMonthEntry.current(0)
    _bind_combobox_scroll(bdayMonthEntry, months)

    bdayDateEntry = ttk.Combobox(dob_frame, values=dates, state='readonly', width=10)
    bdayDateEntry.grid(row=0, column=1, padx=2, pady=0, sticky='ew')
    bdayDateEntry.current(0)
    _bind_combobox_scroll(bdayDateEntry, dates)

    bdayYearEntry = ttk.Combobox(dob_frame, values=years, state='readonly', width=12)
    bdayYearEntry.grid(row=0, column=2, padx=2, pady=0, sticky='ew')
    bdayYearEntry.current(0)
    _bind_combobox_scroll(bdayYearEntry, years)

    diagnosisLabel = ctk.CTkLabel(form_container, text='Diagnosis', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    diagnosisLabel.grid(row=10, column=0, padx=(24, 16), pady=8, sticky=W)
    diagnosisEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    diagnosisEntry.grid(row=10, column=1, padx=(0, 24), pady=8, sticky='ew')

    # Persist edits for the selected patient after validation.
    def Update_data():
        if bdayMonthEntry.get() in ('Month', '') or bdayDateEntry.get() in ('Day', '') or bdayYearEntry.get() in ('Year', ''):
            messagebox.showerror('Error', 'Please complete the birth date fields.', parent=update_window)
            return

        required_fields = [
            nameEntry.get().strip(), mobileEntry.get().strip(), emaileEntry.get().strip(), addressEntry.get().strip(),
            barangayEntry.get().strip(), municipalityEntry.get().strip(), provinceEntry.get().strip(), genderVar.get().strip(),
            diagnosisEntry.get().strip()
        ]
        if any(not value for value in required_fields):
            messagebox.showerror('Error', 'All fields are required before updating.', parent=update_window)
            return

        mobile_number = mobileEntry.get().strip()
        formatted_mobile = _normalize_mobile(mobile_number)
        if not formatted_mobile:
            messagebox.showerror('Error', 'Enter a valid mobile number.', parent=update_window)
            return

        name_value = _to_proper_case(nameEntry.get())
        address_parts = [addressEntry.get(), barangayEntry.get(), municipalityEntry.get(), provinceEntry.get()]
        combined_address = ', '.join(_to_proper_case(part) for part in address_parts)
        diagnosis_value = _to_proper_case(diagnosisEntry.get())
        combined_date = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"
        query = (
            'update patient set name=%s, mobile=%s, email=%s, address=%s, gender=%s, dob=%s, diagnosis=%s, visit_date=%s '
            'where patient_id=%s'
        )
        mycursor.execute(query, (
            name_value, formatted_mobile, emaileEntry.get(), combined_address, genderVar.get(), combined_date,
            diagnosis_value, date, patient_id
        ))
        con.commit()
        messagebox.showinfo('Success', f'Patient ID {patient_id} updated successfully!', parent=update_window)
        update_window.destroy()
        Show_patient()

    update_stud_button = ctk.CTkButton(form_container, text='Update Patient', command=Update_data, fg_color=SECONDARY,
                                       hover_color=PRIMARY, corner_radius=14, font=('Segoe UI', 14, 'bold'))
    update_stud_button.grid(row=11, column=0, columnspan=2, padx=24, pady=(18, 10), sticky='ew')

    patientIdEntry.configure(state='normal')
    patientIdEntry.insert(0, patient_id)
    patientIdEntry.configure(state='disabled')
    if len(list_data) > 1:
        nameEntry.insert(0, list_data[1])
    if len(list_data) > 2:
        formatted_mobile = _normalize_mobile(list_data[2])
        mobileEntry.insert(0, formatted_mobile if formatted_mobile else list_data[2])
    if len(list_data) > 3:
        emaileEntry.insert(0, list_data[3])

    stored_address = list_data[4] if len(list_data) > 4 else ''
    if stored_address:
        parts = [p.strip() for p in stored_address.split(',')]
        if len(parts) >= 1:
            addressEntry.insert(0, parts[0])
        if len(parts) >= 2:
            barangayEntry.insert(0, parts[1])
        if len(parts) >= 3:
            municipalityEntry.insert(0, parts[2])
        if len(parts) >= 4:
            provinceEntry.insert(0, parts[3])

    if len(list_data) > 5 and list_data[5]:
        genderVar.set(list_data[5])
    else:
        genderVar.set(genderOptions[0])

    existing_dob = list_data[6] if len(list_data) > 6 else ''
    if existing_dob and '/' in existing_dob:
        month, day, year = existing_dob.split('/')
        month_value = month.lstrip('0') or month
        day_value = day.lstrip('0') or day
        if month_value not in months:
            month_value = months[0]
        if day_value not in dates:
            day_value = dates[0]
        if year not in years:
            year = years[0]
        bdayMonthEntry.set(month_value)
        bdayDateEntry.set(day_value)
        bdayYearEntry.set(year)

    if len(list_data) > 7:
        diagnosisEntry.insert(0, list_data[7])


    # Refresh the table view using current filters and sort state.
def Show_patient():
    filter_field = None
    filter_term = None

    global search_entry, search_field_var
    if search_entry is not None and search_field_var is not None:
        try:
            term = search_entry.get().strip()
        except Exception:
            term = ''
        if term:
            selected_label = search_field_var.get() if hasattr(search_field_var, 'get') else 'Patient ID'
            filter_field = SEARCH_FIELD_OPTIONS.get(selected_label, 'patient_id')
            filter_term = term

    fetched_data = _fetch_patients(filter_field, filter_term)
    _populate_table(fetched_data)


# Highlight every patient row in the table for batch actions.
def Select_all_patients():
    items = patient_table.get_children()
    if not items:
        messagebox.showinfo('Select All', 'No patient records available to select.')
        return

    patient_table.selection_set(items)
    patient_table.focus(items[0])
    patient_table.see(items[0])


# Clear any current selection in the patient table widget.
def Clear_selected_patients():
    selections = patient_table.selection()
    if not selections:
        if patient_table.get_children():
            messagebox.showinfo('Selection', 'No patients are currently selected.')
        else:
            messagebox.showinfo('Selection', 'No patient records available.')
        return
    patient_table.selection_remove(selections)


# Let staff choose specific patient rows via a modal list.
def Select_specific_patients():
    items = patient_table.get_children()
    if not items:
        messagebox.showinfo('Select Patients', 'No patient records available to select.')
        return

    records = []
    for item in items:
        values = patient_table.item(item).get('values', [])
        if not values:
            continue
        patient_id = str(values[0])
        name = str(values[1]) if len(values) > 1 else ''
        records.append((item, patient_id, name))

    if not records:
        messagebox.showinfo('Select Patients', 'No patient records available to select.')
        return

    selection_window = ctk.CTkToplevel()
    selection_window.title('Select Patients')
    selection_window.grab_set()
    selection_window.resizable(False, False)
    selection_window.configure(fg_color=ACCENT)
    selection_window.transient(root)
    selection_window.geometry('620x580')
    selection_window.grid_rowconfigure(0, weight=1)
    selection_window.grid_columnconfigure(0, weight=1)

    container = ctk.CTkFrame(selection_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24, sticky='nsew')
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(container, text='Select Patients', font=('Segoe UI', 18, 'bold'), text_color=TEXT).grid(
        row=0, column=0, padx=12, pady=(6, 10), sticky='ew'
    )

    list_frame = ctk.CTkFrame(container, fg_color='transparent')
    list_frame.grid(row=1, column=0, sticky='nsew')
    list_frame.grid_columnconfigure(0, weight=1)
    list_frame.grid_rowconfigure(0, weight=1)

    scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL)
    scrollbar.grid(row=0, column=1, sticky='ns')

    listbox = Listbox(
        list_frame,
        selectmode=MULTIPLE,
        exportselection=False,
        width=52,
        height=18,
        font=('Segoe UI', 13)
    )
    listbox.grid(row=0, column=0, sticky='nsew')
    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    for record in records:
        item_id, patient_id, name = record
        display = f'{patient_id} - {name}' if name else patient_id
        listbox.insert(END, display)

    button_row = ctk.CTkFrame(container, fg_color='transparent')
    button_row.grid(row=2, column=0, padx=12, pady=(16, 4), sticky='ew')
    button_row.grid_columnconfigure((0, 1), weight=1)

    # Write the chosen records back to the main tree selection.
    def _apply_selection():
        selections = listbox.curselection()
        if not selections:
            messagebox.showerror('Selection', 'Please choose at least one patient.', parent=selection_window)
            return
        selected_items = [records[index][0] for index in selections]
        patient_table.selection_set(selected_items)
        patient_table.focus(selected_items[0])
        patient_table.see(selected_items[0])
        selection_window.destroy()

    apply_button = ctk.CTkButton(button_row, text='Apply', command=_apply_selection, fg_color=SECONDARY,
                                 hover_color=PRIMARY, corner_radius=12, font=('Segoe UI', 13, 'bold'))
    apply_button.grid(row=0, column=0, padx=(0, 6), sticky='ew')

    cancel_button = ctk.CTkButton(button_row, text='Cancel', command=selection_window.destroy, fg_color='#95A5A6',
                                  hover_color='#7F8C8D', corner_radius=12, font=('Segoe UI', 13, 'bold'))
    cancel_button.grid(row=0, column=1, padx=(6, 0), sticky='ew')


# Dispatch sidebar selection actions to the appropriate handler.
def _on_selection_action(choice):
    if choice == SELECTION_MENU_OPTIONS[0]:
        return

    if choice == 'Select Specific Patients':
        Select_specific_patients()
    elif choice == 'Select All Patients':
        Select_all_patients()
    elif choice == 'Clear Selection':
        Clear_selected_patients()

    if selection_action_var is not None:
        selection_action_var.set(SELECTION_MENU_OPTIONS[0])


# Remove selected patient records after confirmation.
def Delete_patient():
    selections = patient_table.selection()
    if not selections:
        messagebox.showerror('Error', 'Please select at least one patient to delete.')
        return

    patient_ids = []
    for item in selections:
        content = patient_table.item(item)
        values = content.get('values', [])
        if not values:
            continue
        patient_ids.append(str(values[0]))

    if not patient_ids:
        messagebox.showerror('Error', 'Unable to read the selected patient data.')
        return

    if len(patient_ids) == 1:
        prompt = f'Do you want to delete patient {patient_ids[0]}?'
        title = 'Delete Patient'
    else:
        prompt = f'Delete the {len(patient_ids)} selected patients? This cannot be undone.'
        title = 'Delete Patients'

    confirm = messagebox.askyesno(title, prompt)
    if not confirm:
        return

    try:
        for patient_id in patient_ids:
            mycursor.execute('delete from patient where patient_id=%s', (patient_id,))
        con.commit()
    except Exception as exc:
        con.rollback()
        messagebox.showerror('Error', f'Failed to delete selected patients: {exc}')
        return

    Show_patient()
    if len(patient_ids) == 1:
        messagebox.showinfo('Deleted', f'Patient {patient_ids[0]} deleted successfully.')
    else:
        messagebox.showinfo('Deleted', f'Deleted {len(patient_ids)} patients successfully.')


# Display the analytics dashboard with charts and summaries.
def Show_analytics_window():
    analytics = _compute_analytics()

    if analytics['total'] == 0:
        messagebox.showinfo('Patient Analytics', 'No patient records available to analyze yet.')
        return

    if Figure is None or FigureCanvasTkAgg is None:
        messagebox.showerror(
            'Missing Dependency',
            'Analytics charts require the "matplotlib" package. Install it with "pip install matplotlib" and try again.'
        )
        return

    analytics_window = ctk.CTkToplevel()
    analytics_window.title('Patient Analytics')
    analytics_window.grab_set()
    analytics_window.configure(fg_color=ACCENT)
    analytics_window.transient(root)
    analytics_window.resizable(True, True)
    analytics_window.grid_rowconfigure(0, weight=1)
    analytics_window.grid_columnconfigure(0, weight=1)

    screen_w = analytics_window.winfo_screenwidth()
    screen_h = analytics_window.winfo_screenheight()
    min_width = min(960, screen_w)
    min_height = min(700, screen_h)
    win_w = min(max(int(screen_w * 0.75), min_width), screen_w)
    win_h = min(max(int(screen_h * 0.75), min_height), screen_h)
    pos_x = max((screen_w - win_w) // 2, 0)
    pos_y = max((screen_h - win_h) // 2, 0)
    analytics_window.geometry(f'{win_w}x{win_h}+{pos_x}+{pos_y}')
    analytics_window.minsize(min_width, min_height)

    container = ctk.CTkFrame(analytics_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24, sticky='nsew')
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(2, weight=1)

    def _make_canvas_responsive(target_frame, fig, canvas):
        """Resize matplotlib canvases when their parent frames change size."""

        def _on_resize(event):
            if event.width <= 1 or event.height <= 1:
                return
            dpi = fig.dpi or 100
            fig.set_size_inches(max(event.width / dpi, 1), max(event.height / dpi, 1))
            canvas.draw_idle()

        target_frame.bind('<Configure>', _on_resize)

    ctk.CTkLabel(container, text='Patient Analytics Overview', font=('Segoe UI', 18, 'bold'), text_color=TEXT).grid(
        row=0, column=0, padx=18, pady=(10, 6), sticky='ew'
    )

    summary_frame = ctk.CTkFrame(container, fg_color='transparent')
    summary_frame.grid(row=1, column=0, padx=18, pady=(4, 10), sticky='ew')
    summary_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        summary_frame,
        text=f"Total Patients: {analytics['total']}",
        font=('Segoe UI', 14, 'bold'),
        text_color=TEXT
    ).grid(row=0, column=0, sticky='w')

    ctk.CTkLabel(
        summary_frame,
        text=f"Most Recent Visit: {analytics['latest_visit']}",
        font=('Segoe UI', 13),
        text_color=TEXT
    ).grid(row=1, column=0, pady=(2, 0), sticky='w')

    chart_frame = ctk.CTkFrame(container, fg_color='transparent')
    chart_frame.grid(row=2, column=0, padx=18, pady=(4, 10), sticky='nsew')
    chart_frame.grid_columnconfigure((0, 1), weight=1)
    chart_frame.grid_rowconfigure((0, 1), weight=1)

    pie_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    pie_frame.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky='nsew')
    bar_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    bar_frame.grid(row=0, column=1, padx=(8, 0), pady=(0, 8), sticky='nsew')
    municipality_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    municipality_frame.grid(row=1, column=0, padx=(0, 8), pady=(8, 0), sticky='nsew')
    line_frame = ctk.CTkFrame(chart_frame, fg_color=CARD_BG, corner_radius=16)
    line_frame.grid(row=1, column=1, padx=(8, 0), pady=(8, 0), sticky='nsew')

    chart_canvases = []
    figures = _create_analytics_figures(analytics)

    chart_specs = [
        ('gender', 'No gender data available.', pie_frame),
        ('diagnosis', 'No diagnosis data available.', bar_frame),
        ('municipality', 'No municipality data available.', municipality_frame),
        ('visits', 'No visit history available.', line_frame)
    ]

    for key, empty_text, frame in chart_specs:
        fig = figures.get(key)
        if fig is None:
            ctk.CTkLabel(frame, text=empty_text, font=('Segoe UI', 12), text_color=TEXT).pack(
                expand=True, padx=18, pady=18
            )
            continue

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        chart_canvases.append(canvas)
        _make_canvas_responsive(frame, fig, canvas)

    analytics_window._chart_canvases = chart_canvases  # keep references

    close_button = ctk.CTkButton(
        container, text='Close', command=analytics_window.destroy, fg_color=SECONDARY,
        hover_color=PRIMARY, corner_radius=14, font=('Segoe UI', 13, 'bold')
    )
    close_button.grid(row=3, column=0, padx=18, pady=(6, 4), sticky='ew')

# Show detailed information for the selected patient.
def Show_patient_details(event=None):
    selection = patient_table.focus()
    if not selection:
        return

    content = patient_table.item(selection)
    values = list(content.get('values', []))
    if not values:
        return

    patient_id = str(values[0]) if values else ''

    if patient_id:
        try:
            mycursor.execute(
                'select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date '
                'from patient where patient_id=%s', (patient_id,)
            )
            record = mycursor.fetchone()
            if record:
                values = ['' if value is None else str(value) for value in record]
        except Exception:
            pass

    detail_fields = ['Patient ID', 'Name', 'Mobile No.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Visit Date']
    display_values = list(values) + [''] * (len(detail_fields) - len(values))

    if display_values:
        display_values[0] = str(display_values[0])
    if len(display_values) > 2 and display_values[2]:
        formatted_mobile = _normalize_mobile(display_values[2])
        if formatted_mobile:
            display_values[2] = formatted_mobile

    detail_window = ctk.CTkToplevel()
    detail_window.title(f'Patient {display_values[0]} Details')
    detail_window.grab_set()
    detail_window.resizable(False, False)
    detail_window.configure(fg_color=ACCENT)
    detail_window.transient(root)

    container = ctk.CTkFrame(detail_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24)
    container.grid_columnconfigure(1, weight=1)

    for index, (field_name, field_value) in enumerate(zip(detail_fields, display_values)):
        label = ctk.CTkLabel(container, text=field_name, font=('Segoe UI', 15, 'bold'), text_color=TEXT)
        label.grid(row=index, column=0, padx=(24, 16), pady=6, sticky=W)
        value_label = ctk.CTkLabel(
            container,
            text=field_value if field_value else 'N/A',
            font=('Segoe UI', 13),
            text_color=TEXT,
            justify='left',
            anchor='w',
            wraplength=360
        )
        value_label.grid(row=index, column=1, padx=(0, 24), pady=6, sticky='ew')

    close_button = ctk.CTkButton(container, text='Close', command=detail_window.destroy, fg_color=SECONDARY,
                                 hover_color=PRIMARY, corner_radius=14, font=('Segoe UI', 13, 'bold'))
    close_button.grid(row=len(detail_fields), column=0, columnspan=2, padx=24, pady=(12, 6), sticky='ew')


# Debounce search entry changes and refresh the table.
def _on_search_entry_change(event=None):
    Show_patient()


# Update which column search queries target.
def _on_search_field_change(choice):
    Show_patient()


# Present sorting options so users can reorder patient rows.
def open_sort_dialog():
    sort_window = ctk.CTkToplevel()
    sort_window.title('Sort Patients')
    sort_window.grab_set()
    sort_window.resizable(False, False)
    sort_window.configure(fg_color=ACCENT)
    sort_window.transient(root)

    container = ctk.CTkFrame(sort_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24)
    container.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(container, text='Sort By', font=('Segoe UI', 16, 'bold'), text_color=TEXT).grid(
        row=0, column=0, padx=12, pady=(6, 8), sticky='ew'
    )

    field_var = ctk.StringVar(value=SORT_FIELD_LABELS.get(current_sort_field, 'Patient ID'))
    field_menu = ctk.CTkOptionMenu(container, values=list(SORT_FIELD_OPTIONS.keys()), variable=field_var,
                                   font=('Segoe UI', 13), fg_color=SECONDARY, button_color=SECONDARY,
                                   button_hover_color=PRIMARY)
    field_menu.grid(row=1, column=0, padx=12, pady=(0, 10), sticky='ew')

    ctk.CTkLabel(container, text='Order', font=('Segoe UI', 16, 'bold'), text_color=TEXT).grid(
        row=2, column=0, padx=12, pady=(12, 8), sticky='ew'
    )

    order_var = ctk.StringVar(value='Ascending' if current_sort_order == 'ASC' else 'Descending')
    order_menu = ctk.CTkOptionMenu(container, values=['Ascending', 'Descending'], variable=order_var,
                                   font=('Segoe UI', 13), fg_color=SECONDARY, button_color=SECONDARY,
                                   button_hover_color=PRIMARY)
    order_menu.grid(row=3, column=0, padx=12, pady=(0, 16), sticky='ew')

    button_frame = ctk.CTkFrame(container, fg_color='transparent')
    button_frame.grid(row=4, column=0, padx=12, pady=(6, 0), sticky='ew')
    button_frame.grid_columnconfigure((0, 1), weight=1)

    # Apply the picked sort field and order, then refresh the table.
    def apply_sort():
        global current_sort_field, current_sort_order
        current_sort_field = SORT_FIELD_OPTIONS.get(field_var.get(), 'patient_id')
        current_sort_order = 'ASC' if order_var.get() == 'Ascending' else 'DESC'
        sort_window.destroy()
        Show_patient()

    apply_button = ctk.CTkButton(button_frame, text='Apply', command=apply_sort, fg_color=SECONDARY,
                                 hover_color=PRIMARY, corner_radius=12, font=('Segoe UI', 13, 'bold'))
    apply_button.grid(row=0, column=0, padx=(0, 6), pady=4, sticky='ew')

    cancel_button = ctk.CTkButton(button_frame, text='Cancel', command=sort_window.destroy, fg_color='#95A5A6',
                                  hover_color='#7F8C8D', corner_radius=12, font=('Segoe UI', 13, 'bold'))
    cancel_button.grid(row=0, column=1, padx=(6, 0), pady=4, sticky='ew')


# Import patient information from spreadsheet or CSV sources.
def Import_data():
    filepath = filedialog.askopenfilename(
        title='Import Patient Data',
        filetypes=[('Excel Files', '*.xlsx;*.xlsm;*.xltx;*.xltm'), ('CSV Files', '*.csv'), ('All Files', '*.*')]
    )
    if not filepath:
        return

    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    try:
        if ext in ('.xlsx', '.xlsm', '.xltx', '.xltm'):
            if not HAS_OPENPYXL:
                messagebox.showerror(
                    'Missing Dependency',
                    'Excel import requires the "openpyxl" package. Install it with "pip install openpyxl" and try again.'
                )
                return
            data_frame = pandas.read_excel(filepath, dtype=str)
        else:
            data_frame = pandas.read_csv(filepath, dtype=str)
    except Exception as exc:
        messagebox.showerror('Error', f'Unable to read the selected file: {exc}')
        return

    if data_frame.empty:
        messagebox.showinfo('Import', 'The selected file does not contain any records.')
        return

    normalized_to_original = {
        _normalize_column_name(col): col for col in data_frame.columns
    }
# Open a modal showing detailed data for the double-clicked patient.

    required_columns = {
        'patient_id': 'patientid',
        'name': 'name',
        'mobile': 'mobileno',
        'email': 'email',
        'address': 'address',
        'gender': 'gender',
        'dob': 'dateofbirth',
        'diagnosis': 'diagnosis',
        'visit_date': 'visitdate'
    }

    resolved_columns = {}
    missing_fields = []
    for field, normalized in required_columns.items():
        if normalized in normalized_to_original:
            resolved_columns[field] = normalized_to_original[normalized]
        else:
            missing_fields.append(field)

    if missing_fields:
        pretty_missing = ', '.join(field.replace('_', ' ').title() for field in missing_fields)
        messagebox.showerror('Error', f'Missing required columns in file: {pretty_missing}')
        return

    # Safely read a field from the current row with fallback handling.
    def get_value(row, field):
        value = row[resolved_columns[field]]
        if pandas.isna(value):
            return ''
        return str(value).strip()

    inserted = 0
    skipped = 0
    error_samples = []
    field_labels = {
        'patient_id': 'patient ID',
        'name': 'name',
        'mobile': 'mobile number',
        'email': 'email',
        'address': 'address',
        'gender': 'gender',
        'dob': 'date of birth',
        'diagnosis': 'diagnosis',
        'visit_date': 'visit date'
    }

    for idx, row in data_frame.iterrows():
        excel_row = idx + 2  # account for header row
        patient_id = get_value(row, 'patient_id')
        name = get_value(row, 'name')
        mobile = get_value(row, 'mobile')
        email_value = get_value(row, 'email')
        address_value = get_value(row, 'address')
        gender_value = get_value(row, 'gender')
        dob_value = get_value(row, 'dob')
        diagnosis_value = get_value(row, 'diagnosis')
        visit_date_value = get_value(row, 'visit_date')

        required_values = {
            'patient_id': patient_id,
            'name': name,
            'mobile': mobile,
            'email': email_value,
            'address': address_value,
            'gender': gender_value,
            'dob': dob_value,
            'diagnosis': diagnosis_value,
            'visit_date': visit_date_value
        }

        missing_values = [field_labels[key] for key, value in required_values.items() if not value]
        if missing_values:
            skipped += 1
            if len(error_samples) < 5:
                missing_text = ', '.join(missing_values)
                error_samples.append(f'Row {excel_row}: Missing {missing_text}.')
            continue

        formatted_mobile = _normalize_mobile(mobile)
        if not formatted_mobile:
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f'Row {excel_row}: Mobile number must follow +63 000 000 0000 format.')
            continue

        name = _to_proper_case(name)
        address_value = _to_proper_case(address_value)
        diagnosis_value = _to_proper_case(diagnosis_value)

        try:
            query = (
                'insert into patient ('
                'patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date'
                ') values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            )
            mycursor.execute(query, (
                patient_id, name, formatted_mobile, email_value, address_value, gender_value,
                dob_value, diagnosis_value, visit_date_value
            ))
            con.commit()
            inserted += 1
        except IntegrityError:
            con.rollback()
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f'Row {excel_row}: Patient ID already exists.')
        except Exception as exc:
            con.rollback()
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f'Row {excel_row}: {exc}')

    Show_patient()

    summary_message = f'Imported {inserted} record(s).'
    if skipped:
        summary_message += f'\nSkipped {skipped} record(s).'
    if error_samples:
        summary_message += '\n\nSample issues:\n' + '\n'.join(error_samples)

    messagebox.showinfo('Import Complete', summary_message)


# Show the add-patient form and handle new record submissions.
def Add_patient():
    # Validate the current form inputs before inserting a patient.
    def add_data():
        # Detect whether the supplied string includes numeric characters.
        def contains_digits(string):
            return any(char.isdigit() for char in string)
        # Detect whether the supplied string includes characters other than digits or dashes.
        def contains_non_digit(string):
            return any(not char.isdigit() and char != "-" for char in string)

        dob_combined = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"
        mobile_input = mobileEntry.get().strip()

        if contains_digits(nameEntry.get()):
            messagebox.showerror('Error', 'Name cannot contain numbers!', parent=add_window)
        elif contains_non_digit(patientIdEntry.get()):
            messagebox.showerror('Error', 'Patient ID should contain only numbers!', parent=add_window)
        elif bdayMonthEntry.get() in ("Month", "") or bdayDateEntry.get() in ("Day", "") or bdayYearEntry.get() in ("Year", ""):
            messagebox.showerror('Error', 'Please complete the birth date fields.', parent=add_window)
        elif (patientIdEntry.get()=='' or nameEntry.get()=='' or not mobile_input or emaileEntry.get()=='' or
              addressEntry.get()=='' or barangayEntry.get()=='' or municipalityEntry.get()=='' or provinceEntry.get()=='' or
              genderVar.get()=='' or diagnosisEntry.get()==''):
            messagebox.showerror('Error', 'All information are required!', parent= add_window)
        else:
            formatted_mobile = _normalize_mobile(mobile_input)
            if not formatted_mobile:
                messagebox.showerror('Error', 'Mobile No. must follow the format +63 XXX XXX XXXX or 09XX XXX XXXX.', parent=add_window)
                return
            name_value = _to_proper_case(nameEntry.get())
            address_parts = [addressEntry.get(), barangayEntry.get(), municipalityEntry.get(), provinceEntry.get()]
            combined_address = ', '.join(_to_proper_case(part) for part in address_parts)
            diagnosis_value = _to_proper_case(diagnosisEntry.get())
            try:
                query = (
                    'insert into patient ('
                    'patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date'
                    ') values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                )
                # combine address + barangay/city/province into single address field
                mycursor.execute(query, (
                    patientIdEntry.get(),
                    name_value,
                    formatted_mobile,
                    emaileEntry.get(),
                    combined_address,
                    genderVar.get(),
                    dob_combined,
                    diagnosis_value,
                    date
                ))
                con.commit()
                messagebox.showinfo('Success', f'Patient ID {patientIdEntry.get()} added successfully!', parent=add_window)
                result = messagebox.askquestion('Confirm', 'Clear the form for another entry?', parent= add_window)
                if result == 'yes':
                    patientIdEntry.delete(0, END)
                    nameEntry.delete(0, END)
                    mobileEntry.delete(0, END)
                    emaileEntry.delete(0, END)
                    addressEntry.delete(0, END)
                    barangayEntry.delete(0, END)
                    municipalityEntry.delete(0, END)
                    provinceEntry.delete(0, END)
                    diagnosisEntry.delete(0, END)
                    genderVar.set(genderOptions[0])
                    bdayMonthEntry.current(0)
                    bdayDateEntry.current(0)
                    bdayYearEntry.current(0)
                else:
                    add_window.destroy()
            except IntegrityError:
                messagebox.showerror('Error', 'Patient ID already exists.', parent= add_window)
                return
            except Exception as exc:
                messagebox.showerror('Error', f'Failed to add patient: {exc}', parent=add_window)
                return

        Show_patient()


    add_window = ctk.CTkToplevel()
    add_window.grab_set()
    add_window.resizable(False, False)
    add_window.title('Add Patient')
    add_window.configure(fg_color=ACCENT)

    form_container = ctk.CTkFrame(add_window, fg_color=CARD_BG, corner_radius=18)
    form_container.grid(row=0, column=0, padx=26, pady=24)
    form_container.grid_columnconfigure(0, weight=0)
    form_container.grid_columnconfigure(1, weight=1)

    patientIdLabel = ctk.CTkLabel(form_container, text='Patient ID', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    patientIdLabel.grid(row=0, column=0, padx=(24, 16), pady=(18, 8), sticky=W)
    patientIdEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13), width=220)
    patientIdEntry.grid(row=0, column=1, padx=(0, 24), pady=(18, 8), sticky='ew')

    nameLabel = ctk.CTkLabel(form_container, text='Name', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    nameLabel.grid(row=1, column=0, padx=(24, 16), pady=8, sticky=W)
    nameEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    nameEntry.grid(row=1, column=1, padx=(0, 24), pady=8, sticky='ew')

    mobileLabel = ctk.CTkLabel(form_container, text='Mobile No.', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    mobileLabel.grid(row=2, column=0, padx=(24, 16), pady=8, sticky=W)
    mobileEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13), placeholder_text='+63 000 000 0000')
    mobileEntry.grid(row=2, column=1, padx=(0, 24), pady=8, sticky='ew')

    emailLabel = ctk.CTkLabel(form_container, text='Email', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    emailLabel.grid(row=3, column=0, padx=(24, 16), pady=8, sticky=W)
    emaileEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    emaileEntry.grid(row=3, column=1, padx=(0, 24), pady=8, sticky='ew')

    addressLabel = ctk.CTkLabel(form_container, text='Street Address', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    addressLabel.grid(row=4, column=0, padx=(24, 16), pady=8, sticky=W)
    addressEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    addressEntry.grid(row=4, column=1, padx=(0, 24), pady=8, sticky='ew')

    barangayLabel = ctk.CTkLabel(form_container, text='Barangay', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    barangayLabel.grid(row=5, column=0, padx=(24, 16), pady=8, sticky=W)
    barangayEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    barangayEntry.grid(row=5, column=1, padx=(0, 24), pady=8, sticky='ew')

    municipalityLabel = ctk.CTkLabel(form_container, text='Municipality', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    municipalityLabel.grid(row=6, column=0, padx=(24, 16), pady=8, sticky=W)
    municipalityEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    municipalityEntry.grid(row=6, column=1, padx=(0, 24), pady=8, sticky='ew')

    provinceLabel = ctk.CTkLabel(form_container, text='Province', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    provinceLabel.grid(row=7, column=0, padx=(24, 16), pady=8, sticky=W)
    provinceEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    provinceEntry.grid(row=7, column=1, padx=(0, 24), pady=8, sticky='ew')

    genderLabel = ctk.CTkLabel(form_container, text='Gender', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    genderLabel.grid(row=8, column=0, padx=(24, 16), pady=8, sticky=W)
    genderOptions = ['Male', 'Female', 'Other']
    genderVar = StringVar(add_window)
    genderVar.set(genderOptions[0])
    genderDropdown = ctk.CTkOptionMenu(form_container, values=genderOptions, variable=genderVar, font=('Segoe UI', 13))
    genderDropdown.grid(row=8, column=1, padx=(0, 24), pady=8, sticky='ew')

    bdayLabel = ctk.CTkLabel(form_container, text='Date of Birth', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    bdayLabel.grid(row=9, column=0, padx=(24, 16), pady=8, sticky=W)

    months = ['Month'] + [str(i) for i in range(1, 13)]
    dates = ['Day'] + [str(i) for i in range(1, 32)]
    years = ['Year'] + [str(i) for i in range(1990, 2031)]

    dob_frame = ctk.CTkFrame(form_container, fg_color='transparent')
    dob_frame.grid(row=9, column=1, padx=(0, 24), pady=8, sticky='ew')
    dob_frame.grid_columnconfigure((0, 1, 2), weight=1)

    bdayMonthEntry = ttk.Combobox(dob_frame, values=months, state='readonly', width=10)
    bdayMonthEntry.grid(row=0, column=0, padx=2, pady=0, sticky='ew')
    bdayMonthEntry.current(0)
    _bind_combobox_scroll(bdayMonthEntry, months)

    bdayDateEntry = ttk.Combobox(dob_frame, values=dates, state='readonly', width=10)
    bdayDateEntry.grid(row=0, column=1, padx=2, pady=0, sticky='ew')
    bdayDateEntry.current(0)
    _bind_combobox_scroll(bdayDateEntry, dates)

    bdayYearEntry = ttk.Combobox(dob_frame, values=years, state='readonly', width=12)
    bdayYearEntry.grid(row=0, column=2, padx=2, pady=0, sticky='ew')
    bdayYearEntry.current(0)
    _bind_combobox_scroll(bdayYearEntry, years)

    diagnosisLabel = ctk.CTkLabel(form_container, text='Diagnosis', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    diagnosisLabel.grid(row=10, column=0, padx=(24, 16), pady=8, sticky=W)
    diagnosisEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    diagnosisEntry.grid(row=10, column=1, padx=(0, 24), pady=8, sticky='ew')

    add_stud_button = ctk.CTkButton(form_container, text='Add Patient', command=add_data, fg_color=SECONDARY,
                                    hover_color=PRIMARY, corner_radius=14, font=('Segoe UI', 14, 'bold'))
    add_stud_button.grid(row=11, column=0, columnspan=2, padx=24, pady=(18, 10), sticky='ew')


# Close the application gracefully after confirmation.
def Exit():
    quit = messagebox.askquestion('Exit','Do you want to Exit')
    if quit == 'yes':
        root.destroy()
    else:
        pass

con = db_connection
mycursor = db_cursor


# Keep the header clock label updated with current time.
def clock():
    global date, current_time
    date = time.strftime('%m/%d/%Y')
    current_time = time.strftime('%H:%M:%S')
    DateTimeLabel.configure(text=f'  Date: {date}\nTime: {current_time}')
    DateTimeLabel.after(1000, clock)

# **********GUI***************
root = ctk.CTk()
ctk.set_appearance_mode('light')
root.title('School Clinic Patient Record Management System')
root.configure(bg=BG)

# Establish a responsive base size that scales with the display.
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
min_width = min(1024, screen_w)
min_height = min(700, screen_h)
initial_w = min(max(int(screen_w * 0.85), min_width), screen_w)
initial_h = min(max(int(screen_h * 0.8), min_height), screen_h)
offset_x = max((screen_w - initial_w) // 2, 0)
offset_y = max((screen_h - initial_h) // 2, 0)
root.geometry(f'{initial_w}x{initial_h}+{offset_x}+{offset_y}')
root.minsize(min_width, min_height)
root.resizable(True, True)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame = ctk.CTkFrame(root, fg_color='transparent')
top_frame.grid(row=0, column=0, sticky='ew', padx=24, pady=(18, 12))
top_frame.grid_columnconfigure(0, weight=1)

stud = 'School Clinic Patient Record Management System'
sliderLabel = ctk.CTkLabel(
    top_frame,
    text=stud,
    font=('Segoe UI', 26, 'bold'),
    text_color='white',
    fg_color=HEADER_BG,
    corner_radius=18,
    height=60
)
sliderLabel.grid(row=0, column=0, sticky='ew')

DateTimeLabel = ctk.CTkLabel(
    top_frame,
    font=('Segoe UI', 12, 'bold'),
    text_color='white',
    fg_color=SECONDARY,
    corner_radius=12,
    padx=14,
    pady=6
)
DateTimeLabel.grid(row=0, column=1, padx=(12, 0), sticky='e')
clock()

body_frame = ctk.CTkFrame(root, fg_color='transparent')
body_frame.grid(row=1, column=0, sticky='nsew', padx=24, pady=(0, 24))
body_frame.grid_rowconfigure(0, weight=1)

if SIDEBAR_SIDE == 'left':
    sidebar_col, content_col = 0, 1
    sidebar_pad = (0, 18)
    content_pad = (18, 0)
else:
    sidebar_col, content_col = 1, 0
    sidebar_pad = (18, 0)
    content_pad = (0, 18)

body_frame.grid_columnconfigure(content_col, weight=1)
body_frame.grid_columnconfigure(sidebar_col, weight=0, minsize=260)

right_Frame = ctk.CTkFrame(body_frame, fg_color=SIDEBAR_BG, corner_radius=20)
right_Frame.grid(row=0, column=sidebar_col, sticky='nsew', padx=sidebar_pad)
right_Frame.grid_columnconfigure(0, weight=1)

left_frame = ctk.CTkFrame(body_frame, fg_color=ACCENT, corner_radius=24)
left_frame.grid(row=0, column=content_col, sticky='nsew', padx=content_pad)
left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=1)


# Load the sidebar logo image with enhanced nested frame design
def _load_sidebar_logo(filenames=("images/logo.png",), size=(120, 120)):
    try:
        for fname in filenames:
            if os.path.exists(fname):
                img_pil = Image.open(fname)
                img_pil.thumbnail(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img_pil)
    except Exception:
        pass
    # Fallback: create placeholder
    try:
        from PIL import Image as PILImage
        placeholder = PILImage.new('RGBA', size, ACCENT)
        return ImageTk.PhotoImage(placeholder)
    except Exception:
        return None

# Enhanced logo with nested frame design matching login
logo_outer = ctk.CTkFrame(right_Frame, fg_color=ACCENT, corner_radius=70, width=140, height=140, border_width=3, border_color=PRIMARY)
logo_outer.grid(row=0, column=0, pady=16, padx=0)
logo_outer.grid_propagate(False)

logo_inner = ctk.CTkFrame(logo_outer, fg_color='white', corner_radius=60, width=120, height=120)
logo_inner.place(relx=0.5, rely=0.5, anchor='center')

logo_image = _load_sidebar_logo()
logo_Label = Label(logo_inner, image=logo_image, bg='white', bd=0)
logo_Label.image = logo_image  # keep a reference to avoid garbage collection
logo_Label.place(relx=0.5, rely=0.5, anchor='center')

# Standardized sidebar buttons: stretch to available width and consistent spacing
button_kwargs = dict(
    fg_color=CARD_BG,
    hover_color=ACCENT,
    text_color=TEXT,
    corner_radius=14,
    font=('Segoe UI', 14, 'bold'),
    height=44,
    border_width=2,
    border_color=PRIMARY
)

add_stud_button = ctk.CTkButton(right_Frame, text='Add Patient', command=Add_patient, **button_kwargs)
add_stud_button.grid(row=1, column=0, pady=8, padx=10, sticky='ew')

delete_stud_button = ctk.CTkButton(right_Frame, text='Delete Patient', command=Delete_patient, **button_kwargs)
delete_stud_button.grid(row=2, column=0, pady=8, padx=10, sticky='ew')

update_stud_button = ctk.CTkButton(right_Frame, text='Update Patient', command=Update_patient, **button_kwargs)
update_stud_button.grid(row=3, column=0, pady=8, padx=10, sticky='ew')

import_stud_button = ctk.CTkButton(right_Frame, text='Import Patients', command=Import_data, **button_kwargs)
import_stud_button.grid(row=4, column=0, pady=8, padx=10, sticky='ew')

export_stud_button = ctk.CTkButton(right_Frame, text='Export Patients', command=Export_data, **button_kwargs)
export_stud_button.grid(row=5, column=0, pady=8, padx=10, sticky='ew')

analytics_button = ctk.CTkButton(right_Frame, text='View Analytics', command=Show_analytics_window, **button_kwargs)
analytics_button.grid(row=6, column=0, pady=8, padx=10, sticky='ew')

exit_button = ctk.CTkButton(right_Frame, text='Exit', command=Exit, fg_color='#e74c3c', hover_color='#c0392b', text_color='white', font=('Segoe UI', 14, 'bold'), corner_radius=14, height=44)
exit_button.grid(row=7, column=0, pady=12, padx=10, sticky='ew')

header_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
header_frame.grid(row=0, column=0, sticky='ew', padx=28, pady=(24, 12))
header_frame.grid_columnconfigure(0, weight=1)

table_heading = ctk.CTkLabel(header_frame, text='Patient Records', font=('Segoe UI', 22, 'bold'), text_color=TEXT, fg_color=ACCENT)
table_heading.grid(row=0, column=0, sticky='w')

control_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
control_frame.grid(row=0, column=1, sticky='e', padx=(12, 0))
control_frame.grid_columnconfigure(1, weight=1)
control_frame.grid_columnconfigure(3, weight=0)

search_field_var = ctk.StringVar(value=list(SEARCH_FIELD_OPTIONS.keys())[0])
search_field_menu = ctk.CTkOptionMenu(
    control_frame,
    values=list(SEARCH_FIELD_OPTIONS.keys()),
    variable=search_field_var,
    command=_on_search_field_change,
    fg_color=SECONDARY,
    button_color=SECONDARY,
    button_hover_color=PRIMARY,
    font=('Segoe UI', 13)
)
search_field_menu.grid(row=0, column=0, padx=(0, 8), sticky='e')

search_entry = ctk.CTkEntry(control_frame, placeholder_text='Search patients...', width=220, font=('Segoe UI', 13))
search_entry.grid(row=0, column=1, padx=(0, 8), sticky='e')
search_entry.bind('<KeyRelease>', _on_search_entry_change)
search_entry.bind('<Return>', _on_search_entry_change)

sort_button = ctk.CTkButton(control_frame, text='Sort', command=open_sort_dialog, fg_color=SECONDARY,
                             hover_color=PRIMARY, font=('Segoe UI', 13, 'bold'), corner_radius=12, width=80, height=36)
sort_button.grid(row=0, column=2, sticky='e')

selection_action_var = ctk.StringVar(value=SELECTION_MENU_OPTIONS[0])
selection_menu = ctk.CTkOptionMenu(
    control_frame,
    values=SELECTION_MENU_OPTIONS,
    variable=selection_action_var,
    command=_on_selection_action,
    fg_color=SECONDARY,
    button_color=SECONDARY,
    button_hover_color=PRIMARY,
    font=('Segoe UI', 13),
    width=125
)
selection_menu.grid(row=0, column=3, padx=(8, 0), sticky='e')

table_container = ctk.CTkFrame(left_frame, fg_color=CARD_BG, corner_radius=20)
table_container.grid(row=1, column=0, sticky='nsew', padx=24, pady=(0, 24))

tree_frame = Frame(table_container, bg=CARD_BG, bd=0, highlightthickness=0)
tree_frame.pack(fill=BOTH, expand=1, padx=16, pady=16)

scroll_bar_y = ttk.Scrollbar(tree_frame, orient=VERTICAL)
scroll_bar_y.pack(side=RIGHT, fill=Y)

scroll_bar_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
scroll_bar_x.pack(side=BOTTOM, fill=X)

patient_table = ttk.Treeview(tree_frame, columns=(
    'Patient ID', 'Name', 'Mobile No.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Visit Date'
), xscrollcommand=scroll_bar_x.set, yscrollcommand=scroll_bar_y.set, show='headings', selectmode='extended')
patient_table.pack(fill=BOTH, expand=1)

patient_table.bind('<Double-1>', Show_patient_details)
patient_table.bind('<Return>', Show_patient_details)

scroll_bar_x.config(command=patient_table.xview)
scroll_bar_y.config(command=patient_table.yview)

patient_table.heading('Patient ID', text='Patient ID')
patient_table.heading('Name', text='Name')
patient_table.heading('Mobile No.', text='Mobile No.')
patient_table.heading('Email', text='Email')
patient_table.heading('Address', text='Address')
patient_table.heading('Gender', text='Gender')
patient_table.heading('Date of Birth', text='Date of Birth')
patient_table.heading('Diagnosis', text='Diagnosis')
patient_table.heading('Visit Date', text='Visit Date')

patient_table.column('Patient ID', width=150, anchor=CENTER)
patient_table.column('Name', width=250, anchor=CENTER)
patient_table.column('Mobile No.', width=200, anchor=CENTER)
patient_table.column('Email', width=250, anchor=CENTER)
patient_table.column('Address', width=300, anchor=CENTER)
patient_table.column('Gender', width=150, anchor=CENTER)
patient_table.column('Date of Birth', width=200, anchor=CENTER)
patient_table.column('Diagnosis', width=250, anchor=CENTER)
patient_table.column('Visit Date', width=200, anchor=CENTER)

style = ttk.Style()
try:
    style.theme_use('clam')
except TclError:
    pass

style.configure('Treeview', rowheight=42, font=('Segoe UI', 11), foreground=TEXT,
                background=CARD_BG, fieldbackground=CARD_BG, borderwidth=0, highlightthickness=0)
style.configure('Treeview.Heading', font=('Segoe UI', 12, 'bold'), background=PRIMARY, foreground='white', borderwidth=0)
style.map('Treeview.Heading', background=[('active', SECONDARY)])
style.map('Treeview', background=[('selected', SECONDARY)], foreground=[('selected', 'white')])

style.configure('Vertical.TScrollbar', gripcount=0, background=PRIMARY, darkcolor=PRIMARY, lightcolor=PRIMARY,
                troughcolor=ACCENT, bordercolor=ACCENT, arrowcolor='white')
style.configure('Horizontal.TScrollbar', gripcount=0, background=PRIMARY, darkcolor=PRIMARY, lightcolor=PRIMARY,
                troughcolor=ACCENT, bordercolor=ACCENT, arrowcolor='white')

patient_table.tag_configure('evenrow', background=CARD_BG)
patient_table.tag_configure('oddrow', background=TABLE_BG)

Show_patient()

root.mainloop()