import os
from scf_converter.converter import csv_to_scf_convert
from scf_converter.utils.error_handling import graceful_handle_errors

def main():
    """
    Simple CLI/entry point example.
    """
    input_csv = "data/sample_input.csv"          # Adjust path as needed
    config_path = "scf_converter/config/xtmy_config.json"
    output_dir = "output"

    with graceful_handle_errors():
        output_file = csv_to_scf_convert(input_csv, config_path, output_folder=output_dir)
        print(f"SCF file generated: {output_file}")

if __name__ == "__main__":
    main()
