---
type: community
members: 5
---

# Market Data Integration

**Members:** 5 nodes

## Members
- [[fetch]] - code - mcp_client.js
- [[fetchMarketRate()]] - code - mcp_client.js
- [[fetchNav()]] - code - mcp_client.js
- [[mcp_client.js]] - code - mcp_client.js
- [[node-fetch]] - concept - package.json

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Market_Data_Integration
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_API & Calculation]]
- 1 edge to [[_COMMUNITY_Backend Agent]]
- 1 edge to [[_COMMUNITY_Frontend]]

## Top bridge nodes
- [[mcp_client.js]] - degree 6, connects to 2 communities
- [[node-fetch]] - degree 2, connects to 1 community