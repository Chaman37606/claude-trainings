SIP Calculator (simple)

- Start:

```bash
npm install
npm start
```

- Open http://localhost:3000 in your browser.

- Backend subagent: `agents/backend/run_agent.sh` is a tiny runner that starts `server.js`.
- mCP client: `mcp_client.js` demonstrates fetching online NAV data from a public API.

Endpoints:
- `POST /api/calc` { amount, rate, years } -> { futureValue }
- `GET /api/nav/:id` -> { data }

