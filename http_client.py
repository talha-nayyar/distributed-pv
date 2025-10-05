# http_client.py
import requests
import uuid
from crypto_utils import CryptoUtils # Assumes crypto_utils.py is in the same directory

# Configuration
BASE_URL = "http://localhost:5001" # Target any node in the cluster
MASTER_PASSWORD = "my-super-secret-password"

def add_new_secret(secret_value: str, secret_name: str):
    """Encrypts and adds a new secret to the vault."""
    crypto = CryptoUtils(MASTER_PASSWORD)
    
    # 1. Encrypt the secret client-side
    encrypted_data = crypto.encrypt(secret_value)
    
    # 2. Prepare payload
    secret_id = str(uuid.uuid4())
    payload = {"id": secret_id, "data": encrypted_data}
    
    # 3. Send to any node
    try:
        response = requests.post(f"{BASE_URL}/secrets", json=payload)
        response.raise_for_status()
        print(f"Successfully added secret '{secret_name}'. ID: {secret_id}")
        return secret_id
    except requests.exceptions.RequestException as e:
        print(f"Error adding secret: {e}")
        return None

def retrieve_and_decrypt_secret(secret_id: str):
    """Retrieves and decrypts a secret from the vault."""
    crypto = CryptoUtils(MASTER_PASSWORD)
    
    # 1. Fetch encrypted data from any node
    try:
        response = requests.get(f"{BASE_URL}/secrets/{secret_id}")
        response.raise_for_status()
        encrypted_data = response.json().get('data')
        
        # 2. Decrypt client-side
        decrypted_secret = crypto.decrypt(encrypted_data)
        
        if decrypted_secret:
            print(f"Retrieved secret. ID: {secret_id}")
            print(f"Decrypted Value: '{decrypted_secret}'")
        else:
            print("Failed to decrypt the secret. Wrong password or corrupted data.")

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving secret: {e}")

if __name__ == '__main__':
    print("--- Adding a new secret ---")
    api_key_id = add_new_secret(
        secret_value="ghp_12345abcdefg...", 
        secret_name="GitHub API Key"
    )

    if api_key_id:
        print("\n--- Retrieving the secret ---")
        retrieve_and_decrypt_secret(api_key_id)