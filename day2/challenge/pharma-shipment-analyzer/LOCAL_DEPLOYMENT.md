# 🏥 Local Deployment Guide - Pharma Shipment Risk Analyzer

## ✅ Installation Complete!

Dependencies have been installed. Your application is ready to run locally.

---

## 🚀 Start the Application (3 Steps)

### **Step 1: Navigate to Project**
```bash
cd /home/labuser/claude_training/challenge/pharma-shipment-analyzer
```

### **Step 2: Start Backend (Terminal 1)**
```bash
bash run-backend.sh
```

**Expected output:**
```
🚀 Starting Pharma Shipment Risk Analyzer - BACKEND
==================================================
Backend API will run on: http://localhost:8000
API Documentation: http://localhost:8000/docs

INFO:     Started server process [1234]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Step 3: Start Frontend (Terminal 2 - New Window)**
```bash
bash run-frontend.sh
```

**Expected output:**
```
🚀 Starting Pharma Shipment Risk Analyzer - FRONTEND
====================================================
Frontend Dashboard will run on: http://localhost:3000

Starting up http-server, serving ./
Available on:
  http://localhost:3000
```

---

## 🌐 Access Your Application

### **Main Dashboard**
👉 **http://localhost:3000**

### **Backend API**
👉 **http://localhost:8000/api**

### **API Documentation (Swagger)**
👉 **http://localhost:8000/docs**

### **Health Check**
👉 **http://localhost:8000/health**

---

## 📊 Using the Dashboard

1. **Open http://localhost:3000 in your browser**
2. **Click "Choose File"**
3. **Upload any Excel file with these columns:**
   - shipment_id
   - origin
   - destination
   - temp_min
   - temp_max
   - temp_actual
   - status
   - delivery_date
   - handler_id
   - incidents
   - regulatory_flags

4. **View instant analysis!**
   - ✅ Total shipments
   - ✅ High-risk count
   - ✅ Temperature excursions
   - ✅ Risk distribution chart
   - ✅ Top 5 highest-risk
   - ✅ AI recommendations

---

## 📝 Sample Excel File

Create a test file with this structure:

| shipment_id | origin | destination | temp_min | temp_max | temp_actual | status | delivery_date | handler_id | incidents | regulatory_flags |
|---|---|---|---|---|---|---|---|---|---|---|
| SHP-2024-001 | NYC | Boston | 2 | 8 | 27.5 | Delivered | 2024-01-15 | H001 | 1 | FDA Investigation |
| SHP-2024-002 | LA | SF | 2 | 8 | 5.2 | Delivered | 2024-01-14 | H002 | 0 | - |
| SHP-2024-003 | Chicago | Miami | 2 | 8 | 26.8 | Delivered | 2024-01-13 | H003 | 0 | - |

---

## 🔗 API Endpoints

### Upload File
```bash
POST http://localhost:8000/api/upload
Content-Type: multipart/form-data
Body: file (Excel file)
```

### Get Dashboard Stats
```bash
GET http://localhost:8000/api/stats/{file_id}
```

### Get High-Risk Shipments
```bash
GET http://localhost:8000/api/risks/high/{file_id}
```

### Get Chart Data
```bash
GET http://localhost:8000/api/chart-data/{file_id}
```

### Get AI Recommendations
```bash
GET http://localhost:8000/api/recommendations/{file_id}
```

### Export Report
```bash
GET http://localhost:8000/api/export/{file_id}?format=json
```

---

## 🧪 Test with cURL

### Health Check
```bash
curl http://localhost:8000/health
```

### List Available Files
```bash
curl http://localhost:8000/api/files
```

---

## 🛑 Stopping the Application

**In each terminal, press:**
```
Ctrl + C
```

---

## 📋 Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Can open dashboard without errors
- [ ] Can upload Excel file
- [ ] Dashboard metrics display
- [ ] Chart renders
- [ ] Recommendations appear
- [ ] No console errors (check browser DevTools)

---

## 🆘 Troubleshooting

### Port 8000 Already in Use
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Port 3000 Already in Use
```bash
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Backend Error: "Module not found"
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Not Loading
- Check browser console (F12)
- Verify backend is running
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito/private window

### File Upload Error
- Ensure Excel has all required columns
- Check file size (<10MB)
- Verify data types (numbers for temperatures)

---

## 📱 Browser Compatibility

✅ Chrome/Edge 90+
✅ Firefox 88+
✅ Safari 14+
✅ Mobile browsers

---

## 🎯 Next Steps

1. ✅ Start both servers
2. ✅ Open http://localhost:3000
3. ✅ Upload a test file
4. ✅ Explore the dashboard
5. ✅ Check AI recommendations
6. ✅ Review API documentation at http://localhost:8000/docs

---

## 📊 Example Dashboard View

When you upload a file:

```
┌──────────────────────────────────────────┐
│ PHARMA SHIPMENT RISK ANALYZER            │
├──────────────────────────────────────────┤
│                                          │
│ 📦 Total: 1,245  🚨 High-Risk: 87       │
│ 🌡️  Excursions: 12  📊 Avg Risk: 45.2   │
│                                          │
│ [Risk Distribution Pie Chart]            │
│                                          │
│ 🔝 Top 5 High-Risk                       │
│ 1. SHP-2024-001 - 95/100 ⚠️              │
│ 2. SHP-2024-015 - 92/100 ⚠️              │
│ 3. SHP-2024-042 - 88/100 ⚠️              │
│ 4. SHP-2024-058 - 85/100 ⚠️              │
│ 5. SHP-2024-031 - 82/100 ⚠️              │
│                                          │
│ 💡 AI Recommendations                    │
│ • Temperature excursions in Route A      │
│ • Implement monitoring checkpoints       │
│ • Ensure FDA documentation               │
│                                          │
└──────────────────────────────────────────┘
```

---

## ✅ You're All Set!

Your Pharma Shipment Risk Analyzer is ready to use locally.

**Start with:** `bash run-backend.sh` in one terminal, then `bash run-frontend.sh` in another.

**Access:** http://localhost:3000

Happy analyzing! 🏥✨

---

**Status: Ready for Local Deployment** ✅
**Version: 1.0.0**
**Last Updated: 2025-01-05**
