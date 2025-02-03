# scf_converter/utils/error_handling.py

class ConfigError(Exception):
    """Raised for critical user config issues."""
    pass

class CSVError(Exception):
    """Raised for critical CSV input issues."""
    pass

class FormatError(Exception):
    """Raised for invalid data formats (dates, decimals, etc.)."""
    pass

import contextlib

@contextlib.contextmanager
def graceful_handle_errors():
    """
    Example context manager for graceful error handling.
    """
    try:
        yield
    except (ConfigError, CSVError, FormatError) as e:
        print(f"[ERROR]: {e}")
    except Exception as e:
        raise
