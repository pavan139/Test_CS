"""
Module for formatting values according to COBOL-style picture strings.

Supports formats:
- Alphanumeric: X(n) or repeated X (e.g., XXXX)
- Numeric: S9(n)V9(m), 999V99, etc. (case‐insensitive)
"""

from typing import Dict, Union, Match, Tuple, Any
import re
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PictureFormatError(Exception):
    """Base exception for picture formatting errors."""
    pass

class InvalidPictureFormat(PictureFormatError):
    """Raised when the picture string format is invalid."""
    pass

class InvalidInputValue(PictureFormatError):
    """Raised when the input value is invalid for the given picture format."""
    pass

class FieldType(Enum):
    """Enumeration of supported field types."""
    ALPHANUMERIC = "alphanumeric"
    NUMERIC = "numeric"

@dataclass
class NumericFormat:
    """Configuration for numeric field formatting."""
    is_signed: bool
    int_width: int
    dec_width: int

    def __post_init__(self) -> None:
        """Validate the numeric format configuration."""
        if self.int_width < 1:
            raise InvalidPictureFormat("Integer width must be positive")
        if self.dec_width < 0:
            raise InvalidPictureFormat("Decimal width cannot be negative")

class PictureFormatter:
    """Handles formatting of values according to COBOL picture strings."""

    SIGN_MAP_POSITIVE: Dict[str, str] = {
        "0": "{", "1": "A", "2": "B", "3": "C", "4": "D",
        "5": "E", "6": "F", "7": "G", "8": "H", "9": "I"
    }
    
    SIGN_MAP_NEGATIVE: Dict[str, str] = {
        "0": "}", "1": "J", "2": "K", "3": "L", "4": "M",
        "5": "N", "6": "O", "7": "P", "8": "Q", "9": "R"
    }

    def __init__(self) -> None:
        # Pattern for alphanumeric: either X(n) or a sequence of X’s.
        self._alpha_pattern = re.compile(r"^X\((\d+)\)$|^(X+)$", re.IGNORECASE)
        # Pattern for numeric. The numeric part must be either a sequence of 9’s
        # or a number in the form 9(n) (e.g. 9(10)). The fractional part (if any)
        # is preceded by a V.
        self._numeric_pattern = re.compile(
            r"^(S)?(9+|\d+\((\d+)\))(V(9+|\d+\((\d+)\)))?$", re.IGNORECASE
        )

    def _parse_picture(self, picture: str) -> Tuple[FieldType, Union[int, NumericFormat]]:
        picture = picture.upper()
        if match := self._alpha_pattern.match(picture):
            if match.group(1):  # X(n) format
                width = int(match.group(1))
            else:  # e.g. XXXX
                width = len(match.group(2))
            return FieldType.ALPHANUMERIC, width

        if match := self._numeric_pattern.match(picture):
            is_signed = match.group(1) is not None

            # Parse integer part.
            int_spec = match.group(2)
            if match.group(3):  # e.g. 9(10)
                int_width = int(match.group(3))
            else:  # pure sequence of 9’s, e.g. 999
                int_width = len(int_spec)

            # Parse the fractional part (if any). We use group(5) and group(6)
            # so that for a picture like "S9(11)V99", int_width becomes 11 and dec_width becomes 2.
            fraction_spec = match.group(5) if match.group(5) else ''
            if fraction_spec:
                if match.group(6):
                    dec_width = int(match.group(6))
                else:
                    dec_width = len(fraction_spec)
            else:
                dec_width = 0

            return FieldType.NUMERIC, NumericFormat(is_signed, int_width, dec_width)

        raise InvalidPictureFormat(f"Invalid picture format: {picture}")

    # def _format_alphanumeric(self, value: str, width: int) -> str:
    #     return value[:width] if len(value) >= width else value.ljust(width)
    def _format_alphanumeric(self, value: str, width: int) -> str:
      if len(value) > width:
          raise InvalidInputValue(f"'{value}' exceeds width {width}")
      return value.ljust(width)

    def _parse_numeric_value(self, value: str, format_config: NumericFormat) -> Tuple[str, str, str]:
        value = value.strip()
        sign = "+"
        
        if value.startswith("+"):
            if not format_config.is_signed:
                raise InvalidInputValue("Unsigned field cannot have explicit sign")
            value = value[1:]
        elif value.startswith("-"):
            if not format_config.is_signed:
                raise InvalidInputValue("Unsigned field cannot have negative sign")
            sign = "-"
            value = value[1:]

        parts = value.split(".")
        if len(parts) > 2:
            raise InvalidInputValue(f"Invalid numeric value (multiple decimals): {value}")

        integer_part = parts[0] or "0"
        decimal_part = parts[1] if len(parts) == 2 else ""

        # If the picture has no V (i.e. dec_width==0) then a decimal part is not allowed.
        if format_config.dec_width == 0 and decimal_part != "":
            raise InvalidInputValue("Decimal part not allowed for field without V")

        if not integer_part.isdigit():
            raise InvalidInputValue(f"Non-digit in integer part: {integer_part}")
        if decimal_part and not decimal_part.isdigit():
            raise InvalidInputValue(f"Non-digit in decimal part: {decimal_part}")

        if len(integer_part) > format_config.int_width:
            raise InvalidInputValue(
                f"Integer part '{integer_part}' exceeds width {format_config.int_width}"
            )

        return sign, integer_part, decimal_part

    def _format_numeric(self, value: str, format_config: NumericFormat) -> str:
        sign, integer_part, decimal_part = self._parse_numeric_value(value, format_config)

        if format_config.dec_width > 0:
            # For a field with a fractional part, pad the integer and fractional parts exactly.
            dec_formatted = decimal_part.ljust(format_config.dec_width, '0')[:format_config.dec_width]
            int_formatted = integer_part.zfill(format_config.int_width)
            numeric_field = int_formatted + dec_formatted
        else:
            # For numeric fields without a fractional part (no V),
            # apply formatting only if the input was given as a string.
            numeric_field = integer_part.zfill(format_config.int_width)

        # Apply sign encoding if the picture is signed.
        if format_config.is_signed:
            sign_map = self.SIGN_MAP_POSITIVE if sign == "+" else self.SIGN_MAP_NEGATIVE
            numeric_field = numeric_field[:-1] + sign_map[numeric_field[-1]]

        return numeric_field

    def format_value(self, value: Any, picture: str) -> str:
        """
        Format the given value according to the provided picture.
        
        For alphanumeric fields, the value is first converted to a string and then padded/truncated.
        
        For numeric fields:
          - If the picture includes a fractional part (a "V"), formatting is always applied.
          - Otherwise (no "V"):
              * If the input is already a string, the value is formatted (i.e. zero-padded).
              * If the input is not a string (e.g. an int), then the value is simply converted via str().
        """
        field_type, format_details = self._parse_picture(picture)
        
        if field_type == FieldType.ALPHANUMERIC:
            return self._format_alphanumeric(str(value), format_details)
        else:  # Numeric field.
            # If the picture includes a fractional part (V present), always apply formatting.
            if format_details.dec_width > 0:
                return self._format_numeric(str(value), format_details)
            else:
                # For numeric fields without a fractional part:
                # if the value is already a string, apply formatting;
                # otherwise, return the plain type conversion.
                if isinstance(value, str):
                    return self._format_numeric(value, format_details)
                else:
                    return str(value)

def format_picture_value(value: Any, picture: str) -> str:
    return PictureFormatter().format_value(value, picture)
