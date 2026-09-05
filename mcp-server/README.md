# MCP Search Server

A Model Context Protocol (MCP) server for web search and content extraction with a beautiful web UI.

## Features

- 🔍 **Web Search** - Search the web with multiple provider options
- 📄 **Content Extraction** - Extract and preview content from URLs
- 🎨 **Modern Web UI** - Clean, responsive interface for easy searching
- 🔌 **MCP Integration** - Full Model Context Protocol support
- ⚡ **Fast & Reliable** - Optimized for performance

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Optional: Brave Search API key for better results

### Installation

```bash
# Clone/navigate to project
cd mcp-server

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Build TypeScript
npm run build
```

### Running

**Terminal 1 - Start MCP Server:**
```bash
npm start
# Server runs on http://localhost:3001
```

**Terminal 2 - Start Web UI:**
```bash
npm run serve-ui
# UI runs on http://localhost:3000
```

Then open http://localhost:3000 in your browser.

## Development

```bash
# Run in development mode with hot reload
npm run dev
```

## API Endpoints

### Search
```bash
POST /mcp/search
Content-Type: application/json

{
  "query": "machine learning"
}
```

**Response:**
```json
{
  "success": true,
  "query": "machine learning",
  "results": [
    {
      "title": "Machine Learning",
      "url": "https://...",
      "description": "...",
      "source": "Brave Search"
    }
  ],
  "total": 10,
  "provider": "duckduckgo",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Extract Content
```bash
POST /mcp/extract
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "status": 200,
  "contentType": "text/html",
  "contentLength": 5000,
  "excerpt": "...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Tools Discovery
```bash
GET /mcp/tools
```

Returns list of available MCP tools.

### Health Check
```bash
GET /health
```

## Configuration

Edit `.env` file:

```env
# Server ports
MCP_PORT=3001
UI_PORT=3000

# Search provider (duckduckgo, google, bing)
SEARCH_PROVIDER=duckduckgo

# Optional API Keys
BRAVE_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
APIFY_API_TOKEN=your_token_here
```

## Integration with Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "search": {
      "command": "node",
      "args": ["mcp-server/dist/server.js"],
      "env": {
        "MCP_PORT": "3001"
      }
    }
  }
}
```

## Search Providers

- **DuckDuckGo** (default) - No API key required, privacy-focused
- **Brave Search** - Requires API key, best results
- **Google** - Requires API key and credentials
- **Bing** - Requires API key

## Project Structure

```
mcp-server/
├── src/
│   └── server.ts          # MCP server implementation
├── public/
│   └── index.html         # Web UI
├── dist/                  # Compiled JavaScript (generated)
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
└── README.md              # This file
```

## Troubleshooting

### CORS Issues
Make sure both servers are running on different ports and the UI makes requests to the correct MCP_PORT.

### Search returns no results
- Check API key configuration if using paid providers
- Verify internet connection
- Try a different search query

### Port Already in Use
```bash
# Find process using port 3001
lsof -i :3001
# Kill it
kill -9 <PID>
```

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (index.html)   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  MCP Server     │
│  (server.ts)    │
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│  Search APIs    │
│  (Brave/Google) │
└─────────────────┘
```

## Future Enhancements

- [ ] Add web scraping with Puppeteer
- [ ] Implement caching layer
- [ ] Support for advanced query syntax
- [ ] Multi-language support
- [ ] Export results as CSV/JSON
- [ ] Scheduled searches
- [ ] Search history

## License

MIT

## Support

For issues or questions, check the MCP documentation at https://mcpservers.org
