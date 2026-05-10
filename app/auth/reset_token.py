import secrets
import hashlib

def generate_reset_token():
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    return raw_token, token_hash

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()