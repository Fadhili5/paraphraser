from passlib.context import CryptContext
import re

# Password hashing configuration
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

DUMMY_PASSWORD_HASH = pwd_context.hash("dummy-password-for-timing")

# Validation constants
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128  # protects against DoS and absurd inputs


def validate_password_strength(password: str) -> None:
    #Validates password strength.

    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password is too short")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password is too long")

    # Optional light composition checks
    # These discourage trivial passwords without enforcing brittle rules
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("Password must contain at least one letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")


def hash_password(password: str) -> str:
    # Validates and hashes a password for storage.
    validate_password_strength(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verifies a plaintext password against a stored hash.
    return pwd_context.verify(plain_password, hashed_password)
