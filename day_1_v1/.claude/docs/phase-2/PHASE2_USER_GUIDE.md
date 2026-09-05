# ALCOA+ Phase 2 User Guide

## Quick Start: New Features Overview

The ALCOA+ framework now includes 5 powerful new features to help you manage compliance more effectively. This guide walks you through each one.

---

## 1. Data Export System

### What It Does
Export your compliance data in multiple formats for reporting, sharing, and archiving.

### How to Use It

1. **Go to Dashboard Tab**
   - Click the "Dashboard" button at the top

2. **Click Export Button**
   - Look for "Export Dashboard" button at the top of the dashboard
   - Or click "Print Dashboard" for immediate printing

3. **Choose Export Format**
   A dialog will appear with 4 options:

   **CSV Format** (Best for Excel)
   - Open in Excel, Google Sheets, Numbers
   - Good for further analysis
   - Includes all metrics and test cases

   **JSON Format** (Best for Technical Integration)
   - Raw data format
   - For developers/integrations
   - Machine-readable

   **HTML Format** (Best for Sharing)
   - Standalone report file
   - Share via email
   - Includes all styling
   - No dependencies needed

   **PDF Format** (Best for Printing)
   - Professional print layout
   - Uses browser's print dialog
   - Can save as PDF

4. **File Downloads**
   - File automatically downloads with timestamp
   - Example: `ALCOA_Report_1693357542123.csv`

### What Gets Exported

Your export includes:
- Overall compliance percentage
- Systems audited (count)
- Critical findings (count)
- Personnel trained (count)
- Compliance % for each principle (all 9)
- Detailed test case results with status

### Tips

- **Export before meetings** → Share current compliance status
- **Use HTML for email** → Recipient can view without tools
- **Use CSV for analysis** → Load into spreadsheet for deeper analysis
- **Keep regular exports** → Build compliance history

---

## 2. Advanced Search & Filter

### What It Does
Quickly find specific information across the entire framework.

### How to Use It

1. **Go to Search & Filter Tab**
   - Click "Search & Filter" button at the top

2. **Enter Search Term**
   - Type in the search box at top left
   - Examples: "Attributable", "Audit Trail", "compliance"
   - Results appear instantly

3. **Filter Results** (Optional)
   - On the right side, check/uncheck filter categories:
     - Principles (9 ALCOA+ principles)
     - Test Cases (compliance test scenarios)
     - Resources (regulatory references)
   - Uncheck to hide that category

4. **View Results**
   - Results appear as cards below
   - Each card shows:
     - Content type (badge at top)
     - Title
     - Description
     - Relevance score
     - Action button

5. **Navigate to Details**
   - Click "View on Dashboard" → Goes to dashboard with that data
   - Click "View Principle" → Shows associated principle

### Search Examples

| Search Term | What You'll Find |
|-----------|------------------|
| "Attributable" | Principle definition + related tests |
| "Audit Trail" | Test case about user tracking |
| "electronic signature" | References to digital signatures |
| "backup" | Data retention and disaster recovery info |
| "contemporaneous" | Real-time recording requirement |

### Advanced Tips

- **Search is case-insensitive** → "AUDIT" = "audit"
- **Search looks at descriptions too** → Not just titles
- **Save common searches** → Write them down for quick access
- **Combine search + filter** → For narrowed results

---

## 3. Assessment Quiz

### What It Does
Test your knowledge of ALCOA+ principles and get certified.

### How to Use It

1. **Go to Assessment Tab**
   - Click "Assessment" button at the top

2. **Choose Quiz Mode**
   Three options appear:

   **Full Assessment**
   - 25 comprehensive questions
   - Covers all principles
   - Score 70%+ → Earn certificate
   - Takes about 15-20 minutes

   **Practice Mode**
   - 10 random questions
   - See answers right away
   - No scoring
   - Good for learning
   - No time limit

   **View Results**
   - See all your previous quiz attempts
   - Scores and dates
   - History kept in browser

3. **Take the Quiz**
   - Each question shows on a separate screen
   - Read the question carefully
   - Click one answer option
   - See immediate feedback
   - Click "Next Question" to continue

