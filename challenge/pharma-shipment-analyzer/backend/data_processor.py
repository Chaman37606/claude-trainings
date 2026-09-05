"""Excel data processing for pharmaceutical shipments."""
import pandas as pd
from typing import Dict, Any, List
import os


class DataProcessor:
    """Process and validate pharmaceutical shipment data."""

    REQUIRED_COLUMNS = [
        'shipment_id',
        'temp_min',
        'temp_max',
        'temp_actual',
        'status',
        'delivery_date'
    ]

    OPTIONAL_COLUMNS = [
        'origin',
        'destination',
        'handler_id',
        'incidents',
        'regulatory_flags'
    ]

    @classmethod
    def validate_file(cls, file_path: str) -> Dict[str, Any]:
        """Validate Excel file format and contents."""
        errors = []
        warnings = []

        try:
            # Check file exists
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File not found"}

            # Read Excel
            df = pd.read_excel(file_path)

            # Check required columns
            missing = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
            if missing:
                errors.append(f"Missing required columns: {', '.join(missing)}")

            # Check for empty rows
            if df.isnull().all(axis=1).any():
                warnings.append("File contains empty rows")

            # Check data types
            for col in ['temp_min', 'temp_max', 'temp_actual']:
                if col in df.columns:
                    try:
                        pd.to_numeric(df[col], errors='coerce')
                    except:
                        errors.append(f"Column '{col}' contains non-numeric values")

            # Check for empty required fields
            for col in cls.REQUIRED_COLUMNS:
                if col in df.columns and df[col].isnull().any():
                    warnings.append(f"Column '{col}' contains empty values")

            return {
                "valid": len(errors) == 0,
                "rows": len(df),
                "columns": len(df.columns),
                "errors": errors,
                "warnings": warnings
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    @classmethod
    def process_file(cls, file_path: str) -> pd.DataFrame:
        """Load and clean Excel file."""
        # Read Excel
        df = pd.read_excel(file_path)

        # Rename columns to lowercase and strip whitespace
        df.columns = df.columns.str.lower().str.strip()

        # Fill missing optional columns with defaults
        for col in cls.OPTIONAL_COLUMNS:
            if col not in df.columns:
                if col == 'incidents':
                    df[col] = 0
                else:
                    df[col] = ''

        # Convert temperature columns to numeric
        for col in ['temp_min', 'temp_max', 'temp_actual']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert date column
        if 'delivery_date' in df.columns:
            df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce').dt.strftime('%Y-%m-%d')

        # Remove rows with missing critical data
        df = df.dropna(subset=cls.REQUIRED_COLUMNS)

        return df

    @classmethod
    def get_summary(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Get data summary statistics."""
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "temp_range": {
                "min": float(df['temp_actual'].min()) if 'temp_actual' in df.columns else None,
                "max": float(df['temp_actual'].max()) if 'temp_actual' in df.columns else None,
                "mean": float(df['temp_actual'].mean()) if 'temp_actual' in df.columns else None
            },
            "unique_origins": len(df['origin'].unique()) if 'origin' in df.columns else 0,
            "unique_destinations": len(df['destination'].unique()) if 'destination' in df.columns else 0,
            "status_breakdown": df['status'].value_counts().to_dict() if 'status' in df.columns else {}
        }
