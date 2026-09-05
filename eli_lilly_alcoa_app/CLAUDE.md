# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

Eli Lilly ALCOA+ QA System: A pharmaceutical-grade Quality Assurance data management system with complete audit trail compliance. FastAPI backend with SQLAlchemy ORM, SQLite/PostgreSQL database, and a professional HTML/CSS/JavaScript frontend.

---

## Quick Start Commands

### Development (Local)
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend (port 8000)
python main.py

# In another terminal, start frontend (port 8080)
python -m http.server 8080

# Access:
# - UI: http://localhost:8080
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Docker
```bash
# Build and run all services
docker-compose up

# Access: http://localhost:8080
```

### Database
```bash
# Reset database (deletes all data)
rm alcoa_qc.db

# Backup SQLite
sqlite3 alcoa_qc.db ".dump" > backup.sql
```

---

## Architecture Overview

### High-Level Data Flow
```
Frontend (HTML/JS)
    ↓
FastAPI REST API (port 8000)
    ↓
Pydantic Validation (schemas.py)
    ↓
CRUD Operations (crud.py)
    ↓
SQLAlchemy ORM → SQLite/PostgreSQL
    ↓
Automatic Audit Log Creation
    ↓
Response JSON → Frontend
```

### Key Pattern: Automatic Audit Trail
Every database change is automatically logged:
1. **Create/Update/Submit/Approve/Reject** operations in `crud.py` call `log_audit()`
2. `log_audit()` creates an `AuditLog` record with: user_id, action, field_name, old_value, new_value, timestamp, ip_address
3. Frontend retrieves audit logs for any record via `GET /api/audit-logs/{record_id}`

---

## File Structure & Purposes

### Backend Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app definition, all API endpoints, middleware setup |
| `models.py` | SQLAlchemy ORM models: `User`, `QARecord`, `AuditLog` |
| `schemas.py` | Pydantic models for request/response validation |
| `crud.py` | Database CRUD operations, audit logging, business logic |
| `database.py` | SQLAlchemy engine, session, and dependency injection |

### Frontend Files

| File | Purpose |
|------|---------|
| `index.html` | Single-file React app (29KB) with inline CSS and JavaScript |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Multi-container orchestration |
| `Dockerfile` | Backend containerization |
| `nginx.conf` | Reverse proxy configuration |
| `setup.sh` | Local development setup script |

---

## Database Schema

### Users Table
- `id` (int, PK)
- `username` (str, unique)
- `email` (str, unique)
- `full_name` (str)
- `role` (str: analyst, reviewer, admin)
- `is_active` (bool)
- `created_at` (datetime)

### QARecord Table
- `id` (int, PK)
- `batch_number` (str, indexed) - e.g., "BTH-2024-001"
- `test_type` (str) - Physical, Chemical, Microbial, Stability, Potency
- `result` (float)
- `specification_min` (float)
- `specification_max` (float)
- `notes` (text)
- `status` (str, indexed) - draft, submitted, approved, rejected
- `created_by` (int, FK to Users)
- `created_at` (datetime, indexed)
- `updated_at` (datetime)
- `submitted_at` (datetime, nullable)
- `approved_by` (int, FK to Users, nullable)
- `approved_at` (datetime, nullable)

### AuditLog Table
- `id` (int, PK)
- `qa_record_id` (int, FK, indexed)
- `user_id` (int, FK)
- `action` (str) - create, update, submit, approve, reject
- `field_name` (str, nullable) - Which field changed
- `old_value` (text, nullable)
- `new_value` (text, nullable)
- `timestamp` (datetime, indexed)
- `ip_address` (str, nullable)
- `notes` (text, nullable)

---

## API Endpoints

