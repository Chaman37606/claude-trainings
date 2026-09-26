---
type: community
members: 3
---

# NAV Data

**Members:** 3 nodes

## Members
- [[backend-agent]] - code - package.json
- [[scripts]] - code - package.json
- [[start]] - code - package.json

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/NAV_Data
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Frontend]]

## Top bridge nodes
- [[scripts]] - degree 3, connects to 1 community