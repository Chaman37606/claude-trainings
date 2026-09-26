---
name: PII Guard
description: Use when reviewing claims schema, processing logic, or logging. Prevents unintended exposure of personally identifiable information.
paths: "src/**"
---

# PII Guard

Review claims logic for:
- No raw emails in logs or output
- No phone numbers in logs or output
- No policy numbers in debug output
- No customer names in error messages
- No sensitive fields in traces
- Proper masking of PII in audit logs

Return PII risks and required masking changes.
