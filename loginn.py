from tkinter import * # Import all necessary tkinter components
from tkinter import messagebox # For displaying message boxes
from pathlib import Path # For file path operations
import customtkinter as ctk # Custom Tkinter for enhanced UI components
from PIL import Image  # For image handling

from system_configs.config import PRIMARY, SECONDARY, BG, ACCENT, TEXT, CARD_BG # Import color constants from config
from system_configs.database import db_connection, db_cursor # Import database connection


_next_action = None  # Track which window to launch after login UI closes
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

# Helper function to show launch error messages
def _show_launch_error(exc: Exception) -> None:
    fallback = Tk()
    fallback.withdraw()
    messagebox.showerror('Error', f'Failed to start system: {exc}\n\nCheck the terminal for full traceback.')
    fallback.destroy()

# Function to perform the scheduled transition
def _perform_transition() -> None:
    global _next_action
    target = _next_action
    if target is None:
        return

    _next_action = None
    root.destroy()

    if target == 'system':
        try:
            import system  # pylint: disable=import-outside-toplevel
            system.main()
        except Exception as exc:  # pylint: disable=broad-except
            _show_launch_error(exc)
    elif target == 'signup':
        import signup  # pylint: disable=import-outside-toplevel,unused-import

# Function to schedule the transition to another window
def _schedule_transition(target: str) -> None:
    global _next_action
    _next_action = target
    root.after(10, _perform_transition)

# Initialize main window
root = ctk.CTk()
root.title('School Clinic - Staff Login')
ctk.set_appearance_mode('light')

# Center window on screen with better dimensions
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
win_w, win_h = 600, 700
pos_x = (screen_w - win_w) // 2
pos_y = (screen_h - win_h) // 2
root.geometry(f'{win_w}x{win_h}+{pos_x}+{pos_y}')
root.configure(bg=BG)
root.resizable(False, False)

# Placeholder settings
PLACEHOLDER_COLOR = '#95a5a6'
USER_PH = 'Enter username'
PASS_PH = 'Enter password'

# Helper function to load icons with error handling
def _load_icon(path, size=(20, 20)):
    image_path = IMAGES_DIR / path
    try:
        return ctk.CTkImage(Image.open(image_path), size=size)
    except Exception:
        return None

# Function to handle sign-in logic
def sign_in():
    username = username_entry.get().strip()
    passwrd = password_entry.get()

    if not username:
        messagebox.showerror('Error', 'Username cannot be empty')
        return
    
    if not passwrd:
        messagebox.showerror('Error', 'Password cannot be empty')
        return

    try:
        db_cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        result = db_cursor.fetchone()
        
        if result and result[0] == passwrd:
            messagebox.showinfo('Login', 'Login successful — welcome')
            _schedule_transition('system')
        else:
            messagebox.showerror('Invalid', 'Invalid staff username or password')
    except Exception as e:
        messagebox.showerror('Error', f'Database error: {e}')

# Function to switch to sign-up window
def signup():
    _schedule_transition('signup')

# Function to toggle password visibility
def toggle_password():
    # Respect placeholders: only toggle when real text is present
    if show_password.get():
        password_entry.configure(show='*')
        if hide_icon is not None:
            password_toggle_button.configure(image=hide_icon)
        show_password.set(False)
    else:
        password_entry.configure(show='')
        if show_icon is not None:
            password_toggle_button.configure(image=show_icon)
        show_password.set(True)

# State trackers and icon assets
show_password = BooleanVar(value=False)
hide_icon = _load_icon('hidden.png')
show_icon = _load_icon('eye.png')

# Function to load logo image with fallback
def _load_logo(filenames=('logoo.png', 'logo.png')):
    for name in filenames:
        candidate = IMAGES_DIR / name
        if candidate.exists():
            try:
                img_pil = Image.open(candidate)
                img_pil.thumbnail((120, 120))
                return ctk.CTkImage(img_pil, size=img_pil.size)
            except Exception:
                continue
    placeholder = Image.new('RGBA', (120, 120), ACCENT)
    return ctk.CTkImage(placeholder, size=(120, 120))
    
