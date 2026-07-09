# Security Audit Logging
- Use Python's built-in `logging` module to maintain an audit trail of critical security events (logins, access to sensitive data, errors, etc.).
- Logs must be structured (e.g., JSON format when possible or clearly parseable text) containing timestamp, user/actor, action, and outcome.
- Never log raw passwords, full credit card numbers, or unprotected PII. Mask sensitive data before passing it to the logger.
- Define appropriate log levels: `INFO` for routine audit events, `WARNING` for suspicious activities, and `ERROR` or `CRITICAL` for security failures or crashes.
