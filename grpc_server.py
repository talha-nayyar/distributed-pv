# grpc_server.py
from concurrent import futures
import grpc
import os
import threading

# Import generated classes
import vault_pb2
import vault_pb2_grpc

# In-memory data store for this node
vault_db = {}

# List of other nodes, e.g., "node2:50051,node3:50051"
OTHER_NODES_ADDR = os.environ.get("OTHER_NODES_ADDR", "").split(',') if os.environ.get("OTHER_NODES_ADDR") else []

# --- Helper for Replication ---
def replicate_via_grpc(secret_id, data):
    """Sends the new secret to other nodes via gRPC."""
    for node_addr in OTHER_NODES_ADDR:
        if not node_addr: continue
        try:
            with grpc.insecure_channel(node_addr) as channel:
                stub = vault_pb2_grpc.VaultServiceStub(channel)
                request = vault_pb2.ReplicateSecretRequest(id=secret_id, data=data)
                stub.ReplicateSecret(request, timeout=2)
                print(f"Replicated {secret_id} to {node_addr}")
        except grpc.RpcError as e:
            print(f"Failed to replicate to {node_addr}: {e}")

# --- Service Implementation ---
class VaultServiceImpl(vault_pb2_grpc.VaultServiceServicer):
    def AddSecret(self, request, context):
        secret_id = request.id
        secret_data = request.data
        vault_db[secret_id] = secret_data
        print(f"Added secret {secret_id} locally.")

        # Replicate in the background
        threading.Thread(target=replicate_via_grpc, args=(secret_id, secret_data)).start()

        return vault_pb2.AddSecretResponse(id=secret_id, message="Secret added successfully")

    def RetrieveSecret(self, request, context):
        secret_id = request.id
        secret_data = vault_db.get(secret_id)
        if not secret_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Secret not found")
            return vault_pb2.RetrieveSecretResponse()
        
        return vault_pb2.RetrieveSecretResponse(id=secret_id, data=secret_data)
    
    def ReplicateSecret(self, request, context):
        vault_db[request.id] = request.data
        print(f"Received replicated secret {request.id}.")
        return vault_pb2.ReplicateSecretResponse(success=True)

def serve():
    port = os.environ.get("PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vault_pb2_grpc.add_VaultServiceServicer_to_server(VaultServiceImpl(), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"gRPC server started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()