# Header section with gradient-like layering
header_container = ctk.CTkFrame(root, fg_color='transparent')
header_container.pack(fill='x', pady=(20, 0))

logo_image = _load_logo()
logo_outer = ctk.CTkFrame(header_container, fg_color=ACCENT, corner_radius=80, width=160, height=160, border_width=3, border_color=PRIMARY)
logo_outer.pack(anchor='center')
logo_outer.pack_propagate(False)

logo_inner = ctk.CTkFrame(logo_outer, fg_color='white', corner_radius=72, width=144, height=144)
logo_inner.place(relx=0.5, rely=0.5, anchor='center')
logo_label = ctk.CTkLabel(logo_inner, image=logo_image, text='')
logo_label.place(relx=0.5, rely=0.5, anchor='center')

title_label = ctk.CTkLabel(header_container, text='Staff Login', font=('Segoe UI', 32, 'bold'), text_color='white', fg_color=PRIMARY,
                           corner_radius=20, padx=48, pady=12)
title_label.pack(pady=(18, 0), anchor='center')

subtitle_label = ctk.CTkLabel(header_container, text='Welcome back! Please sign in to continue', font=('Segoe UI', 12), text_color=TEXT)
subtitle_label.pack(pady=(6, 0), anchor='center')

# Form card with shadow effect
form_outer = ctk.CTkFrame(root, fg_color=ACCENT, corner_radius=24)
form_outer.pack(fill='both', expand=True, padx=50, pady=(20, 16))

form_card = ctk.CTkFrame(form_outer, fg_color=CARD_BG, corner_radius=20)
form_card.pack(fill='both', expand=True, padx=4, pady=4)
form_card.grid_columnconfigure(0, weight=1)
form_card.grid_columnconfigure(1, weight=0)

username_label = ctk.CTkLabel(form_card, text='Username', font=('Segoe UI', 15, 'bold'), text_color=TEXT)
username_label.grid(row=0, column=0, sticky='w', padx=40, pady=(24, 6))
username_entry = ctk.CTkEntry(form_card, placeholder_text=USER_PH, font=('Segoe UI', 14), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=2, corner_radius=14, height=44)
username_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=40)

password_label = ctk.CTkLabel(form_card, text='Password', font=('Segoe UI', 15, 'bold'), text_color=TEXT)
password_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=40, pady=(18, 6))

password_entry = ctk.CTkEntry(form_card, placeholder_text=PASS_PH, font=('Segoe UI', 14), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=2, corner_radius=14, show='*', height=44)
password_entry.grid(row=3, column=0, sticky='ew', padx=(40, 4), pady=(0, 8))

password_toggle_button = ctk.CTkButton(form_card, width=44, height=44, text='', command=toggle_password,
                                       fg_color=ACCENT, hover_color='#95CEB8', border_width=0, corner_radius=14, image=hide_icon)
password_toggle_button.grid(row=3, column=1, padx=(0, 40), pady=(0, 8), sticky='e')

sign_in_button = ctk.CTkButton(form_card, text='Sign In', command=sign_in, fg_color=SECONDARY,
                               hover_color=PRIMARY, font=('Segoe UI', 16, 'bold'), corner_radius=16, height=50)
sign_in_button.grid(row=4, column=0, columnspan=2, padx=40, pady=(24, 16), sticky='ew')

link_row = ctk.CTkFrame(form_card, fg_color='transparent')
link_row.grid(row=5, column=0, columnspan=2, pady=(0, 24))

question_label = ctk.CTkLabel(link_row, text="Don't have an account?", font=('Segoe UI', 12), text_color=TEXT)
question_label.pack(side='left', padx=(0, 4))

sign_up_button = ctk.CTkButton(link_row, text='Register here', command=signup, fg_color='transparent', text_color=SECONDARY,
                               hover_color=ACCENT, font=('Segoe UI', 12, 'bold', 'underline'), width=100, height=28)
sign_up_button.pack(side='left')

root.mainloop()