4. **Review Results**
   - Final score displays as percentage
   - Score breakdown shown
   - If 70%+: Certificate displays
   - Print certificate for your records

### Question Types

**Multiple Choice** (Most questions)
- 4 possible answers
- Only one is correct
- Select best answer

**Topics Covered**
- ALCOA+ principle definitions
- Implementation requirements
- Regulatory compliance
- Best practices
- Common mistakes to avoid

### Scoring

- **70-79%:** Passing score (Certificate earned)
- **80-89%:** Good comprehension
- **90-100%:** Excellent mastery

### Tips

- **Take practice mode first** → Learn before full assessment
- **Read explanations carefully** → They teach important concepts
- **Retake as needed** → No penalty for multiple attempts
- **Print certificates** → Keep for compliance records
- **Review failed questions** → Study those areas more

---

## 4. Progress Dashboard

### What It Does
Track your organization's implementation progress through the 6-phase ALCOA+ deployment.

### How to Use It

1. **Go to Progress Tab**
   - Click "Progress" button at the top

2. **Review Implementation Phases**
   - Displays 6 project phases
   - Shows completion % for each
   - Due dates listed
   - Status shows (Not Started, In Progress, Complete)

   **The 6 Phases:**
   - Phase 1: Assessment & Planning
   - Phase 2: Policy Development
   - Phase 3: System Enhancement
   - Phase 4: Training & Communication
   - Phase 5: Testing & Validation
   - Phase 6: Deployment & Monitoring

3. **Check Training Completion**
   - Shows completion by personnel role:
     - Auditors (how many trained)
     - Operators (how many trained)
     - Managers (how many trained)
     - QA Personnel (how many trained)
   - Percentage shown prominently

4. **Track Audit Completion**
   - Table shows audit status by system:
     - Baseline
     - Manufacturing
     - Quality
     - LIMS
     - ERP
   - Shows completed vs. total
   - Status badge (Not Started, In Progress, Complete)

### Interpretation Guide

**Progress Percentage**
- 0-33%: Just started, needs focus
- 34-66%: In progress, on track
- 67-99%: Almost done, final push
- 100%: Complete, well done!

**Status Colors** (by percentage)
- <50%: Not Started (Red)
- 50-89%: In Progress (Yellow)
- 90-100%: Complete (Green)

### How to Use This Data

- **Report to leadership** → Share progress updates
- **Identify bottlenecks** → See where you're stuck
- **Plan next steps** → Use to schedule next phases
- **Track trends** → Monitor improvements over time
- **Celebrate wins** → Recognize completed phases

### Tips

- **Check weekly** → Monitor progress
- **Share with team** → Keep everyone informed
- **Update as you complete items** → Keeps data accurate
- **Use for reporting** → Export or print for meetings

---

## 5. Real-Time Compliance Alerts

### What It Does
Automatically notifies you when compliance falls below target levels.

### How It Works

1. **Alert Appears Automatically**
   - Red banner at top of Dashboard
   - Shows when systems are below 80% compliance

2. **Alert Contains**
   - Title: "Compliance Alert: Areas Below Target"
   - Message: Which principles are failing
   - Close button: Dismiss (returns on refresh)

3. **What Triggers an Alert**
   - Any ALCOA+ principle < 80% compliance
   - When you switch scenarios in dashboard
   - Automatic on page load

### Example Alert Scenarios

**Manufacturing Scenario:**
- Alert shows because:
  - Contemporaneous compliance: 78%
  - Consistent compliance: 72%
- These are below 80% target

**Quality Scenario:**
- No alert because:
  - All principles are 90%+
  - All above 80% target

### What To Do When You See an Alert

1. **Read the alert message**
   - Identifies which areas are failing
   - Helps prioritize action

2. **Click principle name**
   - Go to Principles tab
   - Review detailed requirements
   - See test cases for that principle

3. **Check test cases**
   - Go to Dashboard tab
   - Use principle filter
   - Review failing test cases

4. **Take action**
   - Address root causes
   - Update systems/processes
   - Retest

5. **Dismiss alert**
   - Click X button
   - Alert will return if still below threshold

### Understanding Alert Thresholds

- **80%**: Industry best practice threshold
- **70-80%**: Needs improvement
- **Below 70%**: Critical action required
- **90%+**: Excellent compliance

