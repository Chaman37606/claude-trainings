# 🐛 Pharma Shipment Risk Analyzer - Bug & Issue Report

**Status:** Code Audit Complete  
**Date:** 2026-01-05  
**Version:** 1.0.0

---

## 🔴 **CRITICAL BUGS (Must Fix)**

### **Bug #1: Date Parsing Error in Risk Calculation**
**File:** `backend/models.py` (Line 120)  
**Severity:** 🔴 CRITICAL

**Issue:**
```python
delivery_delay_days = max(0, (datetime.now() - datetime.strptime(delivery_date, "%Y-%m-%d")).days - 7)
```

**Problem:** 
- Assumes delivery_date format is always "%Y-%m-%d"
- If date format is different (e.g., "01/15/2024"), crashes with ValueError
- No error handling for invalid dates

**Fix:**
```python
try:
    delivery_date_obj = datetime.strptime(str(delivery_date), "%Y-%m-%d")
    delivery_delay_days = max(0, (datetime.now() - delivery_date_obj).days - 7)
except (ValueError, TypeError):
    delivery_delay_days = 0  # Default to 0 if parsing fails
```

---

### **Bug #2: Memory Leak - Files Not Cleaned Up**
**File:** `backend/main.py` (Line 55-64)  
**Severity:** 🔴 CRITICAL

**Issue:**
```python
file_path = f"uploads/{file_id}_{file.filename}"
# File saved but NEVER deleted
# Uploaded files accumulate indefinitely
```

**Problem:**
- Uploaded files stay in `/uploads` folder forever
- No cleanup mechanism
- Will fill disk with old files
- Security risk (sensitive data not removed)

**Fix:**
```python
import atexit
import shutil
from datetime import datetime, timedelta

# Add cleanup on exit
def cleanup_old_uploads():
    """Remove files older than 24 hours"""
    if not os.path.exists("uploads"):
        return
    
    now = datetime.now()
    for filename in os.listdir("uploads"):
        file_path = os.path.join("uploads", filename)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_time > timedelta(hours=24):
            try:
                os.remove(file_path)
            except:
                pass

atexit.register(cleanup_old_uploads)
```

---

### **Bug #3: Frontend Variable Assignment Issue**
**File:** `frontend/app.js` (Line 27)  
**Severity:** 🔴 CRITICAL

**Issue:**
```javascript
document.getElementById('fileInput').files = files;  // ❌ WRONG
```

**Problem:**
- `files` property is READ-ONLY
- Cannot assign directly to `.files`
- Drag-and-drop doesn't actually work
- Only file input click works

**Fix:**
```javascript
// Instead of assigning files, process them directly
async function handleDroppedFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        // Process file directly
        handleFile(file);
    }
}

// Update drop handler
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    handleDroppedFiles(files);
});
```

---

## 🟠 **HIGH PRIORITY BUGS**

### **Bug #4: No Validation for Empty Files**
**File:** `backend/data_processor.py` (Line 75-90)  
**Severity:** 🟠 HIGH

**Issue:**
```python
df = pd.read_excel(file_path)
# No check if file is empty
# If CSV has no data rows, will crash downstream
```

**Fix:**
```python
@classmethod
def process_file(cls, file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    
    # Check if empty
    if len(df) == 0:
        raise ValueError("File contains no data rows")
    
    # Rest of processing...
```

---

### **Bug #5: Risk Score Can Exceed 100**
**File:** `backend/models.py` (Line 94-106)  
**Severity:** 🟠 HIGH

**Issue:**
```python
risk_score = (
    (temp_impact * 0.40) +
    (delay_impact * 0.30) +
    (incident_impact * 0.20) +
    (compliance_impact * 0.10)
)
return round(min(100, risk_score), 2)  # ✓ Good
```

**Actually OK**, but incident calculation can exceed limits:

```python
def calculate_incident_impact(incident_count: int) -> float:
    return min(100, incident_count * 25)  # Each incident = 25 points
    # ✓ Already capped
```

**Status:** ✓ This is actually handled correctly

---

### **Bug #6: No Protection Against SQL/CSV Injection**
**File:** `backend/main.py` (Line 55)  
**Severity:** 🟠 HIGH

**Issue:**
```python
file_path = f"uploads/{file_id}_{file.filename}"  # Uses user input directly
```

**Problem:**
- File name could contain path traversal (e.g., `../../../etc/passwd`)
- Could write files outside uploads folder

**Fix:**
```python
import re

# Sanitize filename
def sanitize_filename(filename):
    # Remove path separators and special chars
    filename = re.sub(r'[/\\]', '', filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename[:100]  # Max 100 chars

# Usage
safe_filename = sanitize_filename(file.filename)
file_path = f"uploads/{file_id}_{safe_filename}"
```

---

## 🟡 **MEDIUM PRIORITY ISSUES**

### **Issue #7: No Error Handling for Missing API Keys**
**File:** `backend/models.py`  
**Severity:** 🟡 MEDIUM

**Issue:**
- If Claude API call fails, entire analysis fails
- No fallback mechanism
- Users get vague error messages

**Fix:**
```python
async def get_recommendations(file_id: str):
    try:
        # Call Claude API
        pass
    except Exception as e:
        # Return default recommendations instead of crashing
        return {
            "recommendations": [
                "Unable to generate AI recommendations at this time",
                "Review high-risk shipments manually"
            ],
            "error": str(e)
        }
```

---

