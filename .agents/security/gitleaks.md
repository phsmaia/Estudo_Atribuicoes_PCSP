# Secret Scanning with Gitleaks
- Use Gitleaks (via pre-commit) to detect accidentally committed API keys, passwords, and tokens.
- Never commit hardcoded secrets to the repository.
- If Gitleaks blocks a commit, remove the secret from the code and load it from environment variables using `python-dotenv`.
- In case a real secret is committed, consider it compromised and rotate it immediately.
