#!/usr/bin/env python3
"""
Pre-hook: Enforce that only approved sources are retrieved.
Runs before any retrieval operation.
"""

import sys
import json
from src.config import is_approved_source


def main():
    # Read hook input from stdin
    hook_input = json.loads(sys.stdin.read())

    tool_name = hook_input.get("tool_name")
    tool_input = hook_input.get("tool_input", {})

    # Check if this is a retrieval operation
    if tool_name in ["retrieve_from_sources", "ApprovedRetriever.retrieve"]:
        # Check if source IDs are approved
        source_ids = tool_input.get("source_ids", [])
        for source_id in source_ids:
            if not is_approved_source(source_id):
                # Deny access to non-approved source
                result = {
                    "allowed": False,
                    "reason": f"Access denied: source {source_id} is not in approved allowlist",
                    "action": "deny",
                }
                print(json.dumps(result))
                sys.exit(0)

    # Allow the operation
    result = {"allowed": True, "action": "allow"}
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
