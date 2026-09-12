#!/usr/bin/env python3
"""
Post-hook: Log all tool executions to audit trail.
Runs after every tool use.
"""

import sys
import json
import sqlite3
from datetime import datetime

DATABASE_URL = "audit.db"


def main():
    # Read hook input from stdin
    hook_input = json.loads(sys.stdin.read())

    tool_name = hook_input.get("tool_name")
    tool_input = hook_input.get("tool_input", {})
    tool_output = hook_input.get("tool_output", {})
    execution_time = hook_input.get("execution_time", 0)

    # Log to audit database
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Insert audit log (note: actual structure matches AuditLogRecord)
        cursor.execute(
            """
            INSERT INTO audit_logs (audit_id, query_id, action, timestamp, user_id, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "hook_" + str(datetime.utcnow().timestamp()),
                "unknown",
                f"tool_executed: {tool_name}",
                datetime.utcnow().isoformat(),
                "system",
                json.dumps({"tool_name": tool_name, "execution_time": execution_time}),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        # Log error but don't fail the hook
        print(f"Warning: Failed to log to audit trail: {str(e)}", file=sys.stderr)

    # Allow the operation to complete
    result = {"allowed": True, "action": "allow"}
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
