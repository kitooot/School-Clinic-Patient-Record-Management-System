from tkinter import *
import time
import os
import ttkthemes
from tkinter import ttk, messagebox, filedialog
import pymysql
import pandas
import customtkinter as ctk
from PIL import ImageTk, Image

# Color palette (all derived from the logo)
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
    url = filedialog.asksaveasfilename(defaultextension= '.csv')
    indexing =  patient_table.get_children()
    new_list = []
    for index in indexing:
        content = patient_table.item(index)
        data_list = content['values']
        new_list.append(data_list)

    table = pandas.DataFrame(new_list, columns=[
        'Patient ID', 'Name', 'Mobile no.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Ward', 'Visit Date'
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
    # Fetch the current selected patient's data
    indexing = patient_table.focus()
    content = patient_table.item(indexing)
    list_data = content['values']
    # Extract the current DOB information
    previous_dob = list_data[6]  # Assuming DOB is at index 6
    return previous_dob

def Update_patient():
    def Update_data():
        combined_date = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"
        query = (
            'update patient set name=%s, mobile=%s, email=%s, address=%s, gender=%s, dob=%s, diagnosis=%s, ward=%s, visit_date=%s '
            'where patient_id=%s'
        )
        # combine address parts into one string for storage
        combined_address = f"{addressEntry.get()}, {barangayEntry.get()}, {cityEntry.get()}, {provinceEntry.get()}"
        mycursor.execute(query, (
            nameEntry.get(), mobileEntry.get(), emaileEntry.get(), combined_address, genderVar.get(), combined_date,
            diagnosisEntry.get(), wardEntry.get(), date, patientIdEntry.get()
        ))
        con.commit()
        messagebox.showinfo('Success', f'Patient ID {patientIdEntry.get()} is updated successfully')
        update_window.destroy()
        Show_patient()

    update_window = ctk.CTkToplevel()
    update_window.title('Update Patient')
    update_window.grab_set()
    update_window.resizable(False, False)
    patientIdLabel = ctk.CTkLabel(update_window, text='Patient ID', font=('times new roman', 20, 'bold'))
    patientIdLabel.grid(row= 0, column= 0, padx= 30, pady= 15, sticky=W)
    patientIdEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    patientIdEntry.grid(row= 0, column= 1, padx= 15, pady=10)

    nameLabel = ctk.CTkLabel(update_window, text='Name', font=('times new roman', 20, 'bold'))
    nameLabel.grid(row= 1, column= 0, padx= 30, pady= 15, sticky=W)
    nameEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    nameEntry.grid(row= 1, column= 1, padx= 15, pady=10)

    mobileLabel = ctk.CTkLabel(update_window, text='Mobile No.', font=('times new roman', 20, 'bold'))
    mobileLabel.grid(row= 2, column= 0, padx= 30, pady= 15, sticky=W)
    mobileEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    mobileEntry.grid(row= 2, column= 1, padx= 15, pady=10)

    emailLabel = ctk.CTkLabel(update_window, text='Email', font=('times new roman', 20, 'bold'))
    emailLabel.grid(row= 3, column= 0, padx= 30, pady= 15, sticky=W)
    emaileEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    emaileEntry.grid(row= 3, column= 1, padx= 15, pady=10)

    addressLabel = ctk.CTkLabel(update_window, text='Address', font=('times new roman', 20, 'bold'))
    addressLabel.grid(row= 4, column= 0, padx= 30, pady= 15, sticky=W)
    addressEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    addressEntry.grid(row= 4, column= 1, padx= 15, pady=10)

    # Additional address fields: Barangay, City, Province (placed on separate rows)
    barangayLabel = ctk.CTkLabel(update_window, text='Barangay', font=('times new roman', 16, 'bold'))
    barangayLabel.grid(row=5, column=0, padx=30, pady=10, sticky=W)
    barangayEntry = ctk.CTkEntry(update_window, font=('times new roman', 14, 'bold'))
    barangayEntry.grid(row=5, column=1, padx=15, pady=10)

    cityLabel = ctk.CTkLabel(update_window, text='City', font=('times new roman', 16, 'bold'))
    cityLabel.grid(row=6, column=0, padx=30, pady=10, sticky=W)
    cityEntry = ctk.CTkEntry(update_window, font=('times new roman', 14, 'bold'))
    cityEntry.grid(row=6, column=1, padx=15, pady=10)

    provinceLabel = ctk.CTkLabel(update_window, text='Province', font=('times new roman', 16, 'bold'))
    provinceLabel.grid(row=7, column=0, padx=30, pady=10, sticky=W)
    provinceEntry = ctk.CTkEntry(update_window, font=('times new roman', 14, 'bold'))
    provinceEntry.grid(row=7, column=1, padx=15, pady=10)

    genderLabel = ctk.CTkLabel(update_window, text='Gender', font=('times new roman', 20, 'bold'))
    genderLabel.grid(row= 8, column= 0, padx= 30, pady= 15, sticky=W)
    genderOptions = ['Male', 'Female', 'Other']
    genderVar = StringVar(update_window)
    genderVar.set(genderOptions[0])  # Default value

    genderDropdown = OptionMenu(update_window, genderVar, *genderOptions)
    genderDropdown.config(width=15, font=('times new roman', 15, 'bold'))
    genderDropdown.grid(row=5, column=1, padx=15, pady=10)
    
    bdayLabel = ctk.CTkLabel(update_window, text='Date of Birth', font=('times new roman', 20, 'bold'))
    bdayLabel.grid(row= 9, column= 0, padx= 30, pady= 15, sticky=W)
    # Dropdown menu for month
    months = [str(i) for i in range(1, 13)]
    bdayMonthEntry = ttk.Combobox(update_window, values=months, font=('times new roman', 15, 'bold'), width=15, state="readonly")
    bdayMonthEntry.grid(row=9, column=1, padx=0, pady=10)
    bdayMonthEntry.set("Month")  # Set default value

    # Dropdown menu for date (1 to 31)
    datee = [str(i) for i in range(1, 32)]
    bdayDateEntry = ttk.Combobox(update_window, values=datee, font=('times new roman', 15, 'bold'), width=15, state="readonly")
    bdayDateEntry.grid(row=9, column=2, padx=0, pady=10)
    bdayDateEntry.set("Day")  # Set default value

    year = [str(i) for i in range(2000, 2023)]
    bdayYearEntry = ttk.Combobox(update_window, values=year, font=('times new roman', 15, 'bold'), width=15, state="readonly")
    bdayYearEntry.grid(row=9, column=3, padx=0, pady=10)
    bdayYearEntry.set("Year")  # Set default value

    diagnosisLabel = ctk.CTkLabel(update_window, text='Diagnosis', font=('times new roman', 20, 'bold'))
    diagnosisLabel.grid(row= 10, column= 0, padx= 30, pady= 15, sticky=W)
    diagnosisEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    diagnosisEntry.grid(row= 10, column= 1, padx= 15, pady=10)

    wardLabel = ctk.CTkLabel(update_window, text='Ward', font=('times new roman', 20, 'bold'))
    wardLabel.grid(row= 11, column= 0, padx= 30, pady= 15, sticky=W)
    wardEntry = ctk.CTkEntry(update_window, font=('times new roman', 15, 'bold'))
    wardEntry.grid(row= 11, column= 1, padx= 15, pady=10)

    update_stud_button = ctk.CTkButton(update_window, text='Update', command= Update_data)
    update_stud_button.grid(row= 12, columnspan=4, pady= 15)

    indexing = patient_table.focus()
    content = patient_table.item(indexing)
    list_data = content['values']
    patientIdEntry.insert(0, list_data[0])
    nameEntry.insert(0, list_data[1])
    mobileEntry.insert(0, list_data[2])
    emaileEntry.insert(0, list_data[3])
    addressEntry.insert(0, list_data[4])
    genderVar.set(list_data[5])
    diagnosisEntry.insert(0, list_data[7])
    wardEntry.insert(0, list_data[8])

    # Parse stored address into its parts if available (expected format: addr, barangay, city, province)
    stored_address = list_data[4] if len(list_data) > 4 else ''
    if stored_address:
        parts = [p.strip() for p in stored_address.split(',')]
        if len(parts) >= 1:
            addressEntry.delete(0, END)
            addressEntry.insert(0, parts[0])
        if len(parts) >= 2:
            barangayEntry.delete(0, END)
            barangayEntry.insert(0, parts[1])
        if len(parts) >= 3:
            cityEntry.delete(0, END)
            cityEntry.insert(0, parts[2])
        if len(parts) >= 4:
            provinceEntry.delete(0, END)
            provinceEntry.insert(0, parts[3])

    existing_dob = list_data[6]
    if existing_dob:
        month, day, year = existing_dob.split('/')
        bdayMonthEntry.set(month)
        bdayDateEntry.set(day)
        bdayYearEntry.set(year)

def Show_patient():
    query = 'select * from patient'
    mycursor.execute(query)
    fetched_data = mycursor.fetchall()
    _populate_table(fetched_data)

def Delete_patient():
    ask = messagebox.askquestion('Delete Patient', 'Do you want to delete this patient?')
    if ask == 'yes':
        indexing = patient_table.focus()
        content = patient_table.item(indexing)
        content_id = content['values'][0]
        query = 'delete from patient where patient_id=%s'
        mycursor.execute(query, (content_id,))
        con.commit()
        messagebox.showinfo('Deleted', f'Patient {content_id} deleted successfully')
        Show_patient()
    else:
        pass


def Search_patient():
    def search_data():
        query = 'select * from patient where {}=%s'.format(selected_field.get())
        mycursor.execute(query, (searchEntry.get(),))
        fetched_data = mycursor.fetchall()
        _populate_table(fetched_data)

    search_window = ctk.CTkToplevel()
    search_window.title('Search Patient')
    search_window.grab_set()
    search_window.resizable(False, False)

    search_fields = [
        'patient_id', 'name', 'mobile', 'email', 'address', 'gender', 'dob', 'diagnosis', 'ward'
    ]

    selected_field = ttk.Combobox(search_window, values=search_fields, state="readonly")
    selected_field.grid(row=0, column=0, padx=15, pady=10)
    selected_field.current(0)

    searchEntry = ctk.CTkEntry(search_window, font=('times new roman', 15, 'bold'))
    searchEntry.grid(row=0, column=1, padx=15, pady=10)

    search_stud_button = ctk.CTkButton(search_window, text='Search Patient', command=search_data)
    search_stud_button.grid(row=1, columnspan=2, pady=15)

def Add_patient():
    def add_data():
        def contains_digits(string):
            return any(char.isdigit() for char in string)
        def contains_non_digits(string):
            return any(not char.isdigit() for char in string)
        def contains_non_digit(string):
            return any(not char.isdigit() and char != "-" for char in string)

        dob_combined = f"{bdayMonthEntry.get()}/{bdayDateEntry.get()}/{bdayYearEntry.get()}"

        if contains_digits(nameEntry.get()):
            messagebox.showerror('Error', 'Name cannot contain numbers!', parent=add_window)
        elif contains_non_digit(patientIdEntry.get()):
            messagebox.showerror('Error', 'Patient ID should contain only numbers!', parent=add_window)
        elif contains_non_digits(mobileEntry.get()):
            messagebox.showerror('Error', 'Mobile No. should contain only numbers!', parent=add_window)
        elif (patientIdEntry.get()=='' or nameEntry.get()=='' or mobileEntry.get()=='' or emaileEntry.get()=='' or
              addressEntry.get()=='' or barangayEntry.get()=='' or cityEntry.get()=='' or provinceEntry.get()=='' or
              genderVar.get()=='' or diagnosisEntry.get()=='' or wardEntry.get()==''):
            messagebox.showerror('Error', 'All information are required!', parent= add_window)
        else:
            try:
                query = 'insert into patient values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                # combine address + barangay/city/province into single address field
                combined_address = f"{addressEntry.get()}, {barangayEntry.get()}, {cityEntry.get()}, {provinceEntry.get()}"
                mycursor.execute(query, (patientIdEntry.get(), nameEntry.get(), mobileEntry.get(), emaileEntry.get(), combined_address, genderVar.get(), dob_combined, diagnosisEntry.get(), wardEntry.get(), date))
                con.commit()
                result = messagebox.askquestion('Confirm', 'Data was Added, Do you want to clear the form?', parent= add_window)
                if result:
                    patientIdEntry.delete(0, END)
                    nameEntry.delete(0, END)
                    mobileEntry.delete(0, END)
                    emaileEntry.delete(0, END)
                    addressEntry.delete(0, END)
                    barangayEntry.delete(0, END)
                    cityEntry.delete(0, END)
                    provinceEntry.delete(0, END)
                    diagnosisEntry.delete(0, END)
                    wardEntry.delete(0,END)
                    genderVar.set(genderOptions[0])
                    bdayMonthEntry.set("Month")
                    bdayDateEntry.set("Day")
                    bdayYearEntry.set("Year")
                else:
                    pass
            except:
                messagebox.showerror('Error', 'ID cannot be repeated', parent= add_window)
                return

        Show_patient()


    add_window = ctk.CTkToplevel()
    add_window.grab_set()
    add_window.resizable(False, False)
    patientIdLabel = ctk.CTkLabel(add_window, text='Patient ID', font=('times new roman', 20, 'bold'))
    patientIdLabel.grid(row= 0, column= 0, padx= 30, pady= 15, sticky=W)
    patientIdEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    patientIdEntry.grid(row= 0, column= 1, padx= 15, pady=10)

    nameLabel = ctk.CTkLabel(add_window, text='Name', font=('times new roman', 20, 'bold'))
    nameLabel.grid(row= 1, column= 0, padx= 30, pady= 15, sticky=W)
    nameEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    nameEntry.grid(row= 1, column= 1, padx= 15, pady=10)

    mobileLabel = ctk.CTkLabel(add_window, text='Mobile No.', font=('times new roman', 20, 'bold'))
    mobileLabel.grid(row= 2, column= 0, padx= 30, pady= 15, sticky=W)
    mobileEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    mobileEntry.grid(row= 2, column= 1, padx= 15, pady=10)

    emailLabel = ctk.CTkLabel(add_window, text='Email', font=('times new roman', 20, 'bold'))
    emailLabel.grid(row= 3, column= 0, padx= 30, pady= 15, sticky=W)
    emaileEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    emaileEntry.grid(row= 3, column= 1, padx= 15, pady=10)

    addressLabel = ctk.CTkLabel(add_window, text='Address', font=('times new roman', 20, 'bold'))
    addressLabel.grid(row= 4, column= 0, padx= 30, pady= 15, sticky=W)
    addressEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    addressEntry.grid(row= 4, column= 1, padx= 15, pady=10)

    # Additional address fields: Barangay, City, Province (placed on separate rows)
    barangayLabel = ctk.CTkLabel(add_window, text='Barangay', font=('times new roman', 16, 'bold'))
    barangayLabel.grid(row=5, column=0, padx=30, pady=10, sticky=W)
    barangayEntry = ctk.CTkEntry(add_window, font=('times new roman', 14, 'bold'))
    barangayEntry.grid(row=5, column=1, padx=15, pady=10)

    cityLabel = ctk.CTkLabel(add_window, text='City', font=('times new roman', 16, 'bold'))
    cityLabel.grid(row=6, column=0, padx=30, pady=10, sticky=W)
    cityEntry = ctk.CTkEntry(add_window, font=('times new roman', 14, 'bold'))
    cityEntry.grid(row=6, column=1, padx=15, pady=10)

    provinceLabel = ctk.CTkLabel(add_window, text='Province', font=('times new roman', 16, 'bold'))
    provinceLabel.grid(row=7, column=0, padx=30, pady=10, sticky=W)
    provinceEntry = ctk.CTkEntry(add_window, font=('times new roman', 14, 'bold'))
    provinceEntry.grid(row=7, column=1, padx=15, pady=10)

    genderLabel = ctk.CTkLabel(add_window, text='Gender', font=('times new roman', 20, 'bold'))
    genderLabel.grid(row= 8, column= 0, padx= 30, pady= 15, sticky=W)
    genderOptions = ['Male', 'Female', 'Other']
    genderVar = StringVar(add_window)
    genderVar.set(genderOptions[0])

    genderDropdown = OptionMenu(add_window, genderVar, *genderOptions)
    genderDropdown.config(width=15, font=('times new roman', 15, 'bold'))
    genderDropdown.grid(row=8, column=1, padx=15, pady=10)

    bdayLabel = ctk.CTkLabel(add_window, text='Date of Birth', font=('times new roman', 20, 'bold'))
    bdayLabel.grid(row= 9, column= 0, padx= 30, pady= 15, sticky=W)
    months = [str(i) for i in range(1, 13)]
    bdayMonthEntry = ttk.Combobox(add_window, values=months, font=('times new roman', 15, 'bold'), width=15, state="readonly")
    bdayMonthEntry.grid(row=9, column=1, padx=0, pady=10)
    bdayMonthEntry.set("Month")

    dates = [str(i) for i in range(1, 32)]
    bdayDateEntry = ttk.Combobox(add_window, values=dates, font=('times new roman', 15, 'bold'), width=15, state="readonly")
    bdayDateEntry.grid(row=9, column=2, padx=0, pady=10)
    bdayDateEntry.set("Day")

    year = [str(i) for i in range(2000, 2023)]
    bdayYearEntry = ttk.Combobox(add_window, values=year, font=('times new roman', 15, 'bold'), width=15, state="readonly")
    bdayYearEntry.grid(row=9, column=3, padx=0, pady=10)
    bdayYearEntry.set("Year")

    diagnosisLabel = ctk.CTkLabel(add_window, text='Diagnosis', font=('times new roman', 20, 'bold'))
    diagnosisLabel.grid(row= 10, column= 0, padx= 30, pady= 15, sticky=W)
    diagnosisEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    diagnosisEntry.grid(row= 10, column= 1, padx= 15, pady=10)

    wardLabel = ctk.CTkLabel(add_window, text='Ward', font=('times new roman', 20, 'bold'))
    wardLabel.grid(row= 11, column= 0, padx= 30, pady= 15, sticky=W)
    wardEntry = ctk.CTkEntry(add_window, font=('times new roman', 15, 'bold'))
    wardEntry.grid(row= 11, column= 1, padx= 15, pady=10)

    add_stud_button = ctk.CTkButton(add_window, text='Add Patient', command=add_data)
    add_stud_button.grid(row= 12, columnspan=4, pady= 15)

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
        'diagnosis varchar(30), ward varchar(30), visit_date varchar(30)'
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
    for fname in filenames:
        if os.path.exists(fname):
            try:
                img = Image.open(fname).convert('RGBA')
                img.thumbnail(size, Image.LANCZOS)
                # create a background with the sidebar bg so the image sits centered
                bg_img = Image.new('RGBA', size, SIDEBAR_BG)
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                # if the image has alpha, use it as mask when pasting
                mask = img.split()[3] if 'A' in img.getbands() else None
                bg_img.paste(img, (x, y), mask)
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

search_stud_button = ctk.CTkButton(right_Frame, text='Search Patient', command=Search_patient, **button_kwargs)
search_stud_button.grid(row=2, column=0, pady=8, padx=10, sticky='ew')

delete_stud_button = ctk.CTkButton(right_Frame, text='Delete Patient', command=Delete_patient, **button_kwargs)
delete_stud_button.grid(row=3, column=0, pady=8, padx=10, sticky='ew')

update_stud_button = ctk.CTkButton(right_Frame, text='Update Patient', command=Update_patient, **button_kwargs)
update_stud_button.grid(row=4, column=0, pady=8, padx=10, sticky='ew')

show_stud_button = ctk.CTkButton(right_Frame, text='Show Patients', command=Show_patient, **button_kwargs)
show_stud_button.grid(row=5, column=0, pady=8, padx=10, sticky='ew')

export_stud_button = ctk.CTkButton(right_Frame, text='Export Patients', command=Export_data, **button_kwargs)
export_stud_button.grid(row=6, column=0, pady=8, padx=10, sticky='ew')

exit_button = ctk.CTkButton(right_Frame, text='Exit', command=Exit, fg_color='#e74c3c', hover_color='#c0392b', text_color='white', font=('Segoe UI', 14, 'bold'), corner_radius=14, height=44)
exit_button.grid(row=7, column=0, pady=12, padx=10, sticky='ew')

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

table_heading = ctk.CTkLabel(left_frame, text='Patient Records', font=('Segoe UI', 22, 'bold'), text_color=TEXT, fg_color=ACCENT)
table_heading.grid(row=0, column=0, sticky='w', padx=28, pady=(24, 12))

table_container = ctk.CTkFrame(left_frame, fg_color=CARD_BG, corner_radius=20)
table_container.grid(row=1, column=0, sticky='nsew', padx=24, pady=(0, 24))

tree_frame = Frame(table_container, bg=CARD_BG, bd=0, highlightthickness=0)
tree_frame.pack(fill=BOTH, expand=1, padx=16, pady=16)

scroll_bar_y = ttk.Scrollbar(tree_frame, orient=VERTICAL)
scroll_bar_y.pack(side=RIGHT, fill=Y)

scroll_bar_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
scroll_bar_x.pack(side=BOTTOM, fill=X)

patient_table = ttk.Treeview(tree_frame, columns=(
    'Patient ID', 'Name', 'Mobile No.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Ward', 'Visit Date'
), xscrollcommand=scroll_bar_x.set, yscrollcommand=scroll_bar_y.set, show='headings')
patient_table.pack(fill=BOTH, expand=1)

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
patient_table.heading('Ward', text='Ward')
patient_table.heading('Visit Date', text='Visit Date')

patient_table.column('Patient ID', width=150, anchor=CENTER)
patient_table.column('Name', width=250, anchor=CENTER)
patient_table.column('Mobile No.', width=200, anchor=CENTER)
patient_table.column('Email', width=250, anchor=CENTER)
patient_table.column('Address', width=300, anchor=CENTER)
patient_table.column('Gender', width=150, anchor=CENTER)
patient_table.column('Date of Birth', width=200, anchor=CENTER)
patient_table.column('Diagnosis', width=250, anchor=CENTER)
patient_table.column('Ward',width=150, anchor=CENTER)
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