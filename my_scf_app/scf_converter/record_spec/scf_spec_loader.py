# scf_converter/record_spec/scf_spec_loader.py

import json
from functools import lru_cache
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class FieldSpec:
    name: str
    start: int
    end: int
    formatter: str

@dataclass
class RecordSpec:
    record_type: str
    fields: List[FieldSpec]

@lru_cache(maxsize=None)
def load_scf_specs(path: str = "scf_converter/record_spec/scf_record_spec.json") -> Dict[str, RecordSpec]:
    """
    Loads SCF record definitions from JSON and returns a dict of record_type -> RecordSpec
    """
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    specs = {}
    for record_def in records:
        r_type = record_def["record_type"]
        field_specs = []
        for field_info in record_def["fields"]:
            field_specs.append(
                FieldSpec(
                    name=field_info["name"],
                    start=field_info["start"],
                    end=field_info["end"],
                    formatter=field_info["formatter"]
                )
            )
        specs[r_type] = RecordSpec(record_type=r_type, fields=field_specs)
    return specs
