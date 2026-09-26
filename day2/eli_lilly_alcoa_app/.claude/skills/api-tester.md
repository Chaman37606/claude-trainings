# API Tester

Test and validate ALCOA QC API endpoints and CRUD operations.

## Start Development Server
```bash
python main.py &
sleep 2 && echo "Server started on http://localhost:8000"
```

## Test API Health
```bash
curl -s http://localhost:8000/docs 2>/dev/null && echo "✓ API is running" || echo "✗ API is not running"
```

## List All Records
```bash
curl -s http://localhost:8000/records/ | python -m json.tool | head -50
```

## Get Record by ID
```bash
curl -s "http://localhost:8000/records/1" | python -m json.tool
```

## Create Sample Record
```bash
curl -X POST http://localhost:8000/records/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Record", "status": "pending"}' | python -m json.tool
```

## Update Record
```bash
curl -X PUT "http://localhost:8000/records/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Record", "status": "completed"}' | python -m json.tool
```

## Delete Record
```bash
curl -X DELETE "http://localhost:8000/records/1"
```

## View API Docs
Open http://localhost:8000/docs in your browser
