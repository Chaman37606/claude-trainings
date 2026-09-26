# 🪝 Claude Code Hooks Reference

Complete documentation of all 5 hooks configured for the Eli Lilly ALCOA+ QA System.

## 📍 Location
**File**: `.claude/settings.json`

---

## 🎯 All 5 Hooks Overview

| # | Event | Trigger | Purpose |
|---|-------|---------|---------|
| 1 | `SessionStart` | Session launches | Initialize environment |
| 2 | `PreToolUse` | Before Bash command | Validate environment |
| 3 | `PostToolUse` (Bash) | After Bash command | Cleanup artifacts |
| 4 | `PostToolUse` (Write\|Edit) | After file edit | Log modifications |
| 5 | `Stop` | Session exits | Final cleanup |

---

## 📋 Detailed Hook Specifications

### **Hook #1: SessionStart**
**Event**: `SessionStart`  
**Trigger**: When Claude Code session launches  
**Type**: `command`

```json
{
  "matcher": "",
  "hooks": [
    {
      "type": "command",
      "command": "echo '🚀 Eli Lilly ALCOA+ QA System session started' && echo 'Backend: http://localhost:8000' && echo 'Frontend: http://localhost:8080' && echo 'API Docs: http://localhost:8000/docs'",
      "statusMessage": "Initializing ALCOA+ QA System"
    }
  ]
}
```

**What it does**:
- ✅ Displays startup banner
- ✅ Shows available endpoints
- ✅ Provides quick reference links

**Output**:
```
🚀 Eli Lilly ALCOA+ QA System session started
Backend: http://localhost:8000
Frontend: http://localhost:8080
API Docs: http://localhost:8000/docs
```

**Use Case**: Quick reminder of where to access the application

---

### **Hook #2: PreToolUse (Bash)**
**Event**: `PreToolUse`  
**Trigger**: Before any Bash command executes  
**Type**: `command`

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "echo '[Pre-check] Validating environment...' && python -c 'import fastapi; import sqlalchemy; print(\"✓ Dependencies OK\")' 2>/dev/null || echo '⚠ Missing dependencies'",
      "statusMessage": "Validating Python environment",
      "timeout": 5
    }
  ]
}
```

**What it does**:
- ✅ Validates Python environment
- ✅ Checks if FastAPI and SQLAlchemy are installed
- ✅ Warns if dependencies missing

**Output**:
```
[Pre-check] Validating environment...
✓ Dependencies OK
```

**Use Case**: Catch missing dependencies before running commands

**Timeout**: 5 seconds

---

### **Hook #3: PostToolUse (Bash - Cleanup)**
**Event**: `PostToolUse`  
**Trigger**: After Bash command completes  
**Type**: `command`

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "rm -rf ./dist 2>/dev/null; find /tmp -name '*claude*' -type f -mtime +7 -delete 2>/dev/null || true",
      "statusMessage": "Cleaning up build artifacts and temp logs",
      "timeout": 10
    }
  ]
}
```

**What it does**:
- ✅ Removes `./dist` directory
- ✅ Deletes temp logs older than 7 days from `/tmp`
- ✅ Suppresses errors silently

**Command breakdown**:
```bash
# Remove dist directory
rm -rf ./dist 2>/dev/null

# Find and delete old temp logs
find /tmp -name '*claude*' -type f -mtime +7 -delete 2>/dev/null || true
```

**Timeout**: 10 seconds

**Frequency**: Runs after every Bash command

---

### **Hook #4: PostToolUse (Write|Edit - File Logging)**
**Event**: `PostToolUse`  
**Trigger**: After file is created or edited  
**Type**: `command`

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "find . -name '*.py' -type f -newer /tmp/.last_edit 2>/dev/null | head -1 | xargs -I {} echo 'Modified: {}' || true",
      "statusMessage": "Logging file modifications",
      "timeout": 5
    }
  ]
}
```

**What it does**:
- ✅ Finds recently modified Python files
- ✅ Logs the file path
- ✅ Updates modification timestamp

**Output**:
```
Modified: /home/labuser/claude_training/eli_lilly_alcoa_app/main.py
```

**Timeout**: 5 seconds

**Use Case**: Track which files have been edited

---

### **Hook #5: Stop (Session Exit Cleanup)**
**Event**: `Stop`  
**Trigger**: When Claude Code session terminates  
**Type**: `command`

```json
{
  "matcher": "",
  "hooks": [
    {
      "type": "command",
      "command": "rm -rf ./dist 2>/dev/null; rm -f /tmp/backend.log /tmp/frontend.log /tmp/.last_edit 2>/dev/null || true",
      "statusMessage": "Cleaning up dist directory and temp logs"
    }
  ]
}
```

**What it does**:
- ✅ Removes `./dist` directory
- ✅ Removes backend log: `/tmp/backend.log`
- ✅ Removes frontend log: `/tmp/frontend.log`
- ✅ Removes edit tracker: `/tmp/.last_edit`

**Command breakdown**:
```bash
# Remove dist
rm -rf ./dist 2>/dev/null

