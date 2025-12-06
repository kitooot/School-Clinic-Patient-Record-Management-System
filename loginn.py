from tkinter import * # Import all necessary tkinter components
from tkinter import messagebox # For displaying message boxes
import ast # For safely evaluating string representations of Python data structures
import os # For file path operations
import customtkinter as ctk # Custom Tkinter for enhanced UI components
from PIL import Image  # For image handling

from config import PRIMARY, SECONDARY, BG, ACCENT, TEXT, CARD_BG # Import color constants from config


_next_action = None  # Track which window to launch after login UI closes

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
            import system  # pylint: disable=import-outside-toplevel,unused-import
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
root.geometry('550x550+300+200')
ctk.set_appearance_mode('light')

root.configure(bg=BG)
root.resizable(False, False)

# Placeholder settings
PLACEHOLDER_COLOR = '#95a5a6'
USER_PH = 'Enter username'
PASS_PH = 'Enter password'

# Helper function to load icons with error handling
def _load_icon(path, size=(20, 20)):
    try:
        return ctk.CTkImage(Image.open(path), size=size)
    except Exception:
        return None

# Function to handle sign-in logic
def sign_in():
    username = username_entry.get().strip()
    passwrd = password_entry.get()

    # Safe read of data.txt
    if not os.path.exists('data.txt'):
        messagebox.showerror('Error', 'No users found. Please register first.')
        return

    try:
        with open('data.txt', 'r') as file:
            d = file.read().strip()
            if not d:
                messagebox.showerror('Error', 'User database is empty. Please register first.')
                return
            r = ast.literal_eval(d)
    except Exception as e:
        messagebox.showerror('Error', f'Failed to read user data: {e}')
        return

    if username in r and passwrd == r[username]:
        messagebox.showinfo('Login', 'Login successful — welcome')
        _schedule_transition('system')
    else:
        messagebox.showerror('Invalid', 'Invalid staff username or password')

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
def _load_logo(filenames=('logoo.png')):
    try:
        img_pil = Image.open('logoo.png')
        img_pil.thumbnail((120, 120))  
        return ctk.CTkImage(img_pil, size=img_pil.size)
    except Exception:
        placeholder = Image.new('RGBA', (120, 120), ACCENT)  # Create a placeholder image with ACCENT color
        return ctk.CTkImage(placeholder, size=(120, 120))
logo_image = _load_logo()
logo_frame = ctk.CTkFrame(root, fg_color='transparent' ,corner_radius=20, width=120, height=120, border_width=2, border_color=PRIMARY)
logo_frame.place(relx=0.5, rely=0.12, anchor='center')
logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text='')
logo_label.place(relx=0.5, rely=0.5, anchor='center')

title_label = ctk.CTkLabel(root, text='Staff Login', font=('Segoe UI', 26, 'bold'), text_color=TEXT, fg_color=PRIMARY,
                           corner_radius=16, padx=24, pady=6)
title_label.place(relx=0.5, rely=0.26, anchor='center')

form_card = ctk.CTkFrame(root, fg_color=CARD_BG, corner_radius=20)
form_card.place(relx=0.5, rely=0.62, anchor='center', relwidth=0.65, relheight=0.6)

link_row = ctk.CTkFrame(root, fg_color=CARD_BG)
link_row.place(relx=0.5, rely=0.85, anchor='center')
link_row.grid_columnconfigure(0, weight=0)
link_row.grid_columnconfigure(1, weight=0)

question_label = ctk.CTkLabel(link_row, text="Don't have an account?", font=('Segoe UI', 11), text_color=TEXT)
question_label.grid(row=0, column=0, sticky='e')

sign_up_button = ctk.CTkButton(link_row, text='Register', command=signup, fg_color='transparent', text_color=SECONDARY,
                               hover_color=ACCENT, font=('Segoe UI', 11, 'bold'), width=90)
sign_up_button.grid(row=0, column=1, padx=(12, 0), sticky='w')
form_card.grid_columnconfigure(0, weight=1)
form_card.grid_columnconfigure(1, weight=0)

username_label = ctk.CTkLabel(form_card, text='Username', font=('Segoe UI', 14, 'bold'), text_color=TEXT)
username_label.grid(row=0, column=0, sticky='w', padx=32, pady=(32, 6))
username_entry = ctk.CTkEntry(form_card, placeholder_text=USER_PH, font=('Segoe UI', 13), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=1, corner_radius=12, height=34)
username_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=32)

password_label = ctk.CTkLabel(form_card, text='Password', font=('Segoe UI', 14, 'bold'), text_color=TEXT)
password_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=32, pady=(24, 6))

password_entry = ctk.CTkEntry(form_card, placeholder_text=PASS_PH, font=('Segoe UI', 13), text_color=TEXT,
                              fg_color=ACCENT, border_color=PRIMARY, border_width=1, corner_radius=12, show='*', height=34)
password_entry.grid(row=3, column=0, sticky='ew', padx=(32, 4), pady=(0, 4))

password_toggle_button = ctk.CTkButton(form_card, width=36, height=34, text='', command=toggle_password,
                                       fg_color=ACCENT, hover_color=ACCENT, border_width=0, image=hide_icon)
password_toggle_button.grid(row=3, column=1, padx=(0, 32), pady=(0, 4), sticky='e')

sign_in_button = ctk.CTkButton(form_card, text='Sign In', command=sign_in, fg_color=SECONDARY,
                               hover_color=PRIMARY, font=('Segoe UI', 14, 'bold'), corner_radius=14)
sign_in_button.grid(row=4, column=0, columnspan=2, padx=32, pady=(36, 12), sticky='ew')

root.mainloop()