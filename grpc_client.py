# grpc_client.py
import grpc
import uuid
from crypto_utils import CryptoUtils

# Import generated classes
import vault_pb2
import vault_pb2_grpc

# Configuration
GRPC_SERVER_ADDRESS = "localhost:50051" # Target any node in the cluster
MASTER_PASSWORD = "my-super-secret-password"

def add_new_secret_grpc(secret_value: str, secret_name: str):
    crypto = CryptoUtils(MASTER_PASSWORD)
    encrypted_data = crypto.encrypt(secret_value)
    secret_id = str(uuid.uuid4())

    with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
        stub = vault_pb2_grpc.VaultServiceStub(channel)
        request = vault_pb2.AddSecretRequest(id=secret_id, data=encrypted_data)
        try:
            response = stub.AddSecret(request)
            print(f"Successfully added secret '{secret_name}'. ID: {response.id}")
            return response.id
        except grpc.RpcError as e:
            print(f"Error adding secret: {e.details()}")
            return None

def retrieve_secret_grpc(secret_id: str):
    crypto = CryptoUtils(MASTER_PASSWORD)
    
    with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
        stub = vault_pb2_grpc.VaultServiceStub(channel)
        request = vault_pb2.RetrieveSecretRequest(id=secret_id)
        try:
            response = stub.RetrieveSecret(request)
            decrypted_secret = crypto.decrypt(response.data)
            
            if decrypted_secret:
                print(f"Retrieved secret. ID: {response.id}")
                print(f"Decrypted Value: '{decrypted_secret}'")
            else:
                print("Failed to decrypt the secret.")
        except grpc.RpcError as e:
            print(f"Error retrieving secret: {e.details()}")

if __name__ == '__main__':
    print("--- Adding a new secret (gRPC) ---")
    db_password_id = add_new_secret_grpc(
        secret_value="P@ssw0rd123!", 
        secret_name="Database Password"
    )

    if db_password_id:
        print("\n--- Retrieving the secret (gRPC) ---")
        retrieve_secret_grpc(db_password_id)