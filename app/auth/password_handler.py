from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Validation constant
MIN_PASSWORD_LENGTH = 8


def validate_password_strength(password: str) -> None:
    # Raise an error if password is weak
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password is too short!")

    # Optionally check for digits, uppercase, lowercase, special characters
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[!@#$%^&*()[]?""<>"):
        raise ValueError("Password must contain at least one special character")


def hash_password(password: str) -> str:
    # Validate a password then hash it
    validate_password_strength(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # compare the stored password with the user's password
    return pwd_context.verify(plain_password, hashed_password)