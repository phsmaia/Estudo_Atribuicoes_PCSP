# Dependency Audit with pip-audit
- Use pip-audit to check for known vulnerabilities (CVEs) in project dependencies.
- If pip-audit flags a vulnerability, immediately update the offending package in `requirements.txt` to the patched version.
- Avoid pinning dependencies to vulnerable versions unless there is a strictly documented and managed exception.
- Run `pip-audit` regularly on both `requirements.txt` and `requirements-dev.txt`.
