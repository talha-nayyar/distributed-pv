# http_client.py
# Client for testing HTTP/REST monolithic architecture (all 5 requirements)
import requests
import uuid
from crypto_utils import CryptoUtils

# Configuration
BASE_URL = "http://localhost:5001"  # Target any node in the cluster
MASTER_PASSWORD = "my-super-secret-password"
DEFAULT_USER_ID = "user_alice"

def add_new_secret(secret_value: str, secret_name: str, user_id=DEFAULT_USER_ID):
    """Requirement 1: Add a new secret to the vault."""
    crypto = CryptoUtils(MASTER_PASSWORD)
    encrypted_data = crypto.encrypt(secret_value)
    secret_id = str(uuid.uuid4())

    payload = {
        "secret_id": secret_id,
        "user_id": user_id,
        "secret_name": secret_name,
        "data": encrypted_data
    }

    try:
        response = requests.post(f"{BASE_URL}/secrets", json=payload)
        response.raise_for_status()
        print(f"✓ Successfully added secret '{secret_name}'. ID: {secret_id}")
        return secret_id
    except requests.exceptions.RequestException as e:
        print(f"✗ Error adding secret: {e}")
        return None

def retrieve_secret(secret_id: str, user_id=DEFAULT_USER_ID):
    """Requirement 2: Retrieve and decrypt a secret."""
    crypto = CryptoUtils(MASTER_PASSWORD)

    try:
        response = requests.get(f"{BASE_URL}/secrets/{secret_id}", params={"user_id": user_id})
        response.raise_for_status()
        encrypted_data = response.json().get('data')

        decrypted_secret = crypto.decrypt(encrypted_data)
        if decrypted_secret:
            print(f"✓ Retrieved secret ID: {secret_id}")
            print(f"  Decrypted Value: '{decrypted_secret}'")
            return decrypted_secret
        else:
            print("✗ Failed to decrypt the secret")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Error retrieving secret: {e}")
        return None

def update_secret(secret_id: str, new_value: str, user_id=DEFAULT_USER_ID):
    """Requirement 3: Update an existing secret."""
    crypto = CryptoUtils(MASTER_PASSWORD)
    encrypted_data = crypto.encrypt(new_value)

    payload = {
        "user_id": user_id,
        "data": encrypted_data
    }

    try:
        response = requests.put(f"{BASE_URL}/secrets/{secret_id}", json=payload)
        response.raise_for_status()
        print(f"✓ Successfully updated secret {secret_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Error updating secret: {e}")
        return False

def delete_secret(secret_id: str, user_id=DEFAULT_USER_ID):
    """Requirement 3: Delete a secret."""
    try:
        response = requests.delete(f"{BASE_URL}/secrets/{secret_id}", params={"user_id": user_id})
        response.raise_for_status()
        print(f"✓ Successfully deleted secret {secret_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Error deleting secret: {e}")
        return False

def list_secrets(user_id=DEFAULT_USER_ID):
    """Requirement 4: List all secrets (metadata only)."""
    try:
        response = requests.get(f"{BASE_URL}/secrets", params={"user_id": user_id})
        response.raise_for_status()
        data = response.json()
        secrets = data.get('secrets', [])

        print(f"✓ Found {data.get('total_count', 0)} secret(s):")
        for secret in secrets:
            shared = " [SHARED]" if secret.get('is_shared') else ""
            print(f"  - {secret['secret_name']}{shared}")
            print(f"    ID: {secret['secret_id']}")
        return secrets
    except requests.exceptions.RequestException as e:
        print(f"✗ Error listing secrets: {e}")
        return []

def share_secret(secret_id: str, target_user_id: str, owner_id=DEFAULT_USER_ID):
    """Requirement 5: Share a secret with another user."""
    payload = {
        "owner_id": owner_id,
        "target_user_id": target_user_id
    }

    try:
        response = requests.post(f"{BASE_URL}/secrets/{secret_id}/share", json=payload)
        response.raise_for_status()
        print(f"✓ Successfully shared secret with {target_user_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Error sharing secret: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Distributed Password Vault - HTTP/REST Architecture")
    print("Connecting to", BASE_URL)
    print("=" * 60)

    print("\n--- Requirement 1: Add Secret ---")
    db_password_id = add_new_secret(
        secret_value="P@ssw0rd123!",
        secret_name="Database Password"
    )

    api_key_id = add_new_secret(
        secret_value="sk-1234567890abcdef",
        secret_name="API Key"
    )

    if db_password_id:
        print("\n--- Requirement 2: Retrieve Secret ---")
        retrieve_secret(db_password_id)

    print("\n--- Requirement 4: List Secrets ---")
    list_secrets()

    if db_password_id:
        print("\n--- Requirement 3: Update Secret ---")
        update_secret(db_password_id, "NewP@ssw0rd456!")

    if db_password_id:
        print("\n--- Requirement 2: Retrieve Updated Secret ---")
        retrieve_secret(db_password_id)

    if api_key_id:
        print("\n--- Requirement 5: Share Secret ---")
        share_secret(api_key_id, "user_bob")

    # Test Bob accessing shared secret
    print("\n--- Bob accesses shared secret ---")
    retrieve_secret(api_key_id, user_id="user_bob")

    if db_password_id:
        print("\n--- Requirement 3: Delete Secret ---")
        delete_secret(db_password_id)

    print("\n--- List secrets after deletion ---")
    list_secrets()

    print("\n" + "=" * 60)
    print("All HTTP/REST tests completed!")
    print("=" * 60)