# Remove specific log files
rm -f /tmp/backend.log /tmp/frontend.log /tmp/.last_edit 2>/dev/null || true
```

**Trigger**: Only on session exit, not on every operation

---

## 🔄 Hook Execution Timeline

```
Session Start
    ↓
[Hook #1: SessionStart] - Show welcome banner
    ↓
User runs: python main.py
    ↓
[Hook #2: PreToolUse] - Validate environment
    ↓
Command executes
    ↓
[Hook #3: PostToolUse - Bash] - Cleanup dist and old logs
    ↓
User edits: main.py
    ↓
[Hook #4: PostToolUse - Write|Edit] - Log modification
    ↓
User exits Claude
    ↓
[Hook #5: Stop] - Final cleanup
```

---

## 📊 Hook Statistics

| Hook | Event Type | Matcher | Timeout | Frequency |
|------|-----------|---------|---------|-----------|
| #1 | SessionStart | None | None | Once at start |
| #2 | PreToolUse | Bash | 5s | Before each Bash |
| #3 | PostToolUse | Bash | 10s | After each Bash |
| #4 | PostToolUse | Write\|Edit | 5s | After each edit |
| #5 | Stop | None | None | Once at exit |

---

## ✅ What Gets Cleaned Up

### **After Each Bash Command** (Hook #3)
- `./dist/` - Build output directory
- `/tmp/*claude*` - Old temp files (>7 days)

### **On Session Exit** (Hook #5)
- `./dist/` - Build directory
- `/tmp/backend.log` - Backend logs
- `/tmp/frontend.log` - Frontend logs
- `/tmp/.last_edit` - Edit tracker file

### **What's NOT Cleaned**
- Database files (`.db`)
- Project source code
- Environment files (`.env`)
- Git history

---

## 🔧 Customizing Hooks

### View All Hooks
```bash
cat .claude/settings.json | grep -A 20 "hooks"
```

### Edit Hooks
1. Open `.claude/settings.json`
2. Modify the `command` field
3. Save and restart session

### Add New Hook
```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "your-command-here",
      "statusMessage": "Description shown in UI",
      "timeout": 10
    }
  ]
}
```

### Disable a Hook
Remove the entire hook object from the JSON, OR set `statusMessage` to empty.

---

## 🎯 Hook Matchers Reference

| Matcher | Applies To |
|---------|-----------|
| `"Bash"` | Bash commands |
| `"Write"` | File writes (new files) |
| `"Edit"` | File edits (existing files) |
| `"Write|Edit"` | Both writes and edits |
| `""` | All operations (for SessionStart/Stop) |

---

## 💾 Clean Directory Structure After Hooks

```
eli_lilly_alcoa_app/
├── .claude/
│   └── settings.json          (Hook config)
├── src/
│   └── utils/
├── main.py
├── models.py
├── database.py
├── schemas.py
├── crud.py
├── requirements.txt
├── .env.production
├── .gitignore
└── alcoa_qc.db               (Database - preserved)
    
# These are REMOVED by hooks:
# ✗ dist/                     (Removed by hooks #3, #5)
# ✗ /tmp/backend.log          (Removed by hook #5)
# ✗ /tmp/frontend.log         (Removed by hook #5)
# ✗ /tmp/*claude*             (Removed by hook #3)
```

---

## 🚀 Best Practices

1. **SessionStart Hook**: Quick reference for endpoints
2. **PreToolUse Hook**: Catch errors before they happen
3. **PostToolUse (Bash) Hook**: Keep workspace clean
4. **PostToolUse (Edit) Hook**: Track code changes
5. **Stop Hook**: Final cleanup on exit

---

## 📌 Summary Table

```
Hook #1: SessionStart        → Welcome banner
Hook #2: PreToolUse (Bash)   → Validate deps
Hook #3: PostToolUse (Bash)  → Clean artifacts
Hook #4: PostToolUse (Edit)  → Log changes
Hook #5: Stop                → Final cleanup
```

All hooks work together to maintain a clean, organized development environment! 🎯
