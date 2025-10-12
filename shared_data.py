# shared_data.py
import redis
import json
import os

# Get Redis host from environment variable, default to localhost for local testing
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")

# Connect to the Redis container. 'redis' is the hostname inside Docker's network.
# decode_responses=True makes it return strings instead of bytes.
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
print(f"[SharedData] Connecting to Redis at {REDIS_HOST}")


# --- Secrets Database Functions ---

def get_secret(secret_id):
    """Get a secret from Redis"""
    secret_json = r.get(f"secret:{secret_id}")
    return json.loads(secret_json) if secret_json else None

def set_secret(secret_id, secret_data):
    """Store a secret in Redis. Convert dict to JSON string."""
    r.set(f"secret:{secret_id}", json.dumps(secret_data))

def delete_secret(secret_id):
    """Delete a secret from Redis"""
    r.delete(f"secret:{secret_id}")

def get_all_secrets():
    """Get all secrets from Redis (less efficient, for listing)"""
    all_secrets = {}
    for key in r.scan_iter("secret:*"):
        secret_id = key.split(":", 1)[1]
        all_secrets[secret_id] = get_secret(secret_id)
    return all_secrets


# --- Access Control Database Functions ---

def get_access_control(secret_id):
    """Get access control info from Redis"""
    access_json = r.get(f"access:{secret_id}")
    return json.loads(access_json) if access_json else None

def set_access_control(secret_id, access_data):
    """Set access control info in Redis"""
    r.set(f"access:{secret_id}", json.dumps(access_data))

def delete_access_control(secret_id):
    """Delete access control info from Redis"""
    r.delete(f"access:{secret_id}")

def get_all_access_controls():
    """Get all access control data from Redis"""
    all_access = {}
    for key in r.scan_iter("access:*"):
        secret_id = key.split(":", 1)[1]
        all_access[secret_id] = get_access_control(secret_id)
    return all_access