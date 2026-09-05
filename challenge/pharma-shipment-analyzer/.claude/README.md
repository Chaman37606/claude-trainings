# Claude Code Integration Guide

This directory contains Claude Code configuration and customization for the Pharma Shipment Risk Analyzer.

## 📁 Structure

```
.claude/
├── settings.json                  # Claude Code configuration
├── skills/                        # Custom skills
│   ├── analyze-shipment-data.md
│   ├── risk-scorer.md
│   └── export-report.md
└── hooks/                         # Automation hooks
    └── high-risk-alert.sh
```

## 🛠️ Skills

### 1. analyze-shipment-data
Process and validate Excel files for pharmaceutical shipments.
```
/analyze-shipment-data
```

### 2. risk-scorer
Calculate risk scores using industry formula.
```
/risk-scorer
```

### 3. export-report
Generate compliance reports in multiple formats.
```
/export-report
```

## 🔧 Hooks

### PostToolUse
Triggers high-risk alerts when analysis completes with critical findings.

## ⚙️ Configuration

### Permissions
- Allow Python script execution
- Allow file read/write in backend and frontend directories
- Ask before destructive operations

### Environment
- API_PORT: 8000
- UI_PORT: 3000

## 🚀 Usage in Claude Code

1. **Upload File Analysis**
   - Use `/analyze-shipment-data` skill
   - Validates file format
   - Generates statistics

2. **Risk Calculation**
   - Use `/risk-scorer` skill
   - Calculates individual risk scores
   - Categorizes shipments

3. **Report Generation**
   - Use `/export-report` skill
   - Creates audit-ready documentation
   - Supports multiple formats

## 📊 Workflow Example

```
User uploads Excel
    ↓
Claude uses /analyze-shipment-data skill
    ↓
File validated & processed
    ↓
Claude uses /risk-scorer skill
    ↓
Risk scores calculated
    ↓
Hook triggers if high-risk detected
    ↓
Claude uses /export-report skill
    ↓
Compliance report generated
```

## 🔌 Extending

### Add New Skill
1. Create `.claude/skills/new-skill.md`
2. Document bash commands
3. Reference in workflow

### Customize Hooks
Edit `.claude/settings.json` to modify:
- Alert thresholds
- Trigger conditions
- Output messages

## 📝 Best Practices

✅ Skills are standalone and reusable  
✅ Hooks automate routine tasks  
✅ All operations logged for audit  
✅ Error handling graceful  
✅ GDPR and FDA compliant  

## 🆘 Troubleshooting

### Skill Not Available
- Ensure .claude/settings.json is valid JSON
- Check skill file name matches reference
- Reload Claude Code extension

### Hook Not Triggering
- Verify JSON in high-risk-alert.sh
- Check file permissions (chmod +x)
- Review hook configuration in settings.json

## 📞 Support

See CLAUDE.md in project root for complete documentation.
