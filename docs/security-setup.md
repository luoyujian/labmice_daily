# Security setup and upgrade

Set `SECRET_KEY` to a unique random value of at least 32 characters before starting the application. Missing, short, and known default values are rejected at startup. Generate a value locally with:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Keep the value private and persistent across container restarts. Changing it invalidates existing login tokens and requires users to sign in again.

For a new account database, also set `ADMIN_PASSWORD` to a unique password. Empty values and `admin123` are rejected. When any administrator already exists, initialization leaves existing accounts unchanged and does not recreate the default `admin` account. Existing weak passwords must still be changed through account management.

Docker Compose uses the existing `.env` configuration. Direct Python and Windows launcher use requires these variables in the process environment; this patch does not add automatic `.env` loading.

## Verification

After installing the backend dependencies, run from the repository root with a temporary `DATA_DIR` and a test-only `SECRET_KEY` of at least 32 characters:

```sh
python -m unittest discover -s backend/tests -v
```

This batch addresses static-file path containment and insecure authentication defaults. It does not yet address the previously identified startup cleanup and transfer-state issues.

Credential validation also rejects the shipped example placeholders and obvious repeated-character values. SECRET_KEY requires at least 32 characters and 12 distinct characters; the initial ADMIN_PASSWORD requires at least 12 characters and 6 distinct characters. Generate the signing key with Python secrets.token_urlsafe(48). Distinct-character checks are only a basic weak-value filter, not an entropy guarantee. Existing administrator passwords are not changed automatically.
