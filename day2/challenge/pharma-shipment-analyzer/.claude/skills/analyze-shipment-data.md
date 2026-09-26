# Analyze Shipment Data

Processes and validates pharmaceutical shipment Excel files, extracting key metrics and generating initial risk assessment.

## Usage

```bash
cd backend && python -c "
from data_processor import DataProcessor
import json

# Validate file
validation = DataProcessor.validate_file('uploads/shipments.xlsx')
print(json.dumps(validation, indent=2))

# Process and get summary
df = DataProcessor.process_file('uploads/shipments.xlsx')
summary = DataProcessor.get_summary(df)
print(json.dumps(summary, indent=2))
"
```

## What It Does

✅ Validates Excel file format and structure  
✅ Checks for required columns (shipment_id, temp_min, temp_max, etc.)  
✅ Detects data quality issues  
✅ Generates data summary statistics  
✅ Identifies missing or malformed data  

## Output

```json
{
  "valid": true,
  "rows": 1245,
  "columns": 11,
  "temp_range": {
    "min": -0.5,
    "max": 28.3,
    "mean": 5.2
  },
  "unique_origins": 12,
  "unique_destinations": 45,
  "status_breakdown": {
    "Delivered": 1200,
    "In Transit": 30,
    "Delayed": 15
  }
}
```

## Requirements

- ✓ Python 3.8+
- ✓ pandas
- ✓ openpyxl
- ✓ Excel file with required columns

## Error Handling

- Missing required columns: Validation fails
- Invalid data types: Warnings generated
- Empty rows: Automatically removed
- Date format issues: Handled gracefully
