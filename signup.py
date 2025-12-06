from tkinter import * # Import all necessary tkinter components
from tkinter import messagebox # For displaying message boxes
import ast # For safely evaluating string representations of Python data structures
import os # For file path operations
import customtkinter as ctk # Custom Tkinter for enhanced UI components
from PIL import Image # For image handling

from config import PRIMARY, SECONDARY, BG, ACCENT, TEXT, CARD_BG # Import color constants from config

# Initialize main window
window = ctk.CTk()
window.title("School Clinic - Staff Registration")
window.geometry('550x650+300+200')
ctk.set_appearance_mode('light')

window.configure(bg= BG)
window.resizable(False, False)


# Helper function to load icons with error handling
def _load_icon(path, size=(20, 20)):
    try:
        return ctk.CTkImage(Image.open(path), size=size)
    except Exception:
        return None

# Function to handle sign-up logic
def sign_up():
    username = username_entry.get().strip()
    passwrd = password_entry.get()
    confirm_pass = confirm_entry.get()

    if not username:
        messagebox.showerror('Error', 'Username cannot be empty')
        return

    if passwrd != confirm_pass:
        messagebox.showerror('Invalid', 'Passwords do not match')
        return

    try:
        # Load existing data safely
        if os.path.exists('data.txt'):
            with open('data.txt', 'r') as file:
                d = file.read().strip()
                r = ast.literal_eval(d) if d else {}
        else:
            r = {}

        if username in r:
            messagebox.showerror('Error', 'Username already exists')
            return

        r[username] = passwrd

        with open('data.txt', 'w') as file:
            file.write(str(r))

        messagebox.showinfo('Registration', 'Staff registered successfully')
        window.destroy()
        import loginn
    except Exception as e:
        messagebox.showerror('Error', f"An error occurred: {e}")

# Function to switch to sign-in window
def signin():
    window.destroy()
    import loginn

# Function to toggle password visibility
def toggle_password():
    if show_password.get():
        password_entry.configure(show='*')
        confirm_entry.configure(show='*')
        if hide_icon is not None:
            password_toggle_button.configure(image=hide_icon)
            confirm_toggle_button.configure(image=hide_icon)
        show_password.set(False)
    else:
        password_entry.configure(show='')
        confirm_entry.configure(show='')
        if show_icon is not None:
            password_toggle_button.configure(image=show_icon)
            confirm_toggle_button.configure(image=show_icon)
        show_password.set(True)

show_password = BooleanVar(value=False)
hide_icon = _load_icon('hidden.png')
show_icon = _load_icon('eye.png')

# Function to load logo image with fallback
def _load_logo(filenames=("logoo.png", "logo.png"), size=(140, 140)):
    for fname in filenames:
        if os.path.exists(fname):
            try:
                img = Image.open(fname)
                img.thumbnail(size, Image.LANCZOS)
                return ctk.CTkImage(img, size=img.size)
            except Exception:
                continue
    # fallback: create a simple placeholder image so widget still receives an image object
    placeholder = Image.new('RGBA', size, ACCENT)
    return ctk.CTkImage(placeholder, size=size)

logo_image = _load_logo()
header = ctk.CTkFrame(window, fg_color='transparent')
header.pack(fill='x', padx=24, pady=(0, 4))

logo_label = ctk.CTkLabel(header, image=logo_image if logo_image else None,
                          text='' if logo_image else 'School Clinic',
                          font=('Segoe UI', 20, 'bold'), text_color=TEXT, bg_color='transparent')
logo_label.pack(anchor='center')

heading = ctk.CTkLabel(window, text='Register Staff', font=('Segoe UI', 18, 'bold'), text_color=TEXT,
                       fg_color=PRIMARY, corner_radius=16, padx=32, pady=6)
heading.pack(pady=(0, 6))

form_card = ctk.CTkFrame(window, fg_color=CARD_BG, corner_radius=20)
form_card.pack(fill='x', expand=False, padx=80, pady=(4, 10))
form_card.grid_columnconfigure(0, weight=1)
form_card.grid_columnconfigure(1, weight=0)

username_label = ctk.CTkLabel(form_card, text='Username', font=('Segoe UI', 14, 'bold'), text_color=TEXT)
username_label.grid(row=0, column=0, sticky='w', padx=32, pady=(24, 6))
username_entry = ctk.CTkEntry(form_card, placeholder_text='Enter username', font=('Segoe UI', 13), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=1, corner_radius=12, height=34)
username_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=32, pady=(0, 10))

password_label = ctk.CTkLabel(form_card, text='Password', font=('Segoe UI', 14, 'bold'), text_color=TEXT)
password_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=32, pady=(18, 6))
password_entry = ctk.CTkEntry(form_card, placeholder_text='Enter password', font=('Segoe UI', 13), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=1, corner_radius=12, show='*', height=34)
password_entry.grid(row=3, column=0, sticky='ew', padx=(32, 4), pady=(0, 10))

password_toggle_button = ctk.CTkButton(form_card, width=36, height=34, text='', command=toggle_password,
                                       fg_color=ACCENT, hover_color=ACCENT, border_width=0, image=hide_icon)
password_toggle_button.grid(row=3, column=1, padx=(0, 32), pady=(0, 10), sticky='e')

confirm_label = ctk.CTkLabel(form_card, text='Confirm Password', font=('Segoe UI', 14, 'bold'), text_color=TEXT)
confirm_label.grid(row=4, column=0, columnspan=2, sticky='w', padx=32, pady=(18, 6))
confirm_entry = ctk.CTkEntry(form_card, placeholder_text='Confirm password', font=('Segoe UI', 13), text_color=TEXT,
                             fg_color=ACCENT, border_color=PRIMARY, border_width=1, corner_radius=12, show='*', height=34)
confirm_entry.grid(row=5, column=0, sticky='ew', padx=(32, 4), pady=(0, 10))

confirm_toggle_button = ctk.CTkButton(form_card, width=36, height=34, text='', command=toggle_password,
                                      fg_color=ACCENT, hover_color=ACCENT, border_width=0, image=hide_icon)
confirm_toggle_button.grid(row=5, column=1, padx=(0, 32), pady=(0, 10), sticky='e')

register_button = ctk.CTkButton(form_card, text='Register', command=sign_up, fg_color=SECONDARY,
                                hover_color=PRIMARY, font=('Segoe UI', 14, 'bold'), corner_radius=14)
register_button.grid(row=6, column=0, columnspan=2, padx=32, pady=(24, 18), sticky='ew')

link_row = ctk.CTkFrame(window, fg_color='transparent')
link_row.pack(pady=(2, 8))

prompt_label = ctk.CTkLabel(link_row, text='Already have an account?', font=('Segoe UI', 11), text_color=TEXT)
prompt_label.grid(row=0, column=0, sticky='e')

sign_in = ctk.CTkButton(link_row, text='Sign In', command=signin, fg_color='transparent', text_color=SECONDARY,
                        hover_color=ACCENT, font=('Segoe UI', 11, 'bold'), width=90)
sign_in.grid(row=0, column=1, padx=(12, 0), sticky='w')

window.mainloop()