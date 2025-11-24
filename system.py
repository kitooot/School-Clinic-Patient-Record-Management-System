from tkinter import *
import time
import os
import ttkthemes
from tkinter import ttk, messagebox, filedialog
import pymysql
from pymysql.err import IntegrityError
import pandas
import customtkinter as ctk
from PIL import ImageTk, Image

PRIMARY = '#2ECC71'   # Mint Green
SECONDARY = '#16A085' # Deep Teal
BG = '#ECF0F1'        # Light Gray White (used for contrast when needed)
ACCENT = '#A3E4D7'    # Soft Mint
TEXT = '#2C3E50'      # Deep Gray Blue
TABLE_BG = '#F5FFFB'  # Pale Mint for table rows
SIDEBAR_BG = SECONDARY
HEADER_BG = PRIMARY
CARD_BG = '#FFFFFF'

# Sidebar placement: set to 'right' or 'left'
SIDEBAR_SIDE = 'left'

SEARCH_FIELD_OPTIONS = {
    'Patient ID': 'patient_id',
    'Name': 'name',
    'Mobile No.': 'mobile',
    'Email': 'email',
    'Address': 'address',
    'Gender': 'gender',
    'Date of Birth': 'dob',
    'Diagnosis': 'diagnosis',
    'Visit Date': 'visit_date'
}

SORT_FIELD_OPTIONS = {
    'Patient ID': 'patient_id',
    'Name': 'name',
    'Date of Birth': 'dob',
    'Visit Date': 'visit_date'
}

SORT_FIELD_LABELS = {value: key for key, value in SORT_FIELD_OPTIONS.items()}
DATE_SORT_FIELDS = {'dob', 'visit_date'}

current_sort_field = 'patient_id'
current_sort_order = 'ASC'
search_field_var = None
search_entry = None


def _normalize_mobile(number: str):
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


def _is_valid_mobile(number: str) -> bool:
    return _normalize_mobile(number) is not None


def _normalize_column_name(column_name: str) -> str:
    return ''.join(ch for ch in str(column_name).lower() if ch.isalnum())

def Export_data():
    url = filedialog.asksaveasfilename(defaultextension='.csv')
    if not url:
        return
    indexing = patient_table.get_children()
    new_list = []
    for index in indexing:
        content = patient_table.item(index)
        data_list = content['values']
        new_list.append(data_list)

    table = pandas.DataFrame(new_list, columns=[
        'Patient ID', 'Name', 'Mobile no.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Visit Date'
    ])
    table.to_csv(url, index=False)
    messagebox.showinfo('Success', 'Data is saved')


def _populate_table(rows):
    """Refresh treeview content and apply alternating row colors."""
    patient_table.delete(*patient_table.get_children())
    for index, row in enumerate(rows):
        row_values = list(row)
        if len(row_values) > 2:
            formatted_mobile = _normalize_mobile(row_values[2])
            if formatted_mobile:
                row_values[2] = formatted_mobile
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        patient_table.insert('', END, values=row_values, tags=(tag,))


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

    if sort_field in DATE_SORT_FIELDS:
        query += f' order by STR_TO_DATE({sort_field}, "%m/%d/%Y") {sort_order}'
    else:
        query += f' order by {sort_field} {sort_order}'

    mycursor.execute(query, tuple(params))
    return mycursor.fetchall()


def _bind_combobox_scroll(combobox, options):
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


def Get_previous_dob():
    indexing = patient_table.focus()
    if not indexing:
        return ''
    content = patient_table.item(indexing)
    list_data = content['values']
    if len(list_data) <= 6:
        return ''
    previous_dob = list_data[6]
    return previous_dob


