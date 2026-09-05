# Export Report

Generates compliance-ready reports in multiple formats (JSON, PDF, CSV) for audit trails, stakeholder communication, and regulatory documentation.

## Usage

```bash
cd backend && python -c "
from main import analysis_cache
import json

# Get file ID from analysis
file_id = 'abc123'  # From upload response

# Export as JSON
data = analysis_cache[file_id]['analysis']
report = {
    'timestamp': analysis_cache[file_id]['timestamp'],
    'summary': {
        'total_shipments': data['total_shipments'],
        'high_risk_count': data['high_risk_count'],
        'temp_excursions': data['temp_excursions'],
        'average_risk_score': data['average_risk_score']
    },
    'risk_distribution': data['risk_distribution']
}

with open('report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('Report saved: report.json')
"
```

## Export Formats

### JSON
Perfect for API integration and data processing
```json
{
  "timestamp": "2024-01-20T10:30:00Z",
  "file_name": "pharma_shipments.xlsx",
  "analysis": {
    "total_shipments": 1245,
    "high_risk_count": 87,
    "temp_excursions": 12,
    "average_risk_score": 45.2,
    "risk_distribution": {
      "LOW": 750,
      "MEDIUM": 248,
      "HIGH": 37,
      "CRITICAL": 10
    }
  }
}
```

### Compliance Summary
Includes FDA 21 CFR Part 11 documentation requirements

## Report Contents

1. **Executive Summary**
   - Total shipments analyzed
   - High-risk percentage
   - Critical alerts count

2. **Risk Distribution**
   - Breakdown by risk level
   - Percentage distribution
   - Trend analysis

3. **Top Issues**
   - Highest-risk shipments
   - Root cause analysis
   - Temperature excursions

4. **Compliance Notes**
   - Regulatory requirements
   - Documentation trail
   - Recommendations

5. **Audit Trail**
   - Analysis timestamp
   - Data processor version
   - Calculation method

## Use Cases

✅ FDA audit documentation  
✅ Stakeholder presentations  
✅ Regulatory compliance  
✅ Historical archival  
✅ Inter-company reporting  

## Data Privacy

- ✓ Personally identifiable information redacted
- ✓ Secure encryption supported
- ✓ GDPR compliant
- ✓ Access logging enabled

## Delivery

```bash
# Generate and email report
curl -X GET "http://localhost:8000/api/export/abc123?format=json" \
  -H "Accept: application/json" > compliance_report_2024-01-20.json
```
