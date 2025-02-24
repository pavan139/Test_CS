import os
import pandas as pd
import yaml

def load_config(config_path):
    """Load YAML configuration from the specified path."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def process_file(file_config, input_dir="data/input"):
    """
    Read a file (CSV, text, or Excel) based on its type,
    rename columns according to mapping, and convert data types.
    """
    file_path = os.path.join(input_dir, file_config['file_name'])
    file_type = file_config.get('type', 'csv').lower()

    if file_type == 'csv':
        df = pd.read_csv(file_path)
    elif file_type == 'text':
        delimiter = file_config.get('delimiter', ',')
        df = pd.read_csv(file_path, delimiter=delimiter)
    elif file_type == 'excel':
        sheet_name = file_config.get('sheet_name', 0)
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    # Rename columns based on mapping.
    df = df.rename(columns=file_config['mapping'])
    
    # Convert columns to specified data types.
    for col, dtype_info in file_config.get('dtypes', {}).items():
        if dtype_info.get("type") == "date":
            df[col] = pd.to_datetime(df[col], format=dtype_info.get("format"))
    
    return df

def write_to_excel(dataframes, output_path="data/output/final_output.xlsx"):
    """
    Write multiple DataFrames to an Excel file, with each DataFrame in a separate sheet.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Data successfully written to {output_path}")

def main():
    # Load configuration.
    config = load_config("config/input_config.yaml")
    
    dataframes = {}
    # Process each file as defined in the configuration.
    for key, file_config in config.get("input_files", {}).items():
        print(f"Processing file: {file_config['file_name']} (type: {file_config.get('type', 'csv')})")
        df = process_file(file_config)
        dataframes[key] = df
    
    # Write the processed DataFrames to a single Excel file with separate sheets.
    write_to_excel(dataframes)

if __name__ == '__main__':
    main()
