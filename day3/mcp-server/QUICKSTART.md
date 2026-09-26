# Quick Start Guide - MCP Search Server

## 5-Minute Setup

### Step 1: Install & Build
```bash
cd mcp-server
npm install
npm run build
```

### Step 2: Start MCP Server
```bash
npm start
```

You should see:
```
🚀 MCP Server running on port 3001
📊 Search Provider: duckduckgo
🔍 API: http://localhost:3001/mcp/search
📋 Tools: http://localhost:3001/mcp/tools
```

### Step 3: Start Web UI (New Terminal)
```bash
npm run serve-ui
```

### Step 4: Open Browser
Visit: **http://localhost:3000**

You're done! 🎉

## Using the Web UI

### Search
1. Type your search query in the search box
2. Press Enter or click Search
3. Browse results

### Extract Content
1. Paste a URL in the extract box
2. Click Extract
3. View the content preview

## API Usage

### Search via curl
```bash
curl -X POST http://localhost:3001/mcp/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence"}'
```

### Extract via curl
```bash
curl -X POST http://localhost:3001/mcp/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Docker Setup (Alternative)

```bash
docker-compose up --build
```

Then open http://localhost:3000

## Configuration

Edit `.env`:
```env
MCP_PORT=3001
UI_PORT=3000
SEARCH_PROVIDER=duckduckgo
BRAVE_API_KEY=your_key_here  # Optional: for better results
```

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 3001
lsof -i :3001 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**CORS errors?**
- Make sure MCP server is running on 3001
- Make sure UI is running on 3000
- Refresh browser

**No search results?**
- Check internet connection
- Try a different search term
- Check if API key is needed for your provider

## Next Steps

- Add to Claude Code: See README.md "Integration with Claude Code"
- Advanced configuration: See README.md
- API documentation: GET http://localhost:3001/mcp/tools
