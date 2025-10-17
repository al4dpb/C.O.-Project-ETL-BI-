# Security Guidelines

## Environment Variables

**CRITICAL:** This project uses environment variables for all sensitive credentials. Never commit secrets to Git.

### Required Environment Variables

Create `.env.compose` in the project root with:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_KEY>
S3_BUCKET=co-data-dev

# MotherDuck
MOTHERDUCK_TOKEN=<YOUR_MOTHERDUCK_TOKEN>
```

### Pre-commit Hooks Setup

Install pre-commit hooks to prevent accidental secret commits:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Gitignored Files

The following files are gitignored and **must never be committed**:

- `.env.compose`
- `.env`
- `.env.*` (except `.env.local.template`)
- `*.csv` (AWS credential exports)
- `.aws/` directory

### Secret Detection

We use `detect-secrets` to scan for accidental credential leaks. If you encounter a false positive:

```bash
# Update baseline
detect-secrets scan --baseline .secrets.baseline
```

### Runtime Environment Check

To verify your environment variables are set correctly (with redacted secrets):

```bash
./scripts/print_runtime_env.sh
```

## Code Review Checklist

Before committing:

- [ ] No hardcoded AWS keys
- [ ] No hardcoded MotherDuck tokens
- [ ] All credentials read from `os.getenv()` or `process.env`
- [ ] `.env.compose` is gitignored
- [ ] Pre-commit hooks pass
- [ ] `scripts/print_runtime_env.sh` shows redacted values only
