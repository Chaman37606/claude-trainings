# Claude.md - Pharma Shipment Risk Analyzer

**Project Type:** Advanced Data Analysis & Risk Intelligence Tool  
**Tech Stack:** Python FastAPI, React, Pandas, AI-powered insights  
**Purpose:** Pharmaceutical compliance & supply chain risk management

---

## 🎯 Project Vision

This tool helps pharmaceutical logistics teams identify and mitigate supply chain risks in real-time. Claude Code enhances this with:
- **Automatic analysis workflows** via hooks
- **Risk scoring subagents** for intelligent recommendations
- **Custom skills** for data processing
- **Intelligent alerts** for high-risk shipments

---

## 🏗️ Architecture Overview

```
User Upload (Excel)
    ↓
FastAPI Backend
    ├── Parse Excel → Pandas DataFrame
    ├── Calculate Risk Metrics
    ├── Trigger MCP Subagent for AI Insights
    └── Return JSON Response
    ↓
React Frontend
    ├── Display Dashboard
    ├── Charts (Risk Distribution)
    ├── Top 5 Risk Table
    └── AI Recommendations
```

---

## 📁 Project Structure

```
pharma-shipment-analyzer/
├── CLAUDE.md                          ← This file
├── README.md                          ← User documentation
├── backend/
│   ├── main.py                        ← FastAPI app
│   ├── models.py                      ← Risk calculation models
│   ├── data_processor.py              ← Excel parsing & validation
│   ├── requirements.txt               ← Python dependencies
│   └── uploads/                       ← Temporary storage
├── frontend/
│   ├── index.html                     ← React dashboard
│   ├── styles.css                     ← Styling
│   └── app.js                         ← Frontend logic
├── .claude/
│   ├── settings.json                  ← Claude Code config
│   ├── skills/
│   │   ├── analyze-shipment-data.md   ← Data analysis skill
│   │   ├── risk-scorer.md             ← Risk calculation
│   │   └── export-report.md           ← Report generation
│   └── hooks/
│       └── post-analysis-alert.sh     ← Alert on high-risk
├── sample-data/
│   └── pharma_shipments_sample.xlsx   ← Example dataset
└── .gitignore
```

---

## 🔧 Claude Code Integration

### 1. Custom Skills (`.claude/skills/`)

#### **analyze-shipment-data.md**
Processes Excel files and calculates core metrics:
- Parses pharmaceutical shipment data
- Validates data integrity
- Generates initial statistics

```bash
## Analyze Pharma Shipment Data
```bash
cd backend && python -c "
from data_processor import process_shipment_file
import json
result = process_shipment_file('uploads/shipments.xlsx')
print(json.dumps(result, indent=2))
"
```
```

#### **risk-scorer.md**
Calculates risk scores and identifies high-risk shipments:
- Temperature excursions
- Delayed deliveries
- Handling incidents
- Regulatory compliance issues

```bash
## Calculate Risk Scores
```bash
cd backend && python models.py --calculate-risks
```
```

#### **export-report.md**
Generates compliance reports:
- PDF export for audit trail
- Email summary to team
- Historical trending

```bash
## Generate Risk Report
```bash
cd backend && python -c "
from models import generate_report
generate_report('high_risk_only', format='pdf')
"
```
```

---

### 2. Hooks Configuration (`.claude/settings.json`)

#### **PostToolUse Hook - Auto-Alert on High-Risk**
When analysis completes and high-risk shipments found:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -q '\"risk_level\":\"high\"' /tmp/analysis_result.json; then echo '{\"systemMessage\": \"⚠️ HIGH-RISK SHIPMENTS DETECTED - Review immediately\"}'; fi"
          }
        ]
      }
    ]
  }
}
```

#### **PreToolUse Hook - Validate Input Files**
Before processing uploads:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Is this a valid pharmaceutical shipment Excel file? Check: columns (shipment_id, temperature, destination, status), no empty required fields, dates are valid."
          }
        ]
      }
    ]
  }
}
```

