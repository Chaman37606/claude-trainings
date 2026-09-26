Backend subagent

Description:
- This agent is a simple backend subagent that runs the Express server and exposes the SIP calculation API and an mCP-backed NAV fetcher.

Run:
- Start the backend subagent with `sh agents/backend/run_agent.sh` (or `node server.js`).

Notes:
- The mCP client lives at `mcp_client.js` and fetches NAVs from a public example API.
