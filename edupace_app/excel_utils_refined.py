import pandas as pd

REQUIRED_COLUMNS = ['Student ID', 'Outcome', 'Score']

def is_valid_excel(file):
    return file.name.endswith(('.xls', '.xlsx'))

def read_excel_file(file):
    try:
        df = pd.read_excel(file)
        validate_columns(df)
        return df
    except Exception as e:
        print(f"Excel read error: {e}")
        return None

def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