### QA Records
- `POST /api/qa-records` → Create record + auto audit log
- `GET /api/qa-records?skip=0&limit=100` → List records with pagination
- `GET /api/qa-records/{id}` → Get single record with audit logs
- `PUT /api/qa-records/{id}` → Update record, track all field changes
- `POST /api/qa-records/{id}/submit` → Change status to "submitted"
- `POST /api/qa-records/{id}/approve` → Change status to "approved"
- `POST /api/qa-records/{id}/reject?reason=text` → Change status to "rejected"

### Audit & Compliance
- `GET /api/audit-logs/{record_id}` → Timeline of all changes
- `GET /api/compliance/status` → Returns: total_records, approved, submitted, draft, compliance_rate, timestamp
- `GET /api/users` → List users (auto-creates test users if none exist)

### Root
- `GET /` → Health check, returns system info

All endpoints auto-generated docs available at `/docs` (Swagger UI)

---

## Key Development Patterns

### 1. Dependency Injection (FastAPI)
```python
# In main.py endpoints
async def create_qa_record(
    record: QARecordCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```
- `get_db()` from `database.py` provides database session
- `get_current_user()` gets or creates first user (simplified auth)
- `request` provides IP address via `get_client_ip(request)`

### 2. Automatic Audit Trail
Every CRUD operation calls `crud.log_audit()`:
```python
def log_audit(db, qa_record_id, user_id, action, field_name=None, 
              old_value=None, new_value=None, ip_address=None, notes=None):
    # Creates AuditLog entry automatically
```

### 3. Pydantic Validation
- `schemas.py` defines request models: `QARecordCreate`, `QARecordUpdate`
- FastAPI automatically validates and converts JSON to Pydantic models
- Invalid requests return 422 with detailed error messages

### 4. SQLAlchemy Relationships
```python
# User to QARecord (one-to-many)
qa_records = relationship("QARecord", foreign_keys="QARecord.created_by", ...)

# QARecord to AuditLog (one-to-many)
audit_logs = relationship("AuditLog", back_populates="qa_record")
```

---

## Common Development Tasks

### Add a New Endpoint
1. Define request schema in `schemas.py` if needed
2. Add CRUD operation in `crud.py` with audit logging
3. Add route in `main.py` using `@app.get/post/put` decorator
4. Docs auto-generate at `/docs`

### Modify Database Schema
1. Update model in `models.py`
2. Delete `alcoa_qc.db` to recreate on startup
3. Test with `python main.py`

### Track a New Field Change
1. In `crud.py`, the `update_qa_record()` function already handles field tracking
2. It compares old vs new values and logs each change
3. No additional code needed

### Change Audit Trail Data Retention
Edit `DEPLOYMENT.md` section "Audit Log Retention" for archival policies

### Add a New Role
1. Create role string (e.g., "supervisor")
2. Users table already supports arbitrary role strings
3. Frontend enforces role logic in index.html

### Migrate to PostgreSQL
1. Update `requirements.txt`: add `psycopg2-binary`
2. Update `database.py`: change `DATABASE_URL = "postgresql://user:pass@localhost/alcoa_db"`
3. Create database: `createdb alcoa_db`
4. Delete `alcoa_qc.db`, restart app

---

## Frontend Architecture

### Single File Design
`index.html` contains:
- **HTML Structure**: Tabs (Dashboard, Records, Audit, Compliance), forms, tables
- **CSS**: Professional theme with ALCOA+ compliance colors, responsive layout
- **JavaScript**: Fetch API calls to backend, tab switching, form handling, timeline rendering

### Key Frontend Functions
- `loadStats()` - Fetch compliance metrics
- `loadRecords()` - Fetch and display QA records
- `loadRecordsForAudit()` - Populate audit record selector
- `loadAuditTrail(recordId)` - Fetch and render audit timeline
- Tab navigation with `.nav-tab` click handlers

### Frontend-Backend Communication
All API calls via `fetch()` to `http://localhost:8000/api/*`
- CORS enabled in `main.py` (allow all origins for development)
- Content-Type: application/json
- No authentication headers (simplified implementation)

---

