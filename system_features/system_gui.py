"""GUI construction helpers for the patient record management system.""" # Ensure compatibility with future Python versions
from __future__ import annotations # Ensure compatibility with future Python versions

from pathlib import Path # For handling file paths
from typing import Any, Callable, Dict, Iterable # Type hinting

import customtkinter as ctk # For custom Tkinter widgets
from tkinter import BOTH, BOTTOM, CENTER, Frame, TclError, VERTICAL, HORIZONTAL, RIGHT, X, Y # For Tkinter components
from tkinter import ttk # For themed widgets
from PIL import Image, ImageTk # For image handling

from system_configs.config import ( # Import color constants
    PRIMARY,
    SECONDARY,
    BG,
    ACCENT,
    TEXT,
    TABLE_BG,
    SIDEBAR_BG,
    HEADER_BG,
    CARD_BG,
    SEARCH_FIELD_OPTIONS,
    SELECTION_MENU_OPTIONS,
)

# Module-level constant for project root and default logo paths.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOGO_CANDIDATES = (
    PROJECT_ROOT / "images" / "logo.png",
    PROJECT_ROOT / "images" / "logoo.png",
)

# Load the sidebar logo image or a placeholder.
def _load_sidebar_logo(
    paths: Iterable[Path] = DEFAULT_LOGO_CANDIDATES,
    size: tuple[int, int] = (120, 120),
) -> ImageTk.PhotoImage:
    """Load the sidebar logo or fall back to a placeholder that matches the theme."""
    for candidate in paths:
        try:
            if candidate.exists():
                image = Image.open(candidate)
                image.thumbnail(size, Image.LANCZOS)
                return ImageTk.PhotoImage(image)
        except Exception:
            continue

    placeholder = Image.new("RGBA", size, ACCENT)
    return ImageTk.PhotoImage(placeholder)

