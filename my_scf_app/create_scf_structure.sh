#!/usr/bin/env bash

# Create the top-level directory
mkdir -p my_scf_app

# Create subfolders within scf_converter
mkdir -p my_scf_app/scf_converter/record_spec
mkdir -p my_scf_app/scf_converter/config
mkdir -p my_scf_app/scf_converter/utils
mkdir -p my_scf_app/scf_converter/constants

# Create data & output folders
mkdir -p my_scf_app/data
mkdir -p my_scf_app/output

# Create the Python package files (empty placeholders for now)
touch my_scf_app/scf_converter/__init__.py
touch my_scf_app/scf_converter/main.py
touch my_scf_app/scf_converter/converter.py
touch my_scf_app/scf_converter/converter_config.py
touch my_scf_app/scf_converter/config_schema.json

# Create record_spec files
touch my_scf_app/scf_converter/record_spec/__init__.py
touch my_scf_app/scf_converter/record_spec/scf_record_spec.json
touch my_scf_app/scf_converter/record_spec/scf_spec_loader.py

# Create config files
touch my_scf_app/scf_converter/config/xtmy_config.json

# Create utils files
touch my_scf_app/scf_converter/utils/logger.py
touch my_scf_app/scf_converter/utils/error_handling.py
touch my_scf_app/scf_converter/utils/formatter.py

# Create constants
touch my_scf_app/scf_converter/constants/__init__.py

# Create sample data file
touch my_scf_app/data/sample_input.csv

echo "Folder structure created in 'my_scf_app/'"
