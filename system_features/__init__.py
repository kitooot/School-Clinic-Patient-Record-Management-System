"""Feature-specific modules for the system UI."""

from . import crud # CRUD operations for patient records.
from . import import_export # Import and export functionalities.
from . import analytics # Analytics window and functionalities.
from . import search # Search and filter helpers.
from . import sorting # Sorting helpers.
from . import selection # Selection helpers.

# Exported module features.
__all__ = ['crud', 'import_export', 'analytics', 'search', 'sorting', 'selection']
