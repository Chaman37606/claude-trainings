# Quick Start - Pharma Shipment Risk Analyzer

Get started in 5 minutes!

## 1️⃣ Install Dependencies

```bash
cd pharma-shipment-analyzer
pip install -r backend/requirements.txt
```

## 2️⃣ Start Backend (Terminal 1)

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 3️⃣ Start Frontend (Terminal 2)

```bash
cd frontend
npx http-server . -p 3000
```

You should see:
```
Starting up http-server, serving ./
Available on:
  http://localhost:3000
```

## 4️⃣ Open Dashboard

Go to: **http://localhost:3000**

## 5️⃣ Upload Sample Data

1. Click "Choose File"
2. Select any Excel file with these columns:
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

3. Click Upload

4. View instant analysis! 📊

## 📊 What You'll See

✅ Total shipments count  
✅ High-risk shipments highlighted  
✅ Temperature excursions flagged  
✅ Risk distribution pie chart  
✅ Top 5 highest-risk shipments  
✅ AI-powered recommendations  

## 🧪 Sample Excel Structure

| shipment_id | origin | destination | temp_min | temp_max | temp_actual | status | delivery_date | handler_id | incidents | regulatory_flags |
|-------------|--------|-------------|----------|----------|-------------|--------|---------------|-----------|-----------|------------------|
| SHP-2024-001 | NYC | Boston | 2 | 8 | 27.5 | Delivered | 2024-01-15 | H001 | 1 | FDA Investigation |
| SHP-2024-002 | LA | SF | 2 | 8 | 5.2 | Delivered | 2024-01-14 | H002 | 0 | - |

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 3000
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Module Not Found
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Can't Reach API
- Make sure backend is running on http://localhost:8000
- Check backend terminal for errors
- Wait 2-3 seconds after starting

## 📖 Next Steps

1. ✅ Upload your first file
2. ✅ Explore the dashboard
3. ✅ Review AI recommendations
4. ✅ Check CLAUDE.md for advanced features

## 🚀 Production

See README.md for Docker and cloud deployment options.

---

**All set? Upload a file and start analyzing! 🎯**
