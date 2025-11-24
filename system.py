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
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        patient_table.insert('', END, values=row, tags=(tag,))


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

    patient_id = list_data[0]

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
    mobileEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
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

    cityLabel = ctk.CTkLabel(form_container, text='City', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    cityLabel.grid(row=6, column=0, padx=(24, 16), pady=8, sticky=W)
    cityEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    cityEntry.grid(row=6, column=1, padx=(0, 24), pady=8, sticky='ew')

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

    months = [str(i) for i in range(1, 13)]
    dates = [str(i) for i in range(1, 32)]
    years = [str(i) for i in range(1990, 2031)]

    dob_frame = ctk.CTkFrame(form_container, fg_color='transparent')
    dob_frame.grid(row=9, column=1, padx=(0, 24), pady=8, sticky='ew')
    dob_frame.grid_columnconfigure((0, 1, 2), weight=1)

    bdayMonthEntry = ctk.CTkComboBox(dob_frame, values=months, font=('Segoe UI', 12), state='readonly', width=80)
    bdayMonthEntry.grid(row=0, column=0, padx=2)
    bdayMonthEntry.set('Month')

    bdayDateEntry = ctk.CTkComboBox(dob_frame, values=dates, font=('Segoe UI', 12), state='readonly', width=80)
    bdayDateEntry.grid(row=0, column=1, padx=2)
    bdayDateEntry.set('Day')

    bdayYearEntry = ctk.CTkComboBox(dob_frame, values=years, font=('Segoe UI', 12), state='readonly', width=90)
    bdayYearEntry.grid(row=0, column=2, padx=2)
    bdayYearEntry.set('Year')

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
            barangayEntry.get().strip(), cityEntry.get().strip(), provinceEntry.get().strip(), genderVar.get().strip(),
            diagnosisEntry.get().strip()
        ]
        if any(not value for value in required_fields):
            messagebox.showerror('Error', 'All fields are required before updating.', parent=update_window)
            return

        mobile_number = mobileEntry.get().strip()
        if not (len(mobile_number) == 11 and mobile_number.startswith('09') and mobile_number.isdigit()):
            messagebox.showerror('Error', 'Mobile number must be 11 digits and start with 09.', parent=update_window)
            return

        combined_address = f"{addressEntry.get()}, {barangayEntry.get()}, {cityEntry.get()}, {provinceEntry.get()}"
        combined_date = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"
        query = (
            'update patient set name=%s, mobile=%s, email=%s, address=%s, gender=%s, dob=%s, diagnosis=%s, visit_date=%s '
            'where patient_id=%s'
        )
        mycursor.execute(query, (
            nameEntry.get(), mobile_number, emaileEntry.get(), combined_address, genderVar.get(), combined_date,
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
        mobileEntry.insert(0, list_data[2])
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
            cityEntry.insert(0, parts[2])
        if len(parts) >= 4:
            provinceEntry.insert(0, parts[3])

    if len(list_data) > 5 and list_data[5]:
        genderVar.set(list_data[5])
    else:
        genderVar.set(genderOptions[0])

    existing_dob = list_data[6] if len(list_data) > 6 else ''
    if existing_dob and '/' in existing_dob:
        month, day, year = existing_dob.split('/')
        bdayMonthEntry.set(month)
        bdayDateEntry.set(day)
        bdayYearEntry.set(year)

    if len(list_data) > 7:
        diagnosisEntry.insert(0, list_data[7])


def Show_patient():
    query = 'select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date from patient'
    mycursor.execute(query)
    fetched_data = mycursor.fetchall()
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


def Search_patient():
    def search_data():
        field = selected_field.get()
        term = searchEntry.get().strip()
        if not term:
            messagebox.showerror('Error', 'Please enter a value to search.', parent=search_window)
            return

        query = (
            f'select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date '
            f'from patient where {field} LIKE %s'
        )
        wildcard_term = f"%{term}%"
        mycursor.execute(query, (wildcard_term,))
        fetched_data = mycursor.fetchall()
        if not fetched_data:
            messagebox.showinfo('Search', 'No matching records found.', parent=search_window)
        _populate_table(fetched_data)

    search_window = ctk.CTkToplevel()
    search_window.title('Search Patient')
    search_window.grab_set()
    search_window.resizable(False, False)
    search_window.configure(fg_color=ACCENT)

    search_fields = [
        'patient_id', 'name', 'mobile', 'email', 'address', 'gender', 'dob', 'diagnosis', 'visit_date'
    ]

    form_container = ctk.CTkFrame(search_window, fg_color=CARD_BG, corner_radius=18)
    form_container.grid(row=0, column=0, padx=24, pady=24)
    form_container.grid_columnconfigure(0, weight=0)
    form_container.grid_columnconfigure(1, weight=1)

    selected_field = ttk.Combobox(form_container, values=search_fields, state="readonly")
    selected_field.grid(row=0, column=0, padx=(18, 12), pady=12)
    selected_field.current(0)

    searchEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    searchEntry.grid(row=0, column=1, padx=(0, 18), pady=12)

    search_stud_button = ctk.CTkButton(form_container, text='Search', command=search_data, fg_color=SECONDARY,
                                       hover_color=PRIMARY, font=('Segoe UI', 13, 'bold'), corner_radius=12, width=120)
    search_stud_button.grid(row=1, column=0, columnspan=2, pady=(8, 4), padx=18, sticky='ew')

def Show_patient_details(event=None):
    selection = patient_table.focus()
    if not selection:
        return

    content = patient_table.item(selection)
    values = content.get('values', [])
    if not values:
        return

    detail_fields = ['Patient ID', 'Name', 'Mobile No.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Visit Date']
    padded_values = list(values) + [''] * (len(detail_fields) - len(values))

    detail_window = ctk.CTkToplevel()
    detail_window.title(f'Patient {padded_values[0]} Details')
    detail_window.grab_set()
    detail_window.resizable(False, False)
    detail_window.configure(fg_color=ACCENT)
    detail_window.transient(root)

    container = ctk.CTkFrame(detail_window, fg_color=CARD_BG, corner_radius=18)
    container.grid(row=0, column=0, padx=26, pady=24)
    container.grid_columnconfigure(1, weight=1)

    for index, (field_name, field_value) in enumerate(zip(detail_fields, padded_values)):
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

def Add_patient():
    def add_data():
        def contains_digits(string):
            return any(char.isdigit() for char in string)
        def contains_non_digits(string):
            return any(not char.isdigit() for char in string)
        def contains_non_digit(string):
            return any(not char.isdigit() and char != "-" for char in string)

        dob_combined = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"
        mobile_number = mobileEntry.get().strip()

        if contains_digits(nameEntry.get()):
            messagebox.showerror('Error', 'Name cannot contain numbers!', parent=add_window)
        elif contains_non_digit(patientIdEntry.get()):
            messagebox.showerror('Error', 'Patient ID should contain only numbers!', parent=add_window)
        elif contains_non_digits(mobile_number):
            messagebox.showerror('Error', 'Mobile No. should contain only numbers!', parent=add_window)
        elif not (len(mobile_number) == 11 and mobile_number.startswith('09') and mobile_number.isdigit()):
            messagebox.showerror('Error', 'Mobile No. must be 11 digits and start with 09.', parent=add_window)
        elif bdayMonthEntry.get() in ("Month", "") or bdayDateEntry.get() in ("Day", "") or bdayYearEntry.get() in ("Year", ""):
            messagebox.showerror('Error', 'Please complete the birth date fields.', parent=add_window)
        elif (patientIdEntry.get()=='' or nameEntry.get()=='' or mobile_number=='' or emaileEntry.get()=='' or
              addressEntry.get()=='' or barangayEntry.get()=='' or cityEntry.get()=='' or provinceEntry.get()=='' or
              genderVar.get()=='' or diagnosisEntry.get()==''):
            messagebox.showerror('Error', 'All information are required!', parent= add_window)
        else:
            try:
                query = (
                    'insert into patient ('
                    'patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date'
                    ') values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                )
                # combine address + barangay/city/province into single address field
                combined_address = f"{addressEntry.get()}, {barangayEntry.get()}, {cityEntry.get()}, {provinceEntry.get()}"
                mycursor.execute(query, (patientIdEntry.get(), nameEntry.get(), mobile_number, emaileEntry.get(), combined_address, genderVar.get(), dob_combined, diagnosisEntry.get(), date))
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
                    cityEntry.delete(0, END)
                    provinceEntry.delete(0, END)
                    diagnosisEntry.delete(0, END)
                    genderVar.set(genderOptions[0])
                    bdayMonthEntry.set("Month")
                    bdayDateEntry.set("Day")
                    bdayYearEntry.set("Year")
                else:
                    pass
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
    mobileEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
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

    cityLabel = ctk.CTkLabel(form_container, text='City', font=('Segoe UI', 16, 'bold'), text_color=TEXT)
    cityLabel.grid(row=6, column=0, padx=(24, 16), pady=8, sticky=W)
    cityEntry = ctk.CTkEntry(form_container, font=('Segoe UI', 13))
    cityEntry.grid(row=6, column=1, padx=(0, 24), pady=8, sticky='ew')

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

    months = [str(i) for i in range(1, 13)]
    dates = [str(i) for i in range(1, 32)]
    years = [str(i) for i in range(1990, 2031)]

    dob_frame = ctk.CTkFrame(form_container, fg_color='transparent')
    dob_frame.grid(row=9, column=1, padx=(0, 24), pady=8, sticky='ew')
    dob_frame.grid_columnconfigure((0, 1, 2), weight=1)

    bdayMonthEntry = ctk.CTkComboBox(dob_frame, values=months, font=('Segoe UI', 12), state='readonly', width=80)
    bdayMonthEntry.grid(row=0, column=0, padx=2)
    bdayMonthEntry.set('Month')

    bdayDateEntry = ctk.CTkComboBox(dob_frame, values=dates, font=('Segoe UI', 12), state='readonly', width=80)
    bdayDateEntry.grid(row=0, column=1, padx=2)
    bdayDateEntry.set('Day')

    bdayYearEntry = ctk.CTkComboBox(dob_frame, values=years, font=('Segoe UI', 12), state='readonly', width=90)
    bdayYearEntry.grid(row=0, column=2, padx=2)
    bdayYearEntry.set('Year')

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

show_stud_button = ctk.CTkButton(right_Frame, text='Show Patients', command=Show_patient, **button_kwargs)
show_stud_button.grid(row=4, column=0, pady=8, padx=10, sticky='ew')

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

search_header_button = ctk.CTkButton(header_frame, text='Search Patient', command=Search_patient, fg_color=SECONDARY,
                                     hover_color=PRIMARY, font=('Segoe UI', 13, 'bold'), corner_radius=12, width=140, height=36)
search_header_button.grid(row=0, column=1, sticky='e', padx=(12, 0))

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

root.mainloop()