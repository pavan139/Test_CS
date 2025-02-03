# scf_converter/converter_config.py

import json
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from scf_converter.utils.error_handling import ConfigError

@dataclass
class FieldMapping:
    csv_column: Optional[str] = None
    default_value: Optional[str] = None

@dataclass
class RecordMapping:
    fields: Dict[str, FieldMapping] = field(default_factory=dict)

@dataclass
class UserConfig:
    output_file_name: Optional[str] = None
    record_mappings: Dict[str, RecordMapping] = field(default_factory=dict)

def load_user_config(filepath: str) -> UserConfig:
    """
    Load and parse a user config from JSON into UserConfig data class.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ConfigError(f"Error reading config file '{filepath}': {e}")

    return _parse_user_config(data)

def _parse_user_config(data: dict[str, Any]) -> UserConfig:
    record_mappings = {}
    raw_mappings = data.get("record_mappings", {})

    for record_type, rec_data in raw_mappings.items():
        fields_map = {}
        user_fields = rec_data.get("fields", {})
        user_defaults = rec_data.get("defaults", {})
        for field_name in set(user_fields.keys()).union(user_defaults.keys()):
            fields_map[field_name] = FieldMapping(
                csv_column=user_fields.get(field_name),
                default_value=user_defaults.get(field_name)
            )
        record_mappings[record_type] = RecordMapping(fields=fields_map)

    return UserConfig(
        output_file_name=data.get("output_file_name"),
        record_mappings=record_mappings
    )
