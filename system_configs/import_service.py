"""Helpers for importing patient data from external files."""
from __future__ import annotations # Ensure compatibility with future Python versions

from typing import Dict, List, Tuple # For type hinting

import pandas # For data manipulation
from pymysql.err import IntegrityError # For handling database integrity errors

from .helpers import normalize_column_name, normalize_mobile, to_proper_case # Importing helper functions

# Define required columns mapping
REQUIRED_COLUMNS = {
    'patient_id': 'patientid',
    'name': 'name',
    'mobile': 'mobileno',
    'email': 'email',
    'address': 'address',
    'gender': 'gender',
    'dob': 'dateofbirth',
    'diagnosis': 'diagnosis',
    'visit_date': 'visitdate'
}

# Define field labels for error reporting
FIELD_LABELS = {
    'patient_id': 'patient ID',
    'name': 'name',
    'mobile': 'mobile number',
    'email': 'email',
    'address': 'address',
    'gender': 'gender',
    'dob': 'date of birth',
    'diagnosis': 'diagnosis',
    'visit_date': 'visit date'
}

# Import patient records from a DataFrame into the database.
def import_patient_dataframe(data_frame: pandas.DataFrame, cursor, connection) -> Tuple[int, int, List[str]]:
    """Insert patient records from a prepared DataFrame.

    Returns a tuple of (inserted_count, skipped_count, sample_errors).
    """
    if data_frame.empty:
        raise ValueError('The selected file does not contain any records.')

    normalized_to_original = {
        normalize_column_name(col): col for col in data_frame.columns
    }

    resolved_columns: Dict[str, str] = {}
    missing_fields = []
    for field, normalized in REQUIRED_COLUMNS.items():
        if normalized in normalized_to_original:
            resolved_columns[field] = normalized_to_original[normalized]
        else:
            missing_fields.append(field)

    if missing_fields:
        pretty_missing = ', '.join(field.replace('_', ' ').title() for field in missing_fields)
        raise KeyError(f'Missing required columns in file: {pretty_missing}')

    def get_value(row, field: str) -> str:
        value = row[resolved_columns[field]]
        if pandas.isna(value):
            return ''
        return str(value).strip()

    inserted = 0
    skipped = 0
    error_samples: List[str] = []

    for idx, row in data_frame.iterrows():
        excel_row = idx + 2  # account for header row
        patient_id = get_value(row, 'patient_id')
        name = get_value(row, 'name')
        mobile = get_value(row, 'mobile')
        email_value = get_value(row, 'email')
        address_value = get_value(row, 'address')
        gender_value = get_value(row, 'gender')
        dob_value = get_value(row, 'dob')
        diagnosis_value = get_value(row, 'diagnosis')
        visit_date_value = get_value(row, 'visit_date')

        required_values = {
            'patient_id': patient_id,
            'name': name,
            'mobile': mobile,
            'email': email_value,
            'address': address_value,
            'gender': gender_value,
            'dob': dob_value,
            'diagnosis': diagnosis_value,
            'visit_date': visit_date_value
        }

        missing_values = [FIELD_LABELS[key] for key, value in required_values.items() if not value]
        if missing_values:
            skipped += 1
            if len(error_samples) < 5:
                missing_text = ', '.join(missing_values)
                error_samples.append(f'Row {excel_row}: Missing {missing_text}.')
            continue

        formatted_mobile = normalize_mobile(mobile)
        if not formatted_mobile:
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f'Row {excel_row}: Mobile number must follow +63 000 000 0000 format.')
            continue

        name = to_proper_case(name)
        address_value = to_proper_case(address_value)
        diagnosis_value = to_proper_case(diagnosis_value)

        try:
            query = (
                'insert into patient ('
                'patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date'
                ') values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            )
            cursor.execute(query, (
                patient_id, name, formatted_mobile, email_value, address_value, gender_value,
                dob_value, diagnosis_value, visit_date_value
            ))
            connection.commit()
            inserted += 1
        except IntegrityError:
            connection.rollback()
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f'Row {excel_row}: Patient ID already exists.')
        except Exception as exc:  # pylint: disable=broad-except
            connection.rollback()
            skipped += 1
            if len(error_samples) < 5:
                error_samples.append(f'Row {excel_row}: {exc}')

    return inserted, skipped, error_samples