def Update_patient():
    selection = patient_table.focus()
    if not selection:
        messagebox.showerror('Error', 'Please select a patient to update.')
        return

    content = patient_table.item(selection)
    list_data = content.get('values', [])
    if not list_data:
        messagebox.showerror('Error', 'Unable to read the selected patient data.')
        return

    patient_id = str(list_data[0])

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

        combined_address = f"{addressEntry.get()}, {barangayEntry.get()}, {municipalityEntry.get()}, {provinceEntry.get()}"
        combined_date = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"
        query = (
            'update patient set name=%s, mobile=%s, email=%s, address=%s, gender=%s, dob=%s, diagnosis=%s, visit_date=%s '
            'where patient_id=%s'
        )
        mycursor.execute(query, (
            nameEntry.get(), formatted_mobile, emaileEntry.get(), combined_address, genderVar.get(), combined_date,
            diagnosisEntry.get(), date, patient_id
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


def Delete_patient():
    selection = patient_table.focus()
    if not selection:
        messagebox.showerror('Error', 'Please select a patient to delete.')
        return

    content = patient_table.item(selection)
    values = content.get('values', [])
    if not values:
        messagebox.showerror('Error', 'Unable to read the selected patient data.')
        return

    confirm = messagebox.askyesno('Delete Patient', f'Do you want to delete patient {values[0]}?')
    if not confirm:
        return

    query = 'delete from patient where patient_id=%s'
    mycursor.execute(query, (values[0],))
    con.commit()
    messagebox.showinfo('Deleted', f'Patient {values[0]} deleted successfully')
    Show_patient()


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


def _on_search_entry_change(event=None):
    Show_patient()


def _on_search_field_change(choice):
    Show_patient()


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


def Import_data():
    filepath = filedialog.askopenfilename(
        title='Import Patient Data',
        filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
    )
    if not filepath:
        return

    try:
        data_frame = pandas.read_csv(filepath)
    except Exception as exc:
        messagebox.showerror('Error', f'Unable to read the selected file: {exc}')
        return

    if data_frame.empty:
        messagebox.showinfo('Import', 'The selected file does not contain any records.')
        return

    normalized_to_original = {
        _normalize_column_name(col): col for col in data_frame.columns
    }

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

def Add_patient():
    def add_data():
        def contains_digits(string):
            return any(char.isdigit() for char in string)
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
                messagebox.showerror('Error', 'Mobile No. must follow the format +63 000 000 0000.', parent=add_window)
                return
            try:
                query = (
                    'insert into patient ('
                    'patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date'
                    ') values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                )
                # combine address + barangay/city/province into single address field
                combined_address = f"{addressEntry.get()}, {barangayEntry.get()}, {municipalityEntry.get()}, {provinceEntry.get()}"
                mycursor.execute(query, (patientIdEntry.get(), nameEntry.get(), formatted_mobile, emaileEntry.get(), combined_address, genderVar.get(), dob_combined, diagnosisEntry.get(), date))
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

def Exit():
    quit = messagebox.askquestion('Exit','Do you want to Exit')
    if quit == 'yes':
        root.destroy()
    else:
        pass


con = pymysql.connect(host='localhost', user='root', password='')
mycursor = con.cursor()

try:
    query = 'create database clinicmanagementsystem'
    mycursor.execute(query)
    query = 'use clinicmanagementsystem'
    mycursor.execute(query)
    query = (
        'create table patient('
        'patient_id varchar(30) primary key, '
        'name varchar(30), mobile varchar(30), email varchar(30), '
        'address varchar(100), gender varchar(30), dob varchar(30), '
        'diagnosis varchar(30), visit_date varchar(30)'
        ')'
    )
    mycursor.execute(query)
except:
    query = 'use clinicmanagementsystem'
    mycursor.execute(query)
      
        
        
def clock():
    global date, current_time
    date = time.strftime('%m/%d/%Y')
    current_time = time.strftime('%H:%M:%S')
    DateTimeLabel.configure(text=f'  Date: {date}\nTime: {current_time}')
    DateTimeLabel.after(1000, clock)

# **********GUI***************
root = ctk.CTk()
ctk.set_appearance_mode('light')
root.geometry('1200x730+0+0')
root.title('School Clinic Patient Record Management System')
root.resizable(False, False)

root.configure(bg=BG)

DateTimeLabel = ctk.CTkLabel(root, font=('Segoe UI', 12, 'bold'), text_color='white', fg_color=SECONDARY, corner_radius=12, padx=14, pady=6)

DateTimeLabel.place(relx=0.985, rely=0.07, anchor='se')
clock()

stud = 'School Clinic Patient Record Management System'
sliderLabel = ctk.CTkLabel(root, text=stud, font=('Segoe UI', 26, 'bold'), text_color='white', fg_color=HEADER_BG, corner_radius=18, height=60)
sliderLabel.place(relx=0.5, rely=0.08, anchor='n', relwidth=0.9)

# Place sidebar using relative coordinates so it scales with the window
# Right sidebar occupies roughly 22% of the width on the right
right_Frame = ctk.CTkFrame(root, fg_color=SIDEBAR_BG, corner_radius=20)
if SIDEBAR_SIDE == 'right':
    right_frame_relx = 0.78
else:
    right_frame_relx = 0.02
# compute left area placement so main content doesn't overlap the sidebar
right_Frame.place(relx=right_frame_relx, rely=0.0, relwidth=0.2, relheight=1.0)
# allow centering/widgets to expand horizontally inside the sidebar
right_Frame.grid_columnconfigure(0, weight=1)

def _load_sidebar_logo(filenames=("logo.png",), size=(140, 140)):
    from PIL import ImageDraw
    for fname in filenames:
        if os.path.exists(fname):
            try:
                img = Image.open(fname).convert('RGBA')
                img.thumbnail(size, Image.LANCZOS)
                # Create rounded mask
                mask = Image.new('L', size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, size[0], size[1]), radius=35, fill=255)
                # Apply mask to create rounded image
                rounded_img = Image.new('RGBA', size, (0, 0, 0, 0))
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                rounded_img.paste(img, (x, y))
                rounded_img.putalpha(mask)
                # Create background
                bg_img = Image.new('RGBA', size, SIDEBAR_BG)
                bg_img.paste(rounded_img, (0, 0), rounded_img)
                return ImageTk.PhotoImage(bg_img)
            except Exception:
                continue
    # Fallback: plainly colored background that matches the sidebar
    try:
        fallback = Image.new('RGBA', size, SIDEBAR_BG)
        return ImageTk.PhotoImage(fallback)
    except Exception:
        return None

logo_image = _load_sidebar_logo()
logo_Label = Label(right_Frame, image=logo_image, bg=SIDEBAR_BG)
logo_Label.image = logo_image  # keep a reference to avoid garbage collection
logo_Label.grid(row=0, column=0, pady=12, padx=0, sticky='n')

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

exit_button = ctk.CTkButton(right_Frame, text='Exit', command=Exit, fg_color='#e74c3c', hover_color='#c0392b', text_color='white', font=('Segoe UI', 14, 'bold'), corner_radius=14, height=44)
exit_button.grid(row=6, column=0, pady=12, padx=10, sticky='ew')

left_frame = ctk.CTkFrame(root, fg_color=ACCENT, corner_radius=24)
# Compute left_frame position depending on which side the sidebar is on
if SIDEBAR_SIDE == 'right':
    left_relx = 0.03
    left_relwidth = 0.7
else:
    left_relx = 0.26
    left_relwidth = 0.7

left_frame.place(relx=left_relx, rely=0.18, relwidth=left_relwidth, relheight=0.80)

if SIDEBAR_SIDE == 'left':
    sliderLabel.place_configure(relx=left_relx + (left_relwidth / 2), relwidth=left_relwidth * 0.96)
else:
    sliderLabel.place_configure(relx=0.5, relwidth=0.9)

left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=1)

header_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
header_frame.grid(row=0, column=0, sticky='ew', padx=28, pady=(24, 12))
header_frame.grid_columnconfigure(0, weight=1)

table_heading = ctk.CTkLabel(header_frame, text='Patient Records', font=('Segoe UI', 22, 'bold'), text_color=TEXT, fg_color=ACCENT)
table_heading.grid(row=0, column=0, sticky='w')

control_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
control_frame.grid(row=0, column=1, sticky='e', padx=(12, 0))
control_frame.grid_columnconfigure(1, weight=1)

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
), xscrollcommand=scroll_bar_x.set, yscrollcommand=scroll_bar_y.set, show='headings')
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