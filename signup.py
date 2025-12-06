from tkinter import * # Import all necessary tkinter components
from tkinter import messagebox # For displaying message boxes
import os # For file path operations
import customtkinter as ctk # Custom Tkinter for enhanced UI components
from PIL import Image # For image handling

from system_configs.config import PRIMARY, SECONDARY, BG, ACCENT, TEXT, CARD_BG # Import color constants from config
from system_configs.database import db_connection, db_cursor # Import database connection

_next_action = None  # Track which window to launch after signup UI closes


def _show_launch_error(exc: Exception) -> None:
    fallback = Tk()
    fallback.withdraw()
    messagebox.showerror('Error', f'Failed to start login: {exc}\n\nCheck the terminal for full traceback.')
    fallback.destroy()


def _perform_transition() -> None:
    global _next_action
    target = _next_action
    if target is None:
        return

    _next_action = None
    window.destroy()

    if target == 'loginn':
        try:
            import loginn  # pylint: disable=import-outside-toplevel,unused-import
        except Exception as exc:  # pylint: disable=broad-except
            _show_launch_error(exc)


def _schedule_transition(target: str) -> None:
    global _next_action
    _next_action = target
    window.after(10, _perform_transition)

# Initialize main window
window = ctk.CTk()
window.title("School Clinic - Staff Registration")
ctk.set_appearance_mode('light')

# Center window on screen with better dimensions
window.update_idletasks()
screen_w = window.winfo_screenwidth()
screen_h = window.winfo_screenheight()
win_w, win_h = 600, 760
pos_x = (screen_w - win_w) // 2
pos_y = (screen_h - win_h) // 2
window.geometry(f'{win_w}x{win_h}+{pos_x}+{pos_y}')
window.configure(bg=BG)
window.resizable(False, False)


# Helper function to load icons with error handling
def _load_icon(path, size=(20, 20)):
    try:
        return ctk.CTkImage(Image.open(f'images/{path}'), size=size)
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

    if not passwrd:
        messagebox.showerror('Error', 'Password cannot be empty')
        return

    if passwrd != confirm_pass:
        messagebox.showerror('Invalid', 'Passwords do not match')
        return

    try:
        # Check if username already exists
        db_cursor.execute('SELECT username FROM users WHERE username = %s', (username,))
        if db_cursor.fetchone():
            messagebox.showerror('Error', 'Username already exists')
            return

        # Insert new user into database
        db_cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, passwrd))
        db_connection.commit()

        messagebox.showinfo('Registration', 'Staff registered successfully')
        _schedule_transition('loginn')
    except Exception as e:
        messagebox.showerror('Error', f"Database error: {e}")

# Function to switch to sign-in window
def signin():
    _schedule_transition('loginn')

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
def _load_logo(filenames=("images/logoo.png", "images/logo.png"), size=(140, 140)):
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

# Enhanced header section with gradient-like layering
header = ctk.CTkFrame(window, fg_color='transparent')
header.pack(fill='x', pady=(20, 0))

logo_image = _load_logo()
logo_outer = ctk.CTkFrame(header, fg_color=ACCENT, corner_radius=80, width=160, height=160, border_width=3, border_color=PRIMARY)
logo_outer.pack(anchor='center')
logo_outer.pack_propagate(False)

logo_inner = ctk.CTkFrame(logo_outer, fg_color='white', corner_radius=72, width=144, height=144)
logo_inner.place(relx=0.5, rely=0.5, anchor='center')
logo_label = ctk.CTkLabel(logo_inner, image=logo_image, text='')
logo_label.place(relx=0.5, rely=0.5, anchor='center')

heading = ctk.CTkLabel(header, text='Create Account', font=('Segoe UI', 32, 'bold'), text_color='white',
                       fg_color=PRIMARY, corner_radius=20, padx=48, pady=12)
heading.pack(pady=(18, 0), anchor='center')

