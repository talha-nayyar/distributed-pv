# grpc_server.py
# Unified server that runs all microservices on a single port (for simple deployment)
# Note: For full microservices architecture, use individual service files
from concurrent import futures
import grpc
import os

import vault_pb2_grpc

# Import microservice implementations
from secret_management_service import SecretManagementServiceImpl
from secret_retrieval_service import SecretRetrievalServiceImpl
from access_control_service import AccessControlServiceImpl
from replication_service import ReplicationServiceImpl

def serve():
    """
    Run all microservices in a single server process.
    This is useful for simplified deployment or testing.

    For production microservices deployment, use:
    - secret_management_service.py
    - secret_retrieval_service.py
    - access_control_service.py
    - replication_service.py
    - api_gateway.py
    """
    port = os.environ.get("PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))

    # Register all microservices in one server
    vault_pb2_grpc.add_SecretManagementServiceServicer_to_server(
        SecretManagementServiceImpl(), server
    )
    vault_pb2_grpc.add_SecretRetrievalServiceServicer_to_server(
        SecretRetrievalServiceImpl(), server
    )
    vault_pb2_grpc.add_AccessControlServiceServicer_to_server(
        AccessControlServiceImpl(), server
    )
    vault_pb2_grpc.add_ReplicationServiceServicer_to_server(
        ReplicationServiceImpl(), server
    )

    server.add_insecure_port(f'[::]:{port}')
    print(f"=" * 60)
    print(f"Unified gRPC Server started on port {port}")
    print(f"Running all microservices in single process:")
    print(f"  - SecretManagementService")
    print(f"  - SecretRetrievalService")
    print(f"  - AccessControlService")
    print(f"  - ReplicationService")
    print(f"=" * 60)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()