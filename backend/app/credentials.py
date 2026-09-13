"""Dependency-free validation for deployment credentials."""


def validate_credential(value: str, name: str) -> str:
    value = value.strip()
    minimum, diversity = (32, 12) if name == "SECRET_KEY" else (12, 6)
    weak = {"mouse-secret-key-2026", "changeme", "secret", "admin123"}
    placeholders = ("replace-with", "replace_with", "change-me", "change_me", "your-secret", "your_secret")
    if (not value or value.lower() in weak
            or any(marker in value.lower() for marker in placeholders)
            or len(value) < minimum or len(set(value)) < diversity):
        raise RuntimeError(
            f"{name} must be a unique non-placeholder value with at least "
            f"{minimum} characters and {diversity} distinct characters"
        )
    return value