---

### 3. Subagents for Intelligence

#### **Risk Analysis Subagent**
Spawned automatically after data upload. Responsibilities:
- Analyze shipment patterns
- Identify risk clusters
- Generate AI-style recommendations
- Predict future risks

**Prompt Template:**
```
You are a pharmaceutical supply chain risk expert. Analyze these shipments:
- High-risk count: {high_risk_count}
- Temperature excursions: {temp_excursions}
- Average delivery time: {avg_delivery_time}

Provide:
1. Root cause analysis for top risks
2. 3 actionable recommendations
3. Compliance alerts
4. Preventive measures
```

#### **Compliance Auditor Subagent**
Reviews against FDA/GDPR regulations:
- Temperature stability requirements
- Cold chain documentation
- Handling incident classification
- Regulatory violation alerts

---

## 📊 Dashboard Features

### 1. Risk Metrics Display
```
┌─────────────────────────────────────────┐
│  PHARMA SHIPMENT RISK DASHBOARD         │
├─────────────────────────────────────────┤
│                                         │
│  Total Shipments: 1,245  |  High-Risk: 87 (7%)
│  Temp Excursions: 12     |  Delayed: 34 (3%)
│                                         │
└─────────────────────────────────────────┘
```

### 2. Risk Distribution Chart
- Pie chart: Risk levels (Low, Medium, High, Critical)
- Color-coded: Green, Yellow, Orange, Red
- Interactive: Hover for percentages

### 3. Top 5 High-Risk Shipments Table
```
Rank | Shipment ID | Risk Score | Temperature | Status
─────┼─────────────┼────────────┼─────────────┼─────────
 1   | SHP-2024-001| 95/100     | 27.5°C      | ALERT
 2   | SHP-2024-015| 92/100     | 26.8°C      | ALERT
 3   | SHP-2024-042| 88/100     | Normal      | Delayed
 4   | SHP-2024-058| 85/100     | 25.2°C      | ALERT
 5   | SHP-2024-031| 82/100     | Normal      | Damaged
```

### 4. AI Recommendations
Generated by Claude's reasoning:
- "Temperature excursions in Route A suggest insulation failure - recommend replacing cooling units"
- "3 incidents in past week - increase monitoring frequency"
- "Compliance alert: Document temperature log for shipment SHP-2024-001"

---

## 🚀 Quick Start Commands

### Setup
```bash
cd pharma-shipment-analyzer
bash setup.sh
```

### Development
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
npx http-server frontend -p 3000

# Terminal 3: Claude Code (for skills)
# Skills available in Claude editor
```

### Using Claude Skills
In Claude Code interface:
1. `/analyze-shipment-data` → Process and validate file
2. `/risk-scorer` → Calculate risk metrics
3. `/export-report` → Generate compliance report

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload Excel file |
| GET | `/api/analysis/{file_id}` | Get analysis results |
| GET | `/api/risks/high` | List high-risk shipments |
| GET | `/api/stats` | Get dashboard metrics |
| POST | `/api/recommendations` | Get AI insights (calls subagent) |
| GET | `/api/export/{format}` | Export report (PDF/CSV) |

---

## 📋 Sample Excel Format

Required columns in uploaded file:
```
shipment_id | origin | destination | temp_min | temp_max | temp_actual | 
status | delivery_date | handler_id | incidents | regulatory_flags
```

Example:
```
SHP-2024-001 | NYC | Boston | 2°C | 8°C | 27.5°C | Delivered | 2024-01-15 | H001 | Temp Excursion | FDA Investigation
```

---

## 🎯 Risk Scoring Algorithm

```python
Risk Score = (
    (temp_excursion_severity × 0.40) +
    (delivery_delay_days / max_delay × 0.30) +
    (incident_count × 0.20) +
    (regulatory_flags × 0.10)
) × 100

