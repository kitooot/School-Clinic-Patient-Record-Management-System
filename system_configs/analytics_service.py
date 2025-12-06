"""Analytics helpers for patient data visualizations.""" 
from __future__ import annotations # Ensure compatibility with future Python versions

from collections import Counter # For counting hashable objects
from datetime import datetime # For handling date and time
from typing import Dict, Iterable, List, Tuple, Optional # For type hinting

from .helpers import to_proper_case # Importing helper function for proper case conversion

PatientRow = Tuple[str, str, str, str, str, str, str, str, str] # Define a type alias for patient record rows
AnalyticsData = Dict[str, object] # Define a type alias for analytics data dictionary

# define a type alias for patient record rows
def load_all_patients(cursor) -> List[PatientRow]:#
    """Fetch all existing patients from the database."""
    cursor.execute(
        'select patient_id, name, mobile, email, address, gender, dob, diagnosis, visit_date from patient'
    )
    return cursor.fetchall()


# Define a type alias for analytics data dictionary
def compute_analytics(rows: Iterable[PatientRow]) -> AnalyticsData:
    """Aggregate high-level statistics for dashboards and exports."""
    rows = list(rows)
    total = len(rows)

    gender_counts: Counter[str] = Counter()
    municipality_counts: Counter[str] = Counter()
    diagnosis_counts: Counter[str] = Counter()
    month_counts: Counter[str] = Counter()
    month_labels: Dict[str, str] = {}
    latest_visit_dt: Optional[datetime] = None

    for row in rows:
        gender_value = to_proper_case(row[5])
        gender = gender_value or 'Unspecified'
        gender_counts[gender] += 1

        address = row[4] or ''
        parts: List[str] = []
        for part in address.split(','):
            cleaned = to_proper_case(part)
            if cleaned:
                parts.append(cleaned)
        municipality = parts[2] if len(parts) >= 3 else 'Unspecified'
        municipality_counts[municipality] += 1

        diagnosis_value = to_proper_case(row[7])
        diagnosis = diagnosis_value or 'Unspecified'
        diagnosis_counts[diagnosis] += 1

        visit_date = row[8]
        if visit_date:
            try:
                visit_dt = datetime.strptime(visit_date, '%m/%d/%Y')
            except ValueError:
                continue
            key = visit_dt.strftime('%Y-%m')
            month_counts[key] += 1
            month_labels[key] = visit_dt.strftime('%B %Y')
            if latest_visit_dt is None or visit_dt > latest_visit_dt:
                latest_visit_dt = visit_dt

    visits_by_month = [(month_labels[key], month_counts[key]) for key in sorted(month_counts.keys())]

    analytics: AnalyticsData = {
        'total': total,
        'genders': gender_counts.most_common(),
        'municipalities': municipality_counts.most_common(10),
        'diagnoses': diagnosis_counts.most_common(10),
        'visits_by_month': visits_by_month,
        'latest_visit': latest_visit_dt.strftime('%B %d, %Y') if latest_visit_dt else 'N/A'
    }
    return analytics

# Define a type alias for analytics data dictionary
def create_analytics_figures(
    analytics: AnalyticsData,
    figure_cls,
    primary_color: str,
    secondary_color: str
) -> Dict[str, object]:
    """Generate matplotlib figures for the analytics dashboard and exports."""
    if figure_cls is None:
        return {}

    figures: Dict[str, object] = {}

    gender_data = analytics.get('genders') or []
    if gender_data:
        labels = [label for label, _ in gender_data]
        counts = [count for _, count in gender_data]
        fig = figure_cls(figsize=(4.2, 3.2), dpi=100)
        ax = fig.add_subplot(111)

        # Show percentage labels only when a slice has a value.
        def _autopct(pct: float) -> str:
            return f'{pct:.1f}%' if pct > 0 else ''

        ax.pie(counts, labels=labels, autopct=_autopct, startangle=90)
        ax.axis('equal')
        ax.set_title('Gender Distribution', fontsize=12)
        fig.tight_layout()
        figures['gender'] = fig

    diagnosis_data = analytics.get('diagnoses') or []
    top_diagnoses = diagnosis_data[:5]
    if top_diagnoses:
        labels = [label for label, _ in top_diagnoses]
        counts = [count for _, count in top_diagnoses]
        fig = figure_cls(figsize=(4.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        positions = list(range(len(labels)))
        bars = ax.bar(positions, counts, color=primary_color)
        ax.set_title('Top Diagnoses', fontsize=12)
        ax.set_ylabel('Patients')
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=30, ha='right')
        if counts:
            ax.set_ylim(0, max(counts) + 1)
        try:
            ax.bar_label(bars, padding=3, fontsize=9)
        except Exception:
            for rect, value in zip(bars, counts):
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    rect.get_height() + 0.1,
                    str(value),
                    ha='center',
                    va='bottom',
                    fontsize=9
                )
        ax.grid(axis='y', linestyle='--', alpha=0.2)
        fig.tight_layout()
        figures['diagnosis'] = fig

    visits_data = analytics.get('visits_by_month') or []
    recent_visits = visits_data[-12:]
    if recent_visits:
        labels = [label for label, _ in recent_visits]
        counts = [count for _, count in recent_visits]
        positions = list(range(len(labels)))
        fig = figure_cls(figsize=(6.0, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(positions, counts, marker='o', color=secondary_color, linewidth=2)
        ax.set_title('Clinic Visits by Month', fontsize=12)
        ax.set_ylabel('Patients Seen')
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=35, ha='right')
        ax.grid(True, linestyle='--', alpha=0.3)
        fig.tight_layout()
        figures['visits'] = fig

    municipality_data = analytics.get('municipalities') or []
    top_municipalities = municipality_data[:5]
    if top_municipalities:
        labels = [label for label, _ in top_municipalities]
        counts = [count for _, count in top_municipalities]
        fig = figure_cls(figsize=(4.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        positions = list(range(len(labels)))
        bars = ax.barh(positions, counts, color=primary_color)
        ax.set_title('Top Municipalities', fontsize=12)
        ax.set_xlabel('Patients')
        ax.set_yticks(positions)
        ax.set_yticklabels(labels)
        if counts:
            ax.set_xlim(0, max(counts) + 1)
        try:
            ax.bar_label(bars, padding=3, fontsize=9)
        except Exception:
            for rect, value in zip(bars, counts):
                ax.text(
                    rect.get_width() + 0.1,
                    rect.get_y() + rect.get_height() / 2,
                    str(value),
                    va='center',
                    fontsize=9
                )
        ax.grid(axis='x', linestyle='--', alpha=0.2)
        fig.tight_layout()
        figures['municipality'] = fig

    return figures
