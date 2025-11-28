# Application-wide configuration values and constants.

# UI Colors
PRIMARY = '#2ECC71'   # Mint Green
SECONDARY = '#16A085' # Deep Teal
BG = '#ECF0F1'        # Light Gray White (used for contrast when needed)
ACCENT = '#A3E4D7'    # Soft Mint
TEXT = '#2C3E50'      # Deep Gray Blue
TABLE_BG = '#F5FFFB'  # Pale Mint for table rows
SIDEBAR_BG = SECONDARY
HEADER_BG = PRIMARY
CARD_BG = '#FFFFFF'

# Layout options
SIDEBAR_SIDE = 'left'  # set to 'right' if the sidebar should appear on the right

# Search and sorting options shared by the UI
SEARCH_FIELD_OPTIONS = {
    'Patient ID': 'patient_id',
    'Name': 'name',
    'Mobile No.': 'mobile',
    'Email': 'email',
    'Address': 'address',
    'Gender': 'gender',
    'Date of Birth': 'dob',
    'Diagnosis': 'diagnosis',
    'Visit Date': 'visit_date'
}

SORT_FIELD_OPTIONS = {
    'Patient ID': 'patient_id',
    'Name': 'name',
    'Date of Birth': 'dob',
    'Visit Date': 'visit_date'
}

SORT_FIELD_LABELS = {value: key for key, value in SORT_FIELD_OPTIONS.items()}
DATE_SORT_FIELDS = {'dob', 'visit_date'}

SELECTION_MENU_OPTIONS = ['Selection...', 'Select Specific Patients', 'Select All Patients', 'Clear Selection']
