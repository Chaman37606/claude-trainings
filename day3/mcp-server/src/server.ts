import Anthropic from "@modelcontextprotocol/sdk";
import express from "express";
import cors from "cors";
import axios from "axios";
import * as dotenv from "dotenv";

dotenv.config();

const app = express();
const mcp = new Anthropic.Client({
  apiKey: process.env.ANTHROPIC_API_KEY || "",
});

app.use(cors());
app.use(express.json());

const MCP_PORT = parseInt(process.env.MCP_PORT || "3001", 10);
const SEARCH_PROVIDER = process.env.SEARCH_PROVIDER || "duckduckgo";

interface SearchResult {
  title: string;
  url: string;
  description: string;
  source: string;
}

interface SearchResponse {
  success: boolean;
  query: string;
  results: SearchResult[];
  total: number;
  provider: string;
  timestamp: string;
}

async function searchDuckDuckGo(query: string): Promise<SearchResult[]> {
  try {
    const response = await axios.get(
      `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=10`,
      {
        headers: {
          Accept: "application/json",
          "X-Subscription-Token": process.env.BRAVE_API_KEY || "",
        },
      }
    );

    return (
      response.data.web?.map(
        (result: { title: string; url: string; description: string }) => ({
          title: result.title,
          url: result.url,
          description: result.description || "No description available",
          source: "Brave Search",
        })
      ) || []
    );
  } catch {
    console.log("Brave Search failed, using mock data");
    return generateMockResults(query);
  }
}

function generateMockResults(query: string): SearchResult[] {
  return [
    {
      title: `Results for "${query}"`,
      url: `https://example.com/search?q=${encodeURIComponent(query)}`,
      description: `Search results about ${query}`,
      source: "Mock Search",
    },
    {
      title: `Learn about ${query}`,
      url: `https://wikipedia.example.com/${query}`,
      description: `Comprehensive information about ${query}`,
      source: "Mock Search",
    },
    {
      title: `${query} Guide`,
      url: `https://guide.example.com/${query}`,
      description: `Step-by-step guide to ${query}`,
      source: "Mock Search",
    },
  ];
}

// MCP Tool: Search
app.post("/mcp/search", async (req, res) => {
  const { query } = req.body;

  if (!query || typeof query !== "string" || query.trim() === "") {
    res.status(400).json({ error: "Query is required" });
    return;
  }

  const results = await searchDuckDuckGo(query);

  const response: SearchResponse = {
    success: true,
    query: query,
    results: results,
    total: results.length,
    provider: SEARCH_PROVIDER,
    timestamp: new Date().toISOString(),
  };

  res.json(response);
});

// MCP Tool: Extract content from URL
app.post("/mcp/extract", async (req, res) => {
  const { url } = req.body;

  if (!url || typeof url !== "string") {
    res.status(400).json({ error: "URL is required" });
    return;
  }

  try {
    const response = await axios.get(url, {
      headers: { "User-Agent": "Mozilla/5.0 MCP Server" },
      timeout: 10000,
    });

    const content = {
      url: url,
      status: response.status,
      contentType: response.headers["content-type"],
      contentLength: response.data.length,
      excerpt: response.data.substring(0, 500),
      timestamp: new Date().toISOString(),
    };

    res.json(content);
  } catch (error) {
    res.status(500).json({
      error: "Failed to extract content",
      details: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    mcp_version: "1.0.0",
    provider: SEARCH_PROVIDER,
    timestamp: new Date().toISOString(),
  });
});

// Tool discovery endpoint (for MCP clients)
app.get("/mcp/tools", (req, res) => {
  res.json({
    tools: [
      {
        name: "search",
        description: "Search the web for information",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query",
            },
          },
          required: ["query"],
        },
      },
      {
        name: "extract",
        description: "Extract content from a URL",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "URL to extract content from",
            },
          },
          required: ["url"],
        },
      },
    ],
  });
});

app.listen(MCP_PORT, () => {
  console.log(`🚀 MCP Server running on port ${MCP_PORT}`);
  console.log(`📊 Search Provider: ${SEARCH_PROVIDER}`);
  console.log(`🔍 API: http://localhost:${MCP_PORT}/mcp/search`);
  console.log(`📋 Tools: http://localhost:${MCP_PORT}/mcp/tools`);
});
