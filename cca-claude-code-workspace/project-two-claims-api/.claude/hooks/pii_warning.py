import json
import re
import sys

payload = json.load(sys.stdin)
tool_name = payload.get("tool_name", "")
tool_input = payload.get("tool_input", {}) or {}
text = json.dumps(tool_input)

is_edit_tool = tool_name in ["Edit", "Write", "MultiEdit"]
has_pii_keywords = bool(re.search(r"\b(email|phone)\b", text, re.IGNORECASE))

if is_edit_tool and has_pii_keywords:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Warning: This edit contains 'email' or 'phone' keywords. Verify that PII is properly masked before committing."
        }
    }))
    sys.exit(0)

sys.exit(0)
