# grpc_client.py
# Simple client for testing the microservices architecture via API Gateway
import grpc
from crypto_utils import CryptoUtils

import vault_pb2
import vault_pb2_grpc

# Configuration - Connect to API Gateway
GATEWAY_ADDRESS = "localhost:50050"  # API Gateway
MASTER_PASSWORD = "my-super-secret-password"
DEFAULT_USER_ID = "user_alice"

def add_new_secret_grpc(secret_value: str, secret_name: str, user_id=DEFAULT_USER_ID):
    """Add a new secret via the microservices API Gateway"""
    crypto = CryptoUtils(MASTER_PASSWORD)
    encrypted_data = crypto.encrypt(secret_value)

    with grpc.insecure_channel(GATEWAY_ADDRESS) as channel:
        stub = vault_pb2_grpc.SecretManagementServiceStub(channel)
        request = vault_pb2.AddSecretRequest(
            user_id=user_id,
            secret_name=secret_name,
            data=encrypted_data
        )
        try:
            response = stub.AddSecret(request)
            if response.success:
                print(f"✓ Successfully added secret '{secret_name}'")
                print(f"  Secret ID: {response.secret_id}")
                return response.secret_id
            else:
                print(f"✗ Failed to add secret: {response.message}")
                return None
        except grpc.RpcError as e:
            print(f"✗ Error adding secret: {e.details()}")
            return None

def retrieve_secret_grpc(secret_id: str, user_id=DEFAULT_USER_ID):
    """Retrieve a secret via the microservices API Gateway"""
    crypto = CryptoUtils(MASTER_PASSWORD)

    with grpc.insecure_channel(GATEWAY_ADDRESS) as channel:
        stub = vault_pb2_grpc.SecretRetrievalServiceStub(channel)
        request = vault_pb2.RetrieveSecretRequest(
            user_id=user_id,
            secret_id=secret_id
        )
        try:
            response = stub.RetrieveSecret(request)
            if response.success:
                decrypted_secret = crypto.decrypt(response.data)
                if decrypted_secret:
                    print(f"✓ Retrieved secret ID: {secret_id}")
                    print(f"  Decrypted Value: '{decrypted_secret}'")
                    return decrypted_secret
                else:
                    print("✗ Failed to decrypt the secret")
                    return None
            else:
                print(f"✗ Failed to retrieve secret")
                return None
        except grpc.RpcError as e:
            print(f"✗ Error retrieving secret: {e.details()}")
            return None

def list_secrets_grpc(user_id=DEFAULT_USER_ID):
    """List all secrets for a user"""
    with grpc.insecure_channel(GATEWAY_ADDRESS) as channel:
        stub = vault_pb2_grpc.SecretRetrievalServiceStub(channel)
        request = vault_pb2.ListSecretsRequest(user_id=user_id)
        try:
            response = stub.ListSecrets(request)
            print(f"✓ Found {response.total_count} secret(s):")
            for secret_meta in response.secrets:
                shared = " [SHARED]" if secret_meta.is_shared else ""
                print(f"  - {secret_meta.secret_name}{shared}")
                print(f"    ID: {secret_meta.secret_id}")
            return response.secrets
        except grpc.RpcError as e:
            print(f"✗ Error listing secrets: {e.details()}")
            return []

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Distributed Password Vault - Microservices gRPC")
    print("Connecting to API Gateway at", GATEWAY_ADDRESS)
    print("=" * 60)

    print("\n--- Test 1: Add Secret ---")
    db_password_id = add_new_secret_grpc(
        secret_value="P@ssw0rd123!",
        secret_name="Database Password"
    )

    print("\n--- Test 2: Add Another Secret ---")
    api_key_id = add_new_secret_grpc(
        secret_value="sk-1234567890abcdef",
        secret_name="API Key"
    )

    if db_password_id:
        print("\n--- Test 3: Retrieve Secret ---")
        retrieve_secret_grpc(db_password_id)

    print("\n--- Test 4: List All Secrets ---")
    list_secrets_grpc()

    print("\n" + "=" * 60)
    print("Basic tests completed!")
    print("For comprehensive testing, use: python3 microservices_client.py")
    print("=" * 60)