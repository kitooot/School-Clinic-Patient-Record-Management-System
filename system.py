"""Entry point for the School Clinic patient record management system."""
from __future__ import annotations

import importlib
import time
from tkinter import messagebox

from system_configs.config import (
    DATE_SORT_FIELDS,
    PRIMARY,
    SECONDARY,
    SEARCH_FIELD_OPTIONS,
    SELECTION_MENU_OPTIONS,
    SIDEBAR_SIDE,
    SORT_FIELD_LABELS,
    SORT_FIELD_OPTIONS,
)
from system_configs.analytics_service import compute_analytics, create_analytics_figures, load_all_patients
from system_configs.database import db_connection, db_cursor
from system_configs.export_service import export_patient_analytics_pdf, export_patient_records_excel
from system_configs.helpers import normalize_column_name, normalize_mobile, to_proper_case
from system_features import analytics as analytics_feature
from system_features import crud as crud_feature
from system_features import import_export as import_export_feature
from system_features import search as search_feature
from system_features import selection as selection_feature
from system_features import sorting as sorting_feature
from system_features.system_gui import build_main_window

# Dependency checks for optional libraries.
try:
    FPDF = importlib.import_module('fpdf').FPDF
except (ImportError, AttributeError):
    FPDF = None

try:
    matplotlib = importlib.import_module('matplotlib')
    matplotlib.use('TkAgg')
    Figure = importlib.import_module('matplotlib.figure').Figure
    FigureCanvasTkAgg = importlib.import_module('matplotlib.backends.backend_tkagg').FigureCanvasTkAgg
except Exception:
    Figure = None
    FigureCanvasTkAgg = None
    matplotlib = None

try:
    importlib.import_module('openpyxl')
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

CONNECTION = db_connection
CURSOR = db_cursor


def _load_patient_rows():
    return load_all_patients(CURSOR)


def _compute_patient_analytics():
    return compute_analytics(_load_patient_rows())


def _create_patient_analytics_figures(analytics):
    return create_analytics_figures(analytics, Figure, PRIMARY, SECONDARY)


def main():
    root_ref = {}

    def exit_application() -> None:
        app_root = root_ref.get('root')
        if app_root is None:
            return
        if messagebox.askyesno('Exit', 'Do you want to exit?'):
            app_root.destroy()

    components = build_main_window(
        add_patient_handler=crud_feature.add_patient,
        delete_patient_handler=crud_feature.delete_patient,
        update_patient_handler=crud_feature.update_patient,
        import_handler=import_export_feature.import_data,
        export_handler=lambda: import_export_feature.export_data(PRIMARY, SECONDARY),
        analytics_handler=analytics_feature.show_analytics_window,
        exit_handler=exit_application,
        on_search_entry=search_feature.on_search_entry_change,
        on_search_field_change=search_feature.on_search_field_change,
        on_selection_action=selection_feature.on_selection_action,
        on_sort_click=sorting_feature.open_sort_dialog,
        on_patient_details=crud_feature.show_patient_details,
        sidebar_side=SIDEBAR_SIDE,
    )

    root = components['root']
    root_ref['root'] = root
    datetime_label = components['datetime_label']
    search_entry = components['search_entry']
    search_field_var = components['search_field_var']
    selection_action_var = components['selection_action_var']
    patient_table = components['patient_table']

    def current_date() -> str:
        return time.strftime('%m/%d/%Y')

    def refresh_table() -> None:
        crud_feature.show_patient()

    def update_clock() -> None:
        datetime_label.configure(
            text=f"  Date: {time.strftime('%m/%d/%Y')}\nTime: {time.strftime('%H:%M:%S')}"
        )
        datetime_label.after(1000, update_clock)

    search_feature.configure(
        search_entry=search_entry,
        search_field_var=search_field_var,
        search_field_options=SEARCH_FIELD_OPTIONS,
        refresh_callback=refresh_table,
    )

    selection_feature.configure(
        patient_table=patient_table,
        root=root,
        selection_action_var=selection_action_var,
        selection_menu_options=SELECTION_MENU_OPTIONS,
    )

    sorting_feature.configure(
        cursor=CURSOR,
        sort_field_options=SORT_FIELD_OPTIONS,
        sort_field_labels=SORT_FIELD_LABELS,
        date_sort_fields=DATE_SORT_FIELDS,
        root=root,
        refresh_callback=refresh_table,
    )

    crud_feature.configure(
        patient_table=patient_table,
        cursor=CURSOR,
        connection=CONNECTION,
        root=root,
        fetch_patients=sorting_feature.fetch_patients,
        get_filter=search_feature.get_filter,
        get_current_date=current_date,
        normalize_mobile=normalize_mobile,
        to_proper_case=to_proper_case,
    )

    import_export_feature.configure(
        cursor=CURSOR,
        connection=CONNECTION,
        root=root,
        refresh_callback=refresh_table,
        has_openpyxl=HAS_OPENPYXL,
        fpdf_cls=FPDF,
        figure_cls=Figure,
        export_records_fn=export_patient_records_excel,
        export_analytics_fn=export_patient_analytics_pdf,
        normalize_mobile=normalize_mobile,
        normalize_column_name=normalize_column_name,
        to_proper_case=to_proper_case,
    )

    analytics_feature.configure(
        compute_analytics=_compute_patient_analytics,
        create_analytics_figures=_create_patient_analytics_figures,
        root=root,
        figure_cls=Figure,
        figure_canvas_cls=FigureCanvasTkAgg,
    )

    update_clock()
    refresh_table()
    root.mainloop()


if __name__ == '__main__':
    main()