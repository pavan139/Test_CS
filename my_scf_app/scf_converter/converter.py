# scf_converter/converter.py

import csv
import os
from typing import Optional
from scf_converter.converter_config import load_user_config, UserConfig
from scf_converter.record_spec.scf_spec_loader import load_scf_specs
from scf_converter.utils.logger import get_logger, log_call
from scf_converter.utils.error_handling import FormatError
from scf_converter.utils.formatter import format_field_value

logger = get_logger(__name__)

class SCFConverter:
    def __init__(self, config_path: str):
        """
        Constructor: loads user config and SCF specs, prepares for conversion.
        """
        logger.info(f"Initializing SCFConverter with config: {config_path}")
        self.user_config: UserConfig = load_user_config(config_path)
        self.record_specs = load_scf_specs()
        self.output_file_name = self._determine_output_filename(config_path)

        # Audit counters
        self.lines_written = 0
        self.rows_processed = 0
        self.rows_skipped = 0

    def _determine_output_filename(self, config_path: str) -> str:
        """
        Use 'output_file_name' from config if present,
        otherwise derive from config filename.
        """
        if self.user_config.output_file_name:
            return self.user_config.output_file_name
        else:
            base_name = os.path.splitext(os.path.basename(config_path))[0]
            return f"{base_name}.txt"

    @log_call(logger)
    def convert(self, input_csv_path: str, output_folder: Optional[str] = None) -> str:
        """
        Main method to convert a CSV into an SCF text file.
        """
        if output_folder is None:
            output_folder = os.path.dirname(input_csv_path)

        output_path = os.path.join(output_folder, self.output_file_name)
        logger.info(f"Starting conversion: CSV='{input_csv_path}' -> SCF='{output_path}'")

        with open(input_csv_path, "r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            with open(output_path, "w", encoding="utf-8") as scf_out:
                for row in reader:
                    self.rows_processed += 1
                    records_written_for_row = 0

                    for record_type, record_mapping in self.user_config.record_mappings.items():
                        scf_line = self._create_scf_line(row, record_type, record_mapping)
                        if scf_line:
                            scf_out.write(scf_line + "\n")
                            self.lines_written += 1
                            records_written_for_row += 1

                    if records_written_for_row == 0:
                        # Means no SCF lines were written for this CSV row
                        self.rows_skipped += 1

        # Write an optional audit record or summary
        self._write_audit_record(output_path)

        logger.info(f"Finished conversion. Rows processed={self.rows_processed}, lines={self.lines_written}")
        return output_path

    def _create_scf_line(self, csv_row: dict, record_type: str, record_mapping) -> Optional[str]:
        """
        Builds a single SCF line for the given record type from one CSV row.
        Returns None if we skip due to errors or missing specs.
        """
        spec = self.record_specs.get(record_type)
        if not spec:
            logger.warning(f"Record type '{record_type}' not found in specs. Skipping.")
            return None

        line_parts = []
        for field_def in spec.fields:
            length = field_def.end - field_def.start + 1

            # Retrieve mapping info
            field_map = record_mapping.fields.get(field_def.name)
            raw_value = ""
            if field_map:
                # If CSV column is provided, use its value
                if field_map.csv_column and field_map.csv_column in csv_row:
                    raw_value = csv_row[field_map.csv_column]
                # If empty, fallback to default (if any)
                if not raw_value and field_map.default_value is not None:
                    raw_value = field_map.default_value

            # Format/validate
            try:
                formatted_val = format_field_value(raw_value, field_def.formatter)
            except FormatError as e:
                # Decide how to handle format failures: skip the entire record, set blank, or raise
                logger.error(f"Format error for field '{field_def.name}' with value '{raw_value}': {e}")
                return None

            # Enforce length with truncate/pad
            formatted_val = formatted_val[:length].ljust(length)
            line_parts.append(formatted_val)

        return "".join(line_parts)

    def _write_audit_record(self, output_path: str):
        """
        Optional final line summarizing results, e.g. record type '99'.
        """
        audit_line = f"99SUMMARY RowsProcessed={self.rows_processed},LinesWritten={self.lines_written},RowsSkipped={self.rows_skipped}"
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(audit_line + "\n")

@log_call(logger)
def csv_to_scf_convert(input_csv: str, config_path: str, output_folder: Optional[str] = None) -> str:
    """
    Convenience function that instantiates SCFConverter and runs the conversion.
    """
    converter = SCFConverter(config_path)
    return converter.convert(input_csv, output_folder=output_folder)