#  Build the main application window and its components.
def build_main_window(
    *,
    add_patient_handler: Callable[[], None],
    delete_patient_handler: Callable[[], None],
    update_patient_handler: Callable[[], None],
    import_handler: Callable[[], None],
    export_handler: Callable[[], None],
    analytics_handler: Callable[[], None],
    exit_handler: Callable[[], None],
    on_search_entry: Callable[[object], None],
    on_search_field_change: Callable[[str], None],
    on_selection_action: Callable[[str], None],
    on_sort_click: Callable[[], None],
    on_patient_details: Callable[[object], None],
    sidebar_side: str,
) -> Dict[str, Any]:
    """Create the main window and return the key UI widgets."""
    root = ctk.CTk()
    ctk.set_appearance_mode('light')
    root.title('School Clinic Patient Record Management System')
    root.configure(bg=BG)

    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    min_width = min(1024, screen_w)
    min_height = min(700, screen_h)
    initial_w = min(max(int(screen_w * 0.85), min_width), screen_w)
    initial_h = min(max(int(screen_h * 0.85), min_height), screen_h)
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

    title_label = ctk.CTkLabel(
        top_frame,
        text='School Clinic Patient Record Management System',
        font=('Segoe UI', 26, 'bold'),
        text_color='white',
        fg_color=HEADER_BG,
        corner_radius=18,
        height=60,
    )
    title_label.grid(row=0, column=0, sticky='ew')

    datetime_label = ctk.CTkLabel(
        top_frame,
        font=('Segoe UI', 12, 'bold'),
        text_color='white',
        fg_color=SECONDARY,
        corner_radius=12,
        padx=14,
        pady=6,
    )
    datetime_label.grid(row=0, column=1, padx=(12, 0), sticky='e')

    body_frame = ctk.CTkFrame(root, fg_color='transparent')
    body_frame.grid(row=1, column=0, sticky='nsew', padx=24, pady=(0, 24))
    body_frame.grid_rowconfigure(0, weight=1)

    if sidebar_side.lower() == 'right':
        sidebar_col, content_col = 1, 0
        sidebar_pad = (18, 0)
        content_pad = (0, 18)
    else:
        sidebar_col, content_col = 0, 1
        sidebar_pad = (0, 18)
        content_pad = (18, 0)

    body_frame.grid_columnconfigure(content_col, weight=1)
    body_frame.grid_columnconfigure(sidebar_col, weight=0, minsize=260)

    sidebar_frame = ctk.CTkFrame(body_frame, fg_color=SIDEBAR_BG, corner_radius=20)
    sidebar_frame.grid(row=0, column=sidebar_col, sticky='nsew', padx=sidebar_pad)
    sidebar_frame.grid_columnconfigure(0, weight=1)

    content_frame = ctk.CTkFrame(body_frame, fg_color=ACCENT, corner_radius=24)
    content_frame.grid(row=0, column=content_col, sticky='nsew', padx=content_pad)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(1, weight=1)

    logo_outer = ctk.CTkFrame(sidebar_frame, fg_color=ACCENT, corner_radius=70, width=140, height=140, border_width=3, border_color=PRIMARY)
    logo_outer.grid(row=0, column=0, pady=16, padx=0)
    logo_outer.grid_propagate(False)

    logo_inner = ctk.CTkFrame(logo_outer, fg_color='transparent', corner_radius=60, width=120, height=120)
    logo_inner.place(relx=0.5, rely=0.5, anchor='center')

    logo_image = _load_sidebar_logo()
    logo_label = ctk.CTkLabel(logo_inner, image=logo_image, text='')
    logo_label.image = logo_image  # prevent garbage collection
    logo_label.place(relx=0.5, rely=0.5, anchor='center')

    button_kwargs = dict(
        fg_color=CARD_BG,
        hover_color=ACCENT,
        text_color=TEXT,
        corner_radius=14,
        font=('Segoe UI', 14, 'bold'),
        height=44,
        border_width=2,
        border_color=PRIMARY,
    )

    ctk.CTkButton(sidebar_frame, text='Add Patient', command=add_patient_handler, **button_kwargs).grid(row=1, column=0, pady=8, padx=10, sticky='ew')
    ctk.CTkButton(sidebar_frame, text='Delete Patient', command=delete_patient_handler, **button_kwargs).grid(row=2, column=0, pady=8, padx=10, sticky='ew')
    ctk.CTkButton(sidebar_frame, text='Update Patient', command=update_patient_handler, **button_kwargs).grid(row=3, column=0, pady=8, padx=10, sticky='ew')
    ctk.CTkButton(sidebar_frame, text='Import Patients', command=import_handler, **button_kwargs).grid(row=4, column=0, pady=8, padx=10, sticky='ew')
    ctk.CTkButton(sidebar_frame, text='Export Patients', command=export_handler, **button_kwargs).grid(row=5, column=0, pady=8, padx=10, sticky='ew')
    ctk.CTkButton(sidebar_frame, text='View Analytics', command=analytics_handler, **button_kwargs).grid(row=6, column=0, pady=8, padx=10, sticky='ew')
    ctk.CTkButton(sidebar_frame, text='Exit', command=exit_handler, fg_color='#e74c3c', hover_color='#c0392b', text_color='white', font=('Segoe UI', 14, 'bold'), corner_radius=14, height=44).grid(row=7, column=0, pady=12, padx=10, sticky='ew')

    header_frame = ctk.CTkFrame(content_frame, fg_color='transparent')
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
        command=on_search_field_change,
        fg_color=SECONDARY,
        button_color=SECONDARY,
        button_hover_color=PRIMARY,
        font=('Segoe UI', 13),
    )
    search_field_menu.grid(row=0, column=0, padx=(0, 8), sticky='e')

    search_entry = ctk.CTkEntry(control_frame, placeholder_text='Search patients...', width=220, font=('Segoe UI', 13))
    search_entry.grid(row=0, column=1, padx=(0, 8), sticky='e')
    search_entry.bind('<KeyRelease>', lambda event: on_search_entry(event))
    search_entry.bind('<Return>', lambda event: on_search_entry(event))

    sort_button = ctk.CTkButton(
        control_frame,
        text='Sort',
        command=on_sort_click,
        fg_color=SECONDARY,
        hover_color=PRIMARY,
        font=('Segoe UI', 13, 'bold'),
        corner_radius=12,
        width=80,
        height=36,
    )
    sort_button.grid(row=0, column=2, sticky='e')

    selection_action_var = ctk.StringVar(value=SELECTION_MENU_OPTIONS[0])
    selection_menu = ctk.CTkOptionMenu(
        control_frame,
        values=SELECTION_MENU_OPTIONS,
        variable=selection_action_var,
        command=on_selection_action,
        fg_color=SECONDARY,
        button_color=SECONDARY,
        button_hover_color=PRIMARY,
        font=('Segoe UI', 13),
        width=125,
    )
    selection_menu.grid(row=0, column=3, padx=(8, 0), sticky='e')

    table_container = ctk.CTkFrame(content_frame, fg_color=CARD_BG, corner_radius=20)
    table_container.grid(row=1, column=0, sticky='nsew', padx=24, pady=(0, 24))

    tree_frame = Frame(table_container, bg=CARD_BG, bd=0, highlightthickness=0)
    tree_frame.pack(fill=BOTH, expand=1, padx=16, pady=16)

    scroll_bar_y = ttk.Scrollbar(tree_frame, orient=VERTICAL)
    scroll_bar_y.pack(side=RIGHT, fill=Y)

    scroll_bar_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
    scroll_bar_x.pack(side=BOTTOM, fill=X)

    patient_table = ttk.Treeview(
        tree_frame,
        columns=(
            'Patient ID', 'Name', 'Mobile No.', 'Email', 'Address', 'Gender', 'Date of Birth', 'Diagnosis', 'Visit Date'
        ),
        xscrollcommand=scroll_bar_x.set,
        yscrollcommand=scroll_bar_y.set,
        show='headings',
        selectmode='extended',
    )
    patient_table.pack(fill=BOTH, expand=1)

    patient_table.bind('<Double-1>', on_patient_details)
    patient_table.bind('<Return>', on_patient_details)

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

    # Return key UI components for further manipulation.
    return {
        'root': root,
        'datetime_label': datetime_label,
        'search_entry': search_entry,
        'search_field_var': search_field_var,
        'selection_action_var': selection_action_var,
        'patient_table': patient_table,
    }