## Testing Workflow

### Manual Testing
1. Create a QA record with test data
2. Open Audit Trail tab, select record → see "create" action logged
3. Edit the record → see "update" actions with field changes
4. Submit record → see "submit" action logged
5. Approve/reject → see "approve"/"reject" with approver ID

### API Testing
```bash
# Create record
curl -X POST http://localhost:8000/api/qa-records \
  -H "Content-Type: application/json" \
  -d '{"batch_number": "TEST-001", "test_type": "Physical", "result": 98.5, "specification_min": 95, "specification_max": 105, "notes": "test"}'

# Get audit trail
curl http://localhost:8000/api/audit-logs/1

# Check compliance
curl http://localhost:8000/api/compliance/status
```

---

## Important Implementation Details

### ALCOA+ Compliance Built-In
- **Attributable**: Every action includes `user_id`, `ip_address` in audit log
- **Legible**: Professional UI with clear data presentation
- **Contemporaneous**: `timestamp` auto-set to `datetime.utcnow()` at action time
- **Original**: Old/new values preserved in `AuditLog.old_value`/`new_value`
- **Accurate**: Pydantic validation on all inputs, specification range checking
- **Auditability**: Complete `AuditLog` table with change history
- **Accessibility**: Role-based access via `current_user` dependency
- **Authenticity**: User and IP tracking in every audit entry
- **Completeness**: Required fields enforced in Pydantic schemas

### User Auto-Creation
- First call to `/api/users` creates test users if none exist
- First record creation picks first user from database (simplified auth)
- For production: implement proper OAuth2/JWT authentication

### Database Initialization
- `Base.metadata.create_all(bind=engine)` in `main.py` auto-creates tables
- `alcoa_qc.db` created on first run
- No migrations needed for development

### Error Handling
- FastAPI automatically returns 422 for validation errors
- 404 returned for non-existent records
- 500 for unhandled exceptions (check `/tmp/backend.log`)

---

## Configuration & Customization

### Change Default Database
Edit `database.py`:
```python
DATABASE_URL = "sqlite:///./alcoa_qc.db"  # or postgresql://user:pass@host/db
```

### Change API Port
Edit `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000 to desired port
```

### Change CORS Settings
Edit `main.py` middleware:
```python
allow_origins=["https://yourdomain.com"]  # Restrict origins for production
```

### Add Custom Business Logic
- Add validation in Pydantic schemas (`schemas.py`)
- Add business rules in CRUD operations (`crud.py`)
- Add endpoints in FastAPI routes (`main.py`)

---

## Security Notes (Development vs Production)

### Current (Development)
- ✓ No authentication required
- ✓ CORS allows all origins
- ✓ SQLite for simplicity
- ✓ HTTP only

### For Production (See DEPLOYMENT.md)
- [ ] Implement OAuth2/JWT authentication
- [ ] Restrict CORS to specific domains
- [ ] Use PostgreSQL with encrypted connections
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Add rate limiting
- [ ] Implement proper logging
- [ ] Set secure session cookies

---

## Documentation Files

| File | Content |
|------|---------|
| `README.md` | Full feature documentation |
| `QUICK_START.md` | 5-minute setup guide |
| `FEATURES.md` | Complete feature catalog |
| `DEPLOYMENT.md` | Production deployment guide |
| `PROJECT_OVERVIEW.md` | Architecture and design decisions |

---

## Next Steps for Development

1. **Understand the flow**: Follow a QA record from creation → approval in the code
2. **Review audit logging**: See how `log_audit()` is called in every CRUD operation
3. **Trace an endpoint**: Pick `/api/qa-records` and follow it through schemas → crud → database
4. **Test locally**: Create a record via UI or API, verify audit trail
5. **Customize**: Add new fields to `QARecord` model, schemas, and frontend forms

---

**Last Updated**: September 2026 | **Version**: 1.0.0 | **Status**: Production Ready (with configuration)
