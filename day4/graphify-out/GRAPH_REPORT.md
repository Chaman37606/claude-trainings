# Graph Report - day4  (2026-09-19)

## Corpus Check
- Corpus is ~1,041 words - fits in a single context window. You may not need a graph.

## Summary
- 38 nodes · 40 edges · 8 communities (6 shown, 2 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- API & Calculation
- Backend Agent
- Frontend
- Market Data Integration
- Backend Startup
- NAV Data
- Server Setup

## God Nodes (most connected - your core abstractions)
1. `fetch` - 3 edges
2. `scripts` - 3 edges
3. `fetchNav()` - 2 edges
4. `fetchMarketRate()` - 2 edges
5. `express` - 2 edges
6. `cors` - 2 edges
7. `node-fetch` - 2 edges
8. `@anthropic-ai/sdk` - 2 edges
9. `run_agent.sh script` - 1 edges
10. `Anthropic` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (8 total, 2 thin omitted)

### Community 0 - "API & Calculation"
Cohesion: 0.25
Nodes (6): ref_path, app, cors, express, mcp, path

### Community 1 - "Backend Agent"
Cohesion: 0.29
Nodes (4): Anthropic, client, mcp, @anthropic-ai/sdk

### Community 2 - "Frontend"
Cohesion: 0.33
Nodes (5): main, name, version, cors, express

### Community 3 - "Market Data Integration"
Cohesion: 0.60
Nodes (4): fetch, fetchMarketRate(), fetchNav(), node-fetch

### Community 4 - "Backend Startup"
Cohesion: 0.40
Nodes (5): dependencies, @anthropic-ai/sdk, cors, express, node-fetch

### Community 5 - "NAV Data"
Cohesion: 0.67
Nodes (3): scripts, backend-agent, start

## Knowledge Gaps
- **18 isolated node(s):** `run_agent.sh script`, `Anthropic`, `mcp`, `client`, `name` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 25 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dependencies` connect `Backend Startup` to `Frontend`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `@anthropic-ai/sdk` connect `Backend Agent` to `Frontend`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `scripts` connect `NAV Data` to `Frontend`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **What connects `run_agent.sh script`, `Anthropic`, `mcp` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._