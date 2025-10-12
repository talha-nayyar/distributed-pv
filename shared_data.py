# shared_data.py
# Shared data structures across all microservices within a node
# In a production system, this would be replaced by a shared database (Redis, PostgreSQL, etc.)

# Secrets database
# Structure: { secret_id: { user_id, secret_name, data, created_at, updated_at } }
secrets_db = {}

# Access control database
# Structure: { secret_id: { owner_id, shared_with: [user_id1, user_id2] } }
access_db = {}

def get_secret(secret_id):
    """Get a secret from the database"""
    return secrets_db.get(secret_id)

def set_secret(secret_id, secret_data):
    """Store a secret in the database"""
    secrets_db[secret_id] = secret_data

def delete_secret(secret_id):
    """Delete a secret from the database"""
    if secret_id in secrets_db:
        del secrets_db[secret_id]

def get_all_secrets():
    """Get all secrets"""
    return secrets_db

def get_access_control(secret_id):
    """Get access control info for a secret"""
    return access_db.get(secret_id)

def set_access_control(secret_id, access_data):
    """Set access control info for a secret"""
    access_db[secret_id] = access_data

def delete_access_control(secret_id):
    """Delete access control info"""
    if secret_id in access_db:
        del access_db[secret_id]

def get_all_access_controls():
    """Get all access control data"""
    return access_db