### Tips

- **Don't ignore alerts** → They indicate real problems
- **Share with team** → Notify relevant departments
- **Track patterns** → See if same systems consistently alert
- **Use for CAPA** → Create corrective action plans
- **Monitor improvements** → Track progress toward 80%+

---

## Accessing New Features

### Navigation

All new features are easy to access from the top navigation:

```
[Dashboard] [Overview] [Principles] [Implementation] 
[Search & Filter] [Assessment] [Progress] [Resources]
```

Click any tab to navigate instantly.

### Mobile Access

All features work on mobile phones and tablets:
- Responsive design adapts to screen size
- Touch-friendly buttons (44px+)
- Readable on small screens
- No pinch-zoom needed

---

## Tips for Maximum Benefit

### Best Practices

1. **Export Regularly**
   - Weekly: Export current dashboard
   - Monthly: Archive for records
   - Quarterly: Review trends

2. **Use Search Daily**
   - Find specific principles
   - Locate test cases
   - Research requirements quickly

3. **Take Quiz Monthly**
   - Keep team trained
   - Certify new personnel
   - Validate understanding

4. **Monitor Progress Weekly**
   - Track implementation phases
   - Ensure on-time delivery
   - Celebrate milestones

5. **Act on Alerts**
   - Don't ignore alerts
   - Investigate root causes
   - Update systems immediately

### Common Workflows

**Daily:**
- Check Dashboard for compliance status
- Review alerts if any
- Update progress if applicable

**Weekly:**
- Review key metrics
- Check progress dashboard
- Export data for reports

**Monthly:**
- Full progress review
- Team quiz completion
- Compliance trending

**Quarterly:**
- Archive quarterly exports
- Review year-to-date progress
- Plan next quarter

---

## Troubleshooting

### Search Not Working?
1. Refresh page (search index builds on load)
2. Try simpler search terms
3. Check filter settings
4. Clear browser cache

### Export Failed?
1. Check browser download settings
2. Disable any popup blockers
3. Try different format
4. Try another browser

### Quiz Won't Show Results?
1. Make sure all questions answered
2. Refresh page
3. Check browser localStorage enabled
4. Try different browser

### Progress Data Not Saving?
1. Verify localStorage enabled
2. Check browser isn't in private mode
3. Clear browser cache
4. Restart browser

### Mobile Display Issues?
1. Refresh page
2. Rotate device to portrait
3. Try zooming out slightly
4. Use different browser

---

## Frequently Asked Questions

**Q: Can I export the data in bulk?**
A: Yes, all export formats include all data shown on dashboard.

**Q: Can I retake the quiz?**
A: Yes, unlimited times. Your history keeps all attempts.

**Q: How long does my quiz certificate last?**
A: Certificates are valid for 12 months from completion.

**Q: Can I edit progress data?**
A: Currently shown for informational purposes. Manual updates coming in Phase 3.

**Q: Do I need internet?**
A: Once loaded, the app works offline. Data saved in browser.

**Q: Can I print compliance reports directly?**
A: Yes, use "Print Dashboard" or export to HTML/PDF then print.

**Q: How many quiz attempts can I save?**
A: Up to 20 attempts in browser. Older ones are automatically archived.

**Q: Can multiple people use same browser?**
A: Yes, but they'll share search history and quiz results (saved in localStorage).

---

## Getting Help

### Where to Find Information

- **On ALCOA+ Principles** → Principles tab or search
- **On Implementation** → Implementation tab or Progress dashboard
- **On Regulations** → Resources tab
- **On Testing** → Dashboard tab test cases

### Reporting Issues

If something doesn't work:
1. Note the exact steps that caused issue
2. Try another browser
3. Contact your Quality Assurance department

---

## Summary

The new Phase 2 features make compliance management easier:
- **Export** → Share and archive data
- **Search** → Find information fast
- **Quiz** → Validate training and get certified
- **Progress** → Track implementation phases
- **Alerts** → Know when compliance drops

Use these tools to improve your organization's data integrity and maintain ALCOA+ compliance!

---

*Last Updated: 2026-08-29*  
*ALCOA+ Framework Version 2.0*  
*Phase 2 Complete*
