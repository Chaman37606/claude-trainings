# Quick Start Guide - Eli Lilly ALCOA+ QA System

## 🚀 Get Running in 5 Minutes

### Option 1: Local Setup (Recommended for Development)

#### Step 1: Install Dependencies
```bash
cd eli_lilly_alcoa_app
pip install -r requirements.txt
```

#### Step 2: Start Backend Server
```bash
python main.py
```
✓ API running at: `http://localhost:8000`
✓ Docs available at: `http://localhost:8000/docs`

#### Step 3: Start Frontend Server
Open a new terminal:
```bash
# Option A: Python
python -m http.server 8080

# Option B: Node.js (if installed)
npx http-server

# Option C: Direct in browser
Just open index.html directly in your browser
```

#### Step 4: Access the Application
Open your browser: `http://localhost:8080`

---

### Option 2: Docker (Production-Ready)

#### Prerequisites
- Docker and Docker Compose installed

#### Launch with One Command
```bash
docker-compose up
```

Access the application: `http://localhost:8080`
API Documentation: `http://localhost:8000/docs`

---

## ✅ Verify Installation

### Backend Health Check
```bash
curl http://localhost:8000/
```
Should return JSON with system info.

### API Documentation
Visit: `http://localhost:8000/docs`
Interactive Swagger UI with all endpoints.

### Test Data
System automatically creates test users:
- **Analyst** user for data entry
- **Reviewer** user for approvals

---

## 🎯 First Steps in the App

1. **Dashboard Tab**
   - See compliance statistics
   - Create your first QA record

2. **Create a QA Record**
   - Fill in batch number: `TEST-001`
   - Select test type: `Physical Testing`
   - Enter result: `98.5`
   - Set spec range: `95.0 - 105.0`
   - Click "Save Record"

3. **View Audit Trail**
   - Go to "Audit Trail" tab
   - Select your record
   - See the complete history with:
     - Who created it
     - When it was created
     - IP address
     - All field changes

4. **Check Compliance**
   - Go to "Compliance" tab
   - See ALCOA+ checklist
   - View compliance metrics

---

## 🔍 Key Features to Explore

### QA Records Tab
- List all quality assurance tests
- Filter by status (draft, submitted, approved)
- View detailed record information
- See creation timestamp and user

### Audit Trail Tab
- Complete history of every change
- User attribution for all actions
- IP address logging
- Before/after values for field changes
- Beautiful timeline visualization

### Compliance Dashboard
- Real-time compliance metrics
- ALCOA+ requirement checklist
- Approval rate calculation
- Record status breakdown

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Make sure port 8000 is free
lsof -i :8000

# If in use, kill the process
kill -9 <PID>
```

### Frontend won't load
- Check that backend is running on port 8000
- Try clearing browser cache
- Open developer console (F12) for errors

### CORS errors
- Make sure backend is running
- Check that frontend is accessing the correct API URL
- Backend CORS is already configured

### Database errors
```bash
# Reset database (removes all data)
rm alcoa_qc.db

# Restart backend (recreates empty database)
python main.py
```

---

## 📊 Sample Data Flow

1. Create record: Analyst enters test data
   - **Logged**: Create action by user_id, timestamp, IP
   
2. Submit for review: Record moves to submitted status
   - **Logged**: Submit action, timestamp, user
   
3. Approve: Reviewer approves the record
   - **Logged**: Approve action, approver user_id, timestamp
   
4. View history: Complete audit trail available
   - Shows all changes in chronological order
   - Tracks who did what and when

---

## 🔐 Default Credentials

For testing purposes, the system auto-creates:

```
User 1 (Analyst):
  Username: analyst
  Email: analyst@elililly.com
  Role: analyst

User 2 (Reviewer):
  Username: reviewer
  Email: reviewer@elililly.com
  Role: reviewer
```

---

## 📚 API Endpoints Quick Reference

### Records
```bash
# Create record
POST /api/qa-records
{ batch_number, test_type, result, specification_min, specification_max, notes }

# List records
GET /api/qa-records

# Get single record
GET /api/qa-records/{id}

# Update record
PUT /api/qa-records/{id}
{ updated fields }

# Submit for review
POST /api/qa-records/{id}/submit

# Approve
POST /api/qa-records/{id}/approve

# Reject
POST /api/qa-records/{id}/reject?reason=reason_text
```

### Audit & Compliance
```bash
# Get audit trail
GET /api/audit-logs/{record_id}

# Get compliance status
GET /api/compliance/status

# Get users
GET /api/users
```

---

## 🎓 Understanding ALCOA+

The system implements all ALCOA+ principles:

| Principle | Implementation |
|-----------|-----------------|
| **A**ttributable | User IDs, timestamps on all records |
| **L**egible | Clean UI, readable format |
| **C**ontemporaneous | Auto-timestamp at entry time |
| **O**riginal | Original data preserved, changes tracked |
| **A**ccurate | Validation, spec range checking |
| **A**uditability | Complete audit logs |
| **A**ccessibility | Role-based access control |
| **A**uthenticity | User/IP verification |
| **C**ompleteness | Required field validation |

---

## 💡 Tips & Best Practices

1. **Always check audit trail** before approving records
2. **Use descriptive batch numbers** for easy identification
3. **Add notes** for non-routine tests or deviations
4. **Review compliance metrics** regularly
5. **Export audit trails** for regulatory submissions
6. **Keep admin credentials secure** (production deployments)

---

## 📞 Need Help?

1. Check API docs: `http://localhost:8000/docs`
2. Review README.md for detailed documentation
3. Check browser console for frontend errors (F12)
4. Check terminal logs for backend errors

---

**Ready to go!** 🚀 Your ALCOA+ compliant QA system is now running.
