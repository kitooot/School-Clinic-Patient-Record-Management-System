# School Clinic Patient Record Management System

## Overview
School Clinic Patient Record Management System is a Python desktop application that streamlines patient intake, visit tracking, and analytics for school clinic staff. The project combines a modern CustomTkinter interface with a MySQL backend to provide a responsive, dependable workflow for day-to-day clinic operations.

## Key Features
- **Secure Staff Access** – Dedicated signup and login windows grant controlled access to authorized staff members.
- **Patient CRUD** – Add, view, update, and delete patient records with validation to prevent inconsistent data.
- **Smart Search & Sorting** – Filter records by field, apply alphabetical or date-based ordering, and leverage multi-select actions.
- **Import & Export** – Bulk import patient data from Excel or CSV, and export records or analytics for reporting.
- **Interactive Dashboards** – Visualize visit trends, diagnoses, and other insights using Matplotlib-powered charts.
- **Responsive UI Layout** – CustomTkinter styling keeps the interface clean, accessible, and consistent across screens.

## Technology Stack
- **Language:** Python 3.10+
- **GUI:** CustomTkinter & standard tkinter widgets
- **Database:** MySQL via PyMySQL
- **Data Processing:** pandas, openpyxl (Excel support)
- **Reporting:** Matplotlib, FPDF (PDF analytics export)

## Project Structure
```
School-Clinic-Patient-Record-Management-System/
├── images/                         # UI assets (logos, icons)
├── system.py                      # Application entry point
├── loginn.py                      # Staff login window
├── signup.py                      # New staff registration window
├── system_features/               # Modularized feature logic
│   ├── crud.py                    # Patient add/update/delete routines
│   ├── import_export.py           # Import/export dialogs and processing
│   ├── analytics.py               # Analytics window and chart handling
│   ├── search.py                  # Search field wiring and filters
│   ├── sorting.py                 # Sorting dialog and query helpers
│   ├── selection.py               # Batch selection utilities
│   └── system_gui.py              # Layout builder for the main window
├── system_configs/                # Shared configuration and services
│   ├── config.py                  # Theme colours, constants, options
│   ├── database.py                # Connection helpers and schema setup
│   ├── analytics_service.py       # Aggregation for charts and reports
│   ├── helpers.py                 # Normalization utilities
│   ├── import_service.py          # Data import validation helpers
│   └── export_service.py          # Excel/PDF export utilities
└── README.md
```

## Prerequisites
- Python 3.10 or newer installed and available on PATH
- MySQL Server running locally (default connection targets `localhost`, user `root`, blank password)
- Git (optional, for cloning the repository)

Python dependencies are managed manually; recommended packages include:
- `customtkinter`
- `pymysql`
- `pandas`
- `openpyxl`
- `matplotlib`
- `fpdf`

Install them with:
```powershell
pip install customtkinter pymysql pandas openpyxl matplotlib fpdf
```

## Initial Setup
1. **Clone or download** the repository to your local machine.
2. **Configure MySQL** so the credentials in `system_configs/database.py` match your environment (default: `root` user with no password).
3. **Run the schema bootstrap** – launching the app automatically calls `ensure_schema()` to create the `clinicmanagementsystem` database with `patient` and `users` tables.
4. **Prepare assets** – ensure logo images exist under `images/` (e.g., `logo.png`). The UI falls back to a placeholder if absent.

## Running the Application
1. **Register Staff Account** (first-time use):
	```powershell
	python signup.py
	```
	Complete the form to insert a new user into the database.

2. **Login and Launch Main System**:
	```powershell
	python loginn.py
	```
	Enter valid credentials. Upon successful login the main system window starts.

3. **Direct Launch (optional during development)**:
	```powershell
	python system.py
	```
	This bypasses the login step, launching the main dashboard immediately.

## Core Workflows
- **Add Patient:** Use *Add Patient* button, fill the form (required fields, validated mobile format), and submit.
- **Update/Delete:** Select a record in the table, then choose *Update Patient* or *Delete Patient*.
- **Search & Sort:** Use the search field with dropdown to filter records; click *Sort* to open the sort dialog.
- **Selection Actions:** Dropdown options allow selecting all, clearing selection, or choosing specific patients via list.
- **Import:** *Import Patients* accepts Excel/CSV files; ensure columns match required headers.
- **Export:** *Export Patients* saves records to Excel; *View Analytics* then *Export Analytics* produces PDF summaries.

## Database Schema Summary
- **patient**
  - `patient_id` (VARCHAR, PK)
  - `name`, `mobile`, `email`, `address`, `gender` (VARCHAR)
  - `dob`, `visit_date` (DATE)
  - `diagnosis` (VARCHAR)
- **users**
  - `username` (VARCHAR, PK)
  - `password` (VARCHAR)

> **Note:** If you migrate the date columns to DATE types, validate incoming data in `import_service` to ensure `YYYY-MM-DD` formatting.

## Configuration Highlights
- **Theme Colours & UI Constants** – defined in `system_configs/config.py` for consistent styling.
- **Image Paths** – resolved via `pathlib` in GUI modules, so relative paths remain robust.
- **Optional Dependencies** – `system.py` gracefully handles missing Matplotlib/FPDF/OpenPyXL (certain features will alert users when required packages are not installed).

## Troubleshooting
- **Login does not open main window** – ensure `system.main()` is invoked after import (already fixed in `loginn.py`).
- **Import errors** – Check column headers and date formats; see `system_configs/import_service.py` for accepted schemas.
- **Matplotlib/FPDF missing** – Install the packages; analytics export/visualization relies on them.
- **Database connection failures** – Verify MySQL credentials and server availability.

## Contributing
1. Create a new branch for your feature or fix.
2. Follow existing code style (use descriptive function names and minimal comments for complex blocks).
3. Test workflows (signup, login, CRUD, import/export).
4. Create a pull request summarizing changes, new dependencies, and testing performed.

## License
This project is distributed for educational purposes. Adapt or extend it to fit your institution’s needs.

---
For questions or enhancements, open an issue or reach out to the repository maintainer.