Risk Levels:
- 0-30: Low (Green)
- 31-60: Medium (Yellow)
- 61-85: High (Orange)
- 86-100: Critical (Red)
```

---

## 🤖 AI Recommendations Algorithm

Claude analyzes:
1. **Pattern Recognition**: Identify recurring issues
2. **Root Cause Analysis**: Why did risks occur?
3. **Predictive Insights**: Future risk likelihood
4. **Actionable Steps**: Specific recommendations
5. **Compliance Checks**: Regulatory requirements

Example output:
```
🔍 ANALYSIS SUMMARY
────────────────────
High-risk incidents clustered in Q1
Root cause: Insufficient cooling capacity during peak season

📋 RECOMMENDATIONS
────────────────────
1. Increase cooling unit capacity by 25% before Q1 2025
2. Implement temperature monitoring at distribution points
3. Train handlers on proper packaging procedures
4. Review vendor SLA compliance monthly

⚠️ COMPLIANCE ALERTS
────────────────────
- Document all temperature excursions per FDA regulations
- Notify customers of affected shipments within 24 hours
- Maintain audit trail for regulatory review
```

---

## 🔐 Security & Compliance

- **Data Privacy**: Files deleted after 24 hours
- **Audit Trail**: All analyses logged with timestamps
- **Access Control**: Role-based (Analyst, Manager, Admin)
- **Encryption**: Data encrypted in transit and at rest
- **Compliance**: FDA 21 CFR Part 11 ready

---

## 📦 Dependencies

```
Backend:
- fastapi==0.104.1
- pandas==2.0.0
- openpyxl==3.10.0
- python-dotenv==1.0.0

Frontend:
- React 18
- Chart.js (for risk distribution)
- Fetch API (no external libs needed)
```

---

## 🧪 Testing

### Manual Test Workflow
1. Upload `sample-data/pharma_shipments_sample.xlsx`
2. View dashboard metrics
3. Check top 5 high-risk list
4. Review AI recommendations
5. Export compliance report

### Claude Code Testing
```bash
# Validate data processor
/analyze-shipment-data

# Test risk scorer
/risk-scorer

# Generate report
/export-report
```

---

## 🎓 Learning Path

1. **Understand Risk Scoring**: See `models.py` risk algorithm
2. **Data Processing**: Review `data_processor.py` for Excel handling
3. **Frontend Visualizations**: Check `frontend/app.js` for Chart.js integration
4. **API Design**: Explore `backend/main.py` FastAPI routes
5. **Claude Integration**: Use `/analyze-shipment-data` skill in practice

---

## 🚨 Common Issues & Solutions

### Issue: Excel file not parsing
**Solution**: Check file format, ensure required columns present
**Skill**: `/analyze-shipment-data` validates automatically

### Issue: Risk scores seem inaccurate
**Solution**: Review temperature thresholds in `models.py`
**Skill**: `/risk-scorer` recalculates with custom thresholds

### Issue: Need compliance documentation
**Solution**: Use export feature or skill
**Skill**: `/export-report --format=pdf`

---

## 🔮 Future Enhancements

- Real-time IoT sensor integration
- Machine learning risk prediction
- Mobile app for field teams
- Integration with ERP systems
- Blockchain for regulatory compliance

---

## 📞 Support Resources

- **Documentation**: See README.md
- **Sample Data**: `sample-data/pharma_shipments_sample.xlsx`
- **API Docs**: `http://localhost:8000/docs` (Swagger)
- **Claude Code**: Use `/analyze-shipment-data` skill for help

---

## 🎯 Design Philosophy

This tool embodies pharmaceutical compliance excellence:
- **Accuracy**: Every calculation audited
- **Speed**: Real-time risk identification
- **Intelligence**: AI-powered recommendations
- **Compliance**: FDA/GDPR ready
- **Usability**: Intuitive dashboard for logistics teams

---

**Version:** 1.0.0  
**Last Updated:** January 2025  
**Status:** Production Ready  
**Maintainer:** Pharma Supply Chain Team
