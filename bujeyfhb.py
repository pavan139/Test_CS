import os
import pandas as pd
import yaml

def load_config(config_path):
    """Load YAML configuration from the specified path."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def process_file(file_config, input_dir="data/input"):
    """Read a CSV file, rename its columns, and convert specified columns (e.g., date columns)."""
    file_path = os.path.join(input_dir, file_config['file_name'])
    df = pd.read_csv(file_path)
    
    # Rename columns as per the mapping.
    df = df.rename(columns=file_config['mapping'])
    
    # Convert columns to specified data types.
    for col, dtype_info in file_config.get('dtypes', {}).items():
        if dtype_info.get("type") == "date":
            df[col] = pd.to_datetime(df[col], format=dtype_info.get("format"))
    
    return df

def write_to_excel(dataframes, output_path="data/output/final_output.xlsx"):
    """Write multiple DataFrames to an Excel file, each in its own sheet."""
    # Ensure the output directory exists.
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Data successfully written to {output_path}")

def main():
    # Load configuration.
    config = load_config("config/input_config.yaml")
    
    dataframes = {}
    # Process each CSV file as defined in the configuration.
    for key, file_config in config.get("input_files", {}).items():
        print(f"Processing file: {file_config['file_name']}")
        df = process_file(file_config)
        dataframes[key] = df
    
    # Write the processed DataFrames to an Excel file.
    write_to_excel(dataframes)

if __name__ == '__main__':
    main()
