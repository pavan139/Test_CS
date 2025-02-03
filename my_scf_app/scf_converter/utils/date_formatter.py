from dateutil import parser
import re

class ValueFormatError(Exception):
    """Base exception for value formatting errors."""
    pass

class InvalidDateFormat(ValueFormatError):
    """Raised when the input date format is invalid."""
    pass

class InvalidSSNFormat(ValueFormatError):
    """Raised when the SSN format is invalid."""
    pass

def format_date_value(date_str):
    """
    Converts a date string into MMDDYYYY and YYYYMMDD formats.

    Args:
        date_str (str): The date string to format.

    Returns:
        tuple: A tuple containing MMDDYYYY and YYYYMMDD formatted strings.

    Raises:
        InvalidDateFormat: If the input is not a valid date string.
    """
    if not isinstance(date_str, str):
        raise InvalidDateFormat(f"Input must be a string, got {type(date_str).__name__}")
    
    try:
        date_obj = parser.parse(date_str)
        mmddyyyy = date_obj.strftime("%m%d%Y")
        yyyymmdd = date_obj.strftime("%Y%m%d")
        return mmddyyyy, yyyymmdd
    except (parser.ParserError, ValueError) as e:
        raise InvalidDateFormat(f"Invalid date format: {e}")

def check_ssn_value(ssn):
    """
    Validates if the input SSN matches the XXX-XX-XXXX format.

    Args:
        ssn (str): The SSN to validate.

    Returns:
        bool: True if SSN is valid, raises an exception otherwise.

    Raises:
        InvalidSSNFormat: If the input is not a valid SSN.
    """
    ssn_pattern = re.compile(r"^\d{3}-\d{2}-\d{4}$")
    
    if not isinstance(ssn, str):
        raise InvalidSSNFormat(f"Input must be a string, got {type(ssn).__name__}")
    
    if not ssn_pattern.match(ssn):
        raise InvalidSSNFormat("Invalid SSN format. Expected format: XXX-XX-XXXX")
    
    return True
