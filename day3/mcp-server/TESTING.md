# Testing Guide - MCP Search Server

## Prerequisites

- Both servers running (MCP on 3001, UI on 3000)
- curl or Postman for API testing
- Browser for UI testing

## API Testing

### 1. Health Check
```bash
curl http://localhost:3001/health
```

Expected Response:
```json
{
  "status": "healthy",
  "mcp_version": "1.0.0",
  "provider": "duckduckgo",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. List Available Tools
```bash
curl http://localhost:3001/mcp/tools
```

Expected Response:
```json
{
  "tools": [
    {
      "name": "search",
      "description": "Search the web for information",
      "inputSchema": { ... }
    },
    {
      "name": "extract",
      "description": "Extract content from a URL",
      "inputSchema": { ... }
    }
  ]
}
```

### 3. Web Search
```bash
curl -X POST http://localhost:3001/mcp/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'
```

Expected Response (200 OK):
```json
{
  "success": true,
  "query": "machine learning",
  "results": [
    {
      "title": "Machine Learning - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Machine_learning",
      "description": "Machine learning is a branch of artificial intelligence...",
      "source": "Brave Search"
    },
    ...
  ],
  "total": 10,
  "provider": "duckduckgo",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. Test Error Handling - Empty Query
```bash
curl -X POST http://localhost:3001/mcp/search \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'
```

Expected Response (400 Bad Request):
```json
{
  "error": "Query is required"
}
```

### 5. Content Extraction
```bash
curl -X POST http://localhost:3001/mcp/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Expected Response (200 OK):
```json
{
  "url": "https://example.com",
  "status": 200,
  "contentType": "text/html; charset=utf-8",
  "contentLength": 1256,
  "excerpt": "<!doctype html>...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 6. Test Error Handling - Invalid URL
```bash
curl -X POST http://localhost:3001/mcp/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://invalid-domain-12345.com"}'
```

Expected Response (500):
```json
{
  "error": "Failed to extract content",
  "details": "getaddrinfo ENOTFOUND invalid-domain-12345.com"
}
```

## Web UI Testing

### 1. Basic Search
- Open http://localhost:3000
- Enter "Python programming"
- Click Search
- Verify results display with title, URL, description

### 2. Multiple Searches
- Search for different terms
- Verify each returns different results
- Check result count updates

### 3. URL Extraction
- Paste URL in extract box
- Click Extract
- Verify content preview displays

### 4. Error Handling
- Try empty search → Should show error
- Try invalid URL → Should show error message
- Type in search, press Enter → Should trigger search

### 5. Responsive Design
- Open DevTools (F12)
- Toggle device toolbar (Ctrl+Shift+M)
- Test on Mobile, Tablet, Desktop
- Verify layout adapts

## Performance Testing

### Load Test - Multiple Searches
```bash
for i in {1..10}; do
  echo "Search $i..."
  curl -X POST http://localhost:3001/mcp/search \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"test query $i\"}" \
    -w "\nTime: %{time_total}s\n"
done
```

### Concurrent Requests
```bash
# Run 5 searches in parallel
for i in {1..5}; do
  curl -X POST http://localhost:3001/mcp/search \
    -H "Content-Type: application/json" \
    -d '{"query": "concurrent test"}' &
done
wait
```

## Integration Testing

### Test with Claude Code

1. Create Claude Code session in this project
2. Ask Claude to search: "search for machine learning frameworks"
3. Verify it uses the MCP search tool
4. Check results are returned correctly

### Test with cURL in Script
```bash
#!/bin/bash

# Function to test search
test_search() {
  local query="$1"
  echo "Testing search: $query"
  curl -s -X POST http://localhost:3001/mcp/search \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\"}" | jq '.results | length'
}

# Run tests
test_search "Python"
test_search "JavaScript"
test_search "Rust"
```

## Stress Testing

### High Volume Search
```bash
# Send 100 searches rapidly
ab -n 100 -c 10 -X POST -H "Content-Type: application/json" \
  -d '{"query":"test"}' \
  http://localhost:3001/mcp/search
```

### Long Content Extraction
```bash
# Test with large page
curl -X POST http://localhost:3001/mcp/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'
```

## Logging & Monitoring

### Check Server Logs
The server logs all requests to console:
```
[INFO] POST /mcp/search - "machine learning" query
[INFO] Found 10 results in 245ms
[ERROR] Failed to fetch https://invalid.com - Connection timeout
```

### Monitor Performance
```bash
# Watch real-time requests
watch 'curl -s http://localhost:3001/health | jq'
```

## Test Coverage Checklist

- [ ] Health check returns 200
- [ ] Tools endpoint lists both tools
- [ ] Search with valid query returns results
- [ ] Search with empty query returns error
- [ ] Extract with valid URL returns content
- [ ] Extract with invalid URL returns error
- [ ] Multiple searches work correctly
- [ ] Concurrent requests handled
- [ ] UI loads without errors
- [ ] Search from UI works
- [ ] Extract from UI works
- [ ] Error messages display in UI
- [ ] Results display properly formatted
- [ ] Responsive design works on mobile
- [ ] Docker build succeeds
- [ ] Docker run works correctly

## Known Issues & Workarounds

### Issue: "ECONNREFUSED" when starting UI
**Solution:** Ensure MCP server is running first on port 3001

### Issue: Search returns no results
**Solution:** Try different search terms, check API rate limits

### Issue: UI doesn't load
**Solution:** Clear browser cache (Ctrl+Shift+Delete), check console for errors

### Issue: Slow response times
**Solution:** Check internet connection, try simpler queries

## Performance Benchmarks

Expected performance on modern hardware:

- Search response time: 500-2000ms
- Content extraction: 1-5s
- UI load time: <1s
- Concurrent search (10): <5s total

## Reporting Issues

If tests fail, collect:
1. Error message from console
2. HTTP status code
3. Request/response bodies
4. Server logs
5. Steps to reproduce

Then check README.md Troubleshooting section.
