# Helios MCP Server

## Overview
Python MCP server for Helios Travel operations. Exposes travel booking, refund calculation, and escalation classification tools.

## Project Structure
- `travelops_mcp_server.py` - Main MCP server with tools, resources, and prompts
- `.venv/` - Python virtual environment
- `.mcp.json` - MCP server registration (project-scoped)

## Tools
- **get_booking**: Look up booking by ID (read-only, safe)
- **estimate_refund**: Calculate refund amount (no payment issued)
- **check_escalation**: Classify ticket for escalation (read-only risk analysis)
- **create_receipt_draft**: Generate receipt email draft (does not send)

## Resources
- **travelops://policy/refund** - Current refund and escalation policy

## Prompts
- **triage_travel_ticket** - Standardized triage workflow prompt

## Test Scenarios
1. Basic refund: `BK-1002` cancellation with full refund (amount > 50k, requires approval)
2. Risk escalation: Ticket with medical/compensation keywords (automatic escalation)

## Development
- Python 3.10+
- MCP v1 SDK (pinned to `mcp<2`)
- Run `claude` to launch and approve server
- Run `claude mcp list` to check registration status
