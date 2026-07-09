# SAST with Bandit
- Use Bandit to scan Python code for common security vulnerabilities (e.g. SQL injections, hardcoded credentials, insecure cryptographic algorithms).
- When a Bandit error is reported, do not ignore it. Refactor the code to eliminate the vulnerability.
- Only use `# nosec` if absolutely certain it is a false positive and properly document the reason.
- Ensure all database queries use parameterized parameters via SQLAlchemy to prevent SQL injection.
- Ensure safe usages of cryptographic modules.
