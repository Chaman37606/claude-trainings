# Database Helper

Manage and inspect the SQLite database for the ALCOA QC application.

## Reset Database
```bash
rm -f alcoa_qc.db && python -c "from database import Base, engine; Base.metadata.create_all(engine)" && echo "Database reset successfully"
```

## View Database Tables
```bash
sqlite3 alcoa_qc.db ".tables"
```

## Run Database Migrations
```bash
python -c "from database import Base, engine; Base.metadata.create_all(engine)" && echo "Migrations completed"
```

## Check Database Size
```bash
ls -lh alcoa_qc.db | awk '{print "Database size: " $5}'
```

## Backup Database
```bash
cp alcoa_qc.db "alcoa_qc.backup.$(date +%Y%m%d_%H%M%S).db" && echo "Backup created"
```

## Query Records Count
```bash
sqlite3 alcoa_qc.db "SELECT name, COUNT(*) as count FROM sqlite_master WHERE type='table' GROUP BY name;"
```
