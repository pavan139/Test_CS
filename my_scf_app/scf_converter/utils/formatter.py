# scf_converter/utils/formatter.py

import datetime
from decimal import Decimal, InvalidOperation
from scf_converter.utils.error_handling import FormatError

def format_field_value(raw_value: str, formatter: str) -> str:
    """
    Converts/validates 'raw_value' based on 'formatter' (e.g., 'date-mm/dd/yyyy', 'decimal-2').
    Raises FormatError on invalid data.
    """
    raw_value = raw_value.strip()

    if formatter.startswith("date-"):
        return _handle_date(raw_value, formatter)
    elif formatter.startswith("decimal-"):
        return _handle_decimal(raw_value, formatter)
    elif formatter == "integer":
        return _handle_integer(raw_value)
    elif formatter == "string":
        return raw_value
    else:
        raise FormatError(f"Unrecognized formatter '{formatter}'")

def _handle_date(value: str, formatter: str) -> str:
    # e.g., date-mm/dd/yyyy or date-yyyymmdd
    date_pattern = formatter.split("-", 1)[1].lower()
    try:
        if date_pattern == "mm/dd/yyyy":
            dt = datetime.datetime.strptime(value, "%m/%d/%Y")
            return dt.strftime("%m/%d/%Y")
        elif date_pattern == "yyyymmdd":
            dt = datetime.datetime.strptime(value, "%Y%m%d")
            return dt.strftime("%Y%m%d")
        else:
            raise FormatError(f"Unsupported date pattern '{date_pattern}'")
    except ValueError as e:
        raise FormatError(f"Invalid date '{value}' for pattern '{date_pattern}': {e}")

def _handle_decimal(value: str, formatter: str) -> str:
    # e.g., decimal-2 or decimal-4
    decimal_places_str = formatter.split("-")[1]
    try:
        decimal_places = int(decimal_places_str)
        dec = Decimal(value)
        # Quantize to specified decimal places
        dec_str = str(dec.quantize(Decimal(f'1.{"0"*decimal_places}')))
        return dec_str
    except (InvalidOperation, ValueError) as e:
        raise FormatError(f"Invalid decimal '{value}': {e}")

def _handle_integer(value: str) -> str:
    if not value.isdigit():
        raise FormatError(f"Value '{value}' is not an integer.")
    return value
