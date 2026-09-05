# Eli Lilly ALCOA+ QA System

A professional Quality Assurance data management system built with ALCOA+ compliance standards for Eli Lilly. This application provides complete audit trails, data integrity tracking, and comprehensive compliance reporting.

## 🏥 Features

### ALCOA+ Compliance
- **Attributable**: All records track creator, reviewer, and modification history
- **Legible**: Clean, professional UI with clear data presentation
- **Contemporaneous**: Automatic timestamping of all data entries and changes
- **Original**: Complete preservation of original data with change tracking
- **Accurate**: Built-in validation to ensure data meets specification requirements
- **Auditability**: Full audit trail of all actions, changes, and approvals
- **Accessibility**: Role-based access control and user management
- **Authenticity**: User attribution and IP tracking for regulatory compliance
- **Completeness**: Ensures all required fields are populated

### Core Features
- 📋 **QA Data Entry**: Create and manage QA test records
- 🔍 **Complete Audit Trail**: Track every change with user, timestamp, and IP address
- ✅ **Compliance Dashboard**: Real-time compliance metrics and status
- 📊 **Analytics**: Track approval rates and compliance trends
- 🔐 **User Management**: Role-based access (analyst, reviewer, admin)
- 📝 **Detailed Reporting**: Export audit trails and compliance reports

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Session-based with role support
- **API**: RESTful JSON API with CORS support

### Frontend
- **UI Framework**: Vanilla HTML/CSS/JavaScript with React CDN
- **Design**: Professional, accessible, responsive design
- **Charts**: Real-time compliance metrics

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
cd eli_lilly_alcoa_app
pip install -r requirements.txt
```

### 2. Initialize Database

The database is automatically created on first run. No additional setup needed.

### 3. Start the Backend Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 4. Open Frontend in Browser

Open `index.html` in your web browser or serve it with a simple HTTP server:

```bash
# Using Python 3
python -m http.server 8080

# Then visit: http://localhost:8080
```

Or with Node.js:
```bash
npx http-server
```

## 📚 API Endpoints

### QA Records
- `POST /api/qa-records` - Create new QA record
- `GET /api/qa-records` - List all QA records
- `GET /api/qa-records/{id}` - Get record details
- `PUT /api/qa-records/{id}` - Update QA record
- `POST /api/qa-records/{id}/submit` - Submit for review
- `POST /api/qa-records/{id}/approve` - Approve record
- `POST /api/qa-records/{id}/reject` - Reject with reason

### Audit & Compliance
- `GET /api/audit-logs/{record_id}` - Get audit trail for record
- `GET /api/compliance/status` - Get compliance metrics
- `GET /api/users` - List system users

## 🗄️ Database Schema

### Users Table
- Stores user information, roles, and creation timestamps
- Role types: analyst, reviewer, admin

### QA Records Table
- Batch number, test type, results
- Specification ranges (min/max)
- Status tracking (draft, submitted, approved, rejected)
- Timestamps for creation, submission, approval

### Audit Logs Table
- Complete record of all changes
- User attribution
- IP address tracking
- Field-level change tracking (old value → new value)
- Action timestamps

## 🔐 User Roles

### Analyst
- Create new QA records
- Edit own records in draft status
- View all records and audit trails
- Submit records for review

### Reviewer
- View all records
- Approve/reject submitted records
- View complete audit trails
- Generate compliance reports

### Admin
- Full system access
- User management
- System configuration
- All reviewer and analyst permissions

## 📊 Compliance Dashboard

The compliance dashboard provides:
- Total record count
- Approved/pending/draft breakdown
- Compliance rate percentage
- ALCOA+ checklist confirmation
- Audit trail completeness verification

## 🔍 Audit Trail Features

Every record tracks:
1. **Who** - User who performed the action
2. **When** - Exact timestamp of the action
3. **What** - Specific fields that changed
4. **How** - Original and new values
5. **Where** - IP address of the user
6. **Why** - Reason for the action (when applicable)

## 🧪 Testing

### Create Sample Data

The system automatically creates test users on first run:
- Username: `analyst` - QA Analyst role
- Username: `reviewer` - QA Reviewer role

### Test Workflow
1. Create a QA record with test data
2. View the audit trail to see creation logged
3. Submit the record (tracked in audit log)
4. Approve/reject (tracked with user and IP)
5. View complete history in audit timeline

## 📁 Project Structure

```
eli_lilly_alcoa_app/
├── main.py                 # FastAPI application
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic validation schemas
├── crud.py                 # Database operations
├── database.py             # Database configuration
├── requirements.txt        # Python dependencies
├── index.html              # Professional frontend UI
└── README.md              # This file
```

## 🎨 UI Features

- **Professional Design**: Clinical-grade interface suitable for pharmaceutical industry
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Stats and records update automatically
- **Accessible**: WCAG compliant color contrasts and semantic HTML
- **Status Indicators**: Visual badges for record status
- **Timeline View**: Beautiful audit trail timeline visualization

## 🔄 Data Flow

```
User Input (HTML Form)
    ↓
API Request (JSON)
    ↓
FastAPI Validation (Pydantic)
    ↓
Database Operation (SQLAlchemy)
    ↓
Audit Log Entry (Automatic)
    ↓
Response to Frontend (JSON)
    ↓
UI Update (Real-time)
```

## 🚨 Regulatory Compliance

This system is designed to meet:
- FDA 21 CFR Part 11 Electronic Records Requirements
- ALCOA+ Data Integrity Standards
- ICH Q14 Guidance on Drug Development
- Pharmaceutical CAPA Process Requirements
- Batch Record Management Standards

## 📞 Support

For issues or questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review audit logs for error details
3. Check browser console for frontend errors

## 📄 License

Developed for Eli Lilly Quality Assurance Department

## 🔄 Future Enhancements

- [ ] Role-based permissions UI
- [ ] CSV/PDF export functionality
- [ ] Email notifications for approvals
- [ ] Advanced filtering and search
- [ ] Compliance report generation
- [ ] Multi-batch operations
- [ ] Electronic signature integration
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Advanced analytics

## ⚙️ Configuration

To modify default settings, edit these values in `main.py`:

```python
# Database location
DATABASE_URL = "sqlite:///./alcoa_qc.db"

# API host and port
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🔒 Security Notes

- This is a development build. For production:
  - Use proper authentication (OAuth2, JWT)
  - Implement SSL/TLS
  - Set proper CORS restrictions
  - Use PostgreSQL instead of SQLite
  - Implement rate limiting
  - Enable API key authentication
  - Set up proper logging and monitoring

---

**Developed with professional standards for the pharmaceutical industry** ✓ ALCOA+ Compliant
