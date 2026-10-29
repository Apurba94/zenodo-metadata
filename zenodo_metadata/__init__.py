"""Build and validate .zenodo.json deposit metadata."""
from .core import build, validate, from_cff_dict, UPLOAD_TYPES

__version__ = "0.1.0"
__all__ = ["build", "validate", "from_cff_dict", "UPLOAD_TYPES"]