### **Issue #8: No Pagination for Large Files**
**File:** `frontend/app.js`  
**Severity:** 🟡 MEDIUM

**Issue:**
- If file has 10,000+ shipments, browser becomes slow
- All data loaded at once into DOM
- No pagination or lazy loading

**Fix:**
```javascript
// Add pagination to top 5 list
const ITEMS_PER_PAGE = 5;
let currentPage = 1;

function displayRisksWithPagination(risks, page = 1) {
    const start = (page - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageRisks = risks.slice(start, end);
    
    // Render only page items
    renderRisks(pageRisks);
}
```

---

### **Issue #9: No HTTPS/SSL Configuration**
**File:** `backend/main.py`  
**Severity:** 🟡 MEDIUM

**Issue:**
- Running over HTTP (not secure)
- No SSL certificates
- Not suitable for production with real data

**Fix:**
```bash
# For production, use:
# 1. Self-signed certificate (testing)
# 2. Let's Encrypt (production)
# 3. Nginx reverse proxy with SSL
```

---

### **Issue #10: Analysis Results Lost on Server Restart**
**File:** `backend/main.py` (Line 31)  
**Severity:** 🟡 MEDIUM

**Issue:**
```python
analysis_cache = {}  # In-memory, lost on restart
```

**Problem:**
- All uploaded files and analysis disappear on restart
- No persistence

**Fix:**
```python
import json

# Save to file
def save_analysis(file_id, analysis):
    with open(f"cache/{file_id}.json", 'w') as f:
        json.dump(analysis, f)

# Load from file
def load_analysis(file_id):
    try:
        with open(f"cache/{file_id}.json", 'r') as f:
            return json.load(f)
    except:
        return None
```

---

## 🟢 **LOW PRIORITY ISSUES**

### **Issue #11: Hardcoded API URL**
**File:** `frontend/app.js` (Line 5)  
**Severity:** 🟢 LOW

**Issue:**
```javascript
const API_BASE = 'http://localhost:8000/api';  // Hard-coded
```

**Fix:**
```javascript
const API_BASE = window.API_URL || 'http://localhost:8000/api';
// Can be set via environment variable or config
```

---

### **Issue #12: No Loading Animation for Chart**
**File:** `frontend/app.js` (Line 120)  
**Severity:** 🟢 LOW

**Issue:**
- Chart renders instantly but might be jarring
- No fade-in animation

**Fix:**
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.chart-card {
    animation: fadeIn 0.5s ease-in;
}
```

---

### **Issue #13: No Timezone Handling**
**File:** `backend/models.py`  
**Severity:** 🟢 LOW

**Issue:**
```python
datetime.now()  # Uses server timezone
```

**Better:**
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)  # Always UTC
```

---

## 📋 **PRIORITY FIX ORDER**

| Priority | Bug | File | Impact |
|----------|-----|------|--------|
| 🔴 P0 | Date parsing crash | models.py:120 | System fails |
| 🔴 P0 | Files not cleaned | main.py:55-64 | Disk fills up |
| 🔴 P0 | Drag-drop broken | app.js:27 | Feature doesn't work |
| 🟠 P1 | Empty file crash | data_processor.py:75 | System fails |
| 🟠 P1 | Path traversal risk | main.py:55 | Security issue |
| 🟠 P1 | API error handling | models.py | Bad UX |
| 🟡 P2 | Pagination | app.js | Performance |
| 🟡 P2 | No persistence | main.py:31 | Data loss |
| 🟢 P3 | Hardcoded URL | app.js:5 | Maintainability |

---

## ✅ **WHAT'S WORKING WELL**

✅ Risk calculation algorithm (correct logic)  
✅ Temperature excursion detection  
✅ Top 5 shipments ranking  
✅ Dashboard UI/UX  
✅ Chart rendering (Chart.js integration)  
✅ CORS configuration  
✅ File upload mechanism (basic)  
✅ API endpoint structure  

---

## 🔧 **QUICK FIXES NEEDED**

### **Step 1: Fix Date Parsing (Fixes Bug #1)**
```python
# In models.py, update line 120:
try:
    delivery = datetime.strptime(str(delivery_date), "%Y-%m-%d")
    days_delayed = max(0, (datetime.now() - delivery).days - 7)
except (ValueError, TypeError):
    days_delayed = 0
```

### **Step 2: Fix Drag-Drop (Fixes Bug #3)**
```javascript
// In app.js, update drop handler:
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
        handleFileSelect.call({
            target: { files: e.dataTransfer.files }
        });
    }
});
```

### **Step 3: Add File Cleanup (Fixes Bug #2)**
```python
# Add to main.py:
import atexit
import shutil

def cleanup():
    if os.path.exists("uploads"):
        shutil.rmtree("uploads", ignore_errors=True)

atexit.register(cleanup)
```

---

## 📊 **Bug Summary**

| Category | Count | Status |
|----------|-------|--------|
| Critical | 3 | 🔴 Need Fixes |
| High | 3 | 🟠 Should Fix |
| Medium | 4 | 🟡 Nice to Fix |
| Low | 3 | 🟢 Optional |
| **Total** | **13** | ⚠️ |

---

## 🎯 **Recommended Action**

**Fix the 3 CRITICAL bugs immediately:**
1. Date parsing error
2. File cleanup mechanism
3. Drag-and-drop

**These prevent features from working properly.**

---

Would you like me to fix these bugs? I can implement all the fixes! 🔧