subtitle = ctk.CTkLabel(header, text='Register to manage patient records', font=('Segoe UI', 12), text_color=TEXT)
subtitle.pack(pady=(6, 0), anchor='center')

# Enhanced form card with shadow effect
form_outer = ctk.CTkFrame(window, fg_color=ACCENT, corner_radius=24)
form_outer.pack(fill='both', expand=True, padx=50, pady=(18, 16))

form_card = ctk.CTkFrame(form_outer, fg_color=CARD_BG, corner_radius=20)
form_card.pack(fill='both', expand=True, padx=4, pady=4)
form_card.grid_columnconfigure(0, weight=1)
form_card.grid_columnconfigure(1, weight=0)

username_label = ctk.CTkLabel(form_card, text='Username', font=('Segoe UI', 15, 'bold'), text_color=TEXT)
username_label.grid(row=0, column=0, sticky='w', padx=40, pady=(24, 6))
username_entry = ctk.CTkEntry(form_card, placeholder_text='Enter username', font=('Segoe UI', 14), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=2, corner_radius=14, height=44)
username_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=40, pady=(0, 4))

password_label = ctk.CTkLabel(form_card, text='Password', font=('Segoe UI', 15, 'bold'), text_color=TEXT)
password_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=40, pady=(14, 6))
password_entry = ctk.CTkEntry(form_card, placeholder_text='Enter password', font=('Segoe UI', 14), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=2, corner_radius=14, show='*', height=44)
password_entry.grid(row=3, column=0, sticky='ew', padx=(40, 4), pady=(0, 4))

password_toggle_button = ctk.CTkButton(form_card, width=44, height=44, text='', command=toggle_password,
                                       fg_color=ACCENT, hover_color='#95CEB8', border_width=0, corner_radius=14, image=hide_icon)
password_toggle_button.grid(row=3, column=1, padx=(0, 40), pady=(0, 4), sticky='e')

confirm_label = ctk.CTkLabel(form_card, text='Confirm Password', font=('Segoe UI', 15, 'bold'), text_color=TEXT)
confirm_label.grid(row=4, column=0, columnspan=2, sticky='w', padx=40, pady=(14, 6))
confirm_entry = ctk.CTkEntry(form_card, placeholder_text='Confirm password', font=('Segoe UI', 14), text_color=TEXT,
                             fg_color=ACCENT, border_color=PRIMARY, border_width=2, corner_radius=14, show='*', height=44)
confirm_entry.grid(row=5, column=0, sticky='ew', padx=(40, 4), pady=(0, 4))

confirm_toggle_button = ctk.CTkButton(form_card, width=44, height=44, text='', command=toggle_password,
                                      fg_color=ACCENT, hover_color='#95CEB8', border_width=0, corner_radius=14, image=hide_icon)
confirm_toggle_button.grid(row=5, column=1, padx=(0, 40), pady=(0, 4), sticky='e')

register_button = ctk.CTkButton(form_card, text='Create Account', command=sign_up, fg_color=SECONDARY,
                                hover_color=PRIMARY, font=('Segoe UI', 16, 'bold'), corner_radius=16, height=50)
register_button.grid(row=6, column=0, columnspan=2, padx=40, pady=(20, 14), sticky='ew')

link_row = ctk.CTkFrame(form_card, fg_color='transparent')
link_row.grid(row=7, column=0, columnspan=2, pady=(0, 20))

prompt_label = ctk.CTkLabel(link_row, text='Already have an account?', font=('Segoe UI', 12), text_color=TEXT)
prompt_label.pack(side='left', padx=(0, 4))

sign_in = ctk.CTkButton(link_row, text='Sign in here', command=signin, fg_color='transparent', text_color=SECONDARY,
                        hover_color=ACCENT, font=('Segoe UI', 12, 'bold', 'underline'), width=100, height=28)
sign_in.pack(side='left')

window.mainloop()