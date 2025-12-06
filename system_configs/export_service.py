"""Export helpers for patient records and analytics."""
from __future__ import annotations # Ensure compatibility with future Python versions

from datetime import datetime # For handling date and time
import os # For file system operations
import tempfile # For creating temporary files
from typing import List # For type hinting

import pandas # For data manipulation and Excel export

from .analytics_service import compute_analytics, create_analytics_figures, load_all_patients #  Importing analytics functions
from .helpers import normalize_mobile # Importing helper function for mobile number normalization

# Export all patient records to an Excel file.
def export_patient_records_excel(cursor, file_path: str) -> None:
    """Write all patients to an Excel workbook."""
    rows = load_all_patients(cursor)
    if not rows:
        raise ValueError('There are no patient records to export.')

    headers = [
        'Patient ID',
        'Name',
        'Mobile No.',
        'Email',
        'Address',
        'Gender',
        'Date of Birth',
        'Diagnosis',
        'Visit Date'
    ]
    formatted_rows = []
    for row in rows:
        formatted_rows.append([
            str(row[0] or ''),
            str(row[1] or ''),
            normalize_mobile(row[2]) or str(row[2] or ''),
            str(row[3] or ''),
            str(row[4] or ''),
            str(row[5] or ''),
            str(row[6] or ''),
            str(row[7] or ''),
            str(row[8] or '')
        ])

    table = pandas.DataFrame(formatted_rows, columns=headers)
    table.to_excel(file_path, index=False)

# Generate a PDF file summarizing patient analytics.
def export_patient_analytics_pdf(
    cursor,
    file_path: str,
    fpdf_cls,
    figure_cls,
    primary_color: str,
    secondary_color: str
) -> None:
    """Generate a PDF file summarizing patient analytics."""
    analytics = compute_analytics(load_all_patients(cursor))

    pdf = fpdf_cls(unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Patient Analytics', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Generated on {datetime.now().strftime("%B %d, %Y %I:%M %p")}', 0, 1, 'C')
    pdf.ln(4)

    if analytics['total'] == 0:
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, 'No patient records available for analytics.', 0, 1, 'C')
        pdf.output(file_path)
        return

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Total Patients: {analytics['total']}", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f"Most Recent Visit: {analytics['latest_visit']}", 0, 1)
    pdf.ln(3)

    figures = create_analytics_figures(analytics, figure_cls, primary_color, secondary_color)
    chart_titles = {
        'gender': 'Gender Distribution',
        'diagnosis': 'Top Diagnoses',
        'municipality': 'Top Municipalities',
        'visits': 'Clinic Visits by Month'
    }

    temp_files: List[str] = []
    try:
        for key in ('gender', 'diagnosis', 'municipality', 'visits'):
            fig = figures.get(key)
            title = chart_titles.get(key, key.title())

            if fig is None:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, title, 0, 1, 'C')
                pdf.set_font('Arial', '', 11)
                pdf.ln(4)
                pdf.multi_cell(0, 7, 'No data available for this chart.')
                continue

            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            tmp_file.close()
            temp_files.append(tmp_file.name)
            fig.savefig(tmp_file.name, dpi=180, bbox_inches='tight')

            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, title, 0, 1, 'C')
            pdf.ln(4)

            max_width = pdf.w - 20
            pdf.image(tmp_file.name, x=10, w=max_width)

        pdf.output(file_path)
    finally:
        for path in temp_files:
            try:
                os.remove(path)
            except OSError:
                pass
