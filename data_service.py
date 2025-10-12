# data_service.py
# Centralized data service for microservices to share data
from concurrent import futures
import grpc
import os
from datetime import datetime

import vault_pb2
import vault_pb2_grpc

# Centralized data stores
secrets_db = {}
access_db = {}

class DataServiceImpl(vault_pb2_grpc.ReplicationServiceServicer):
    """
    Centralized data service that all microservices connect to.
    Uses the ReplicationService interface as it has all CRUD operations.
    """

    def ReplicateSecret(self, request, context):
        """Store a new secret"""
        secret_id = request.secret_id
        secrets_db[secret_id] = {
            'user_id': request.user_id,
            'secret_name': request.secret_name,
            'data': request.data,
            'created_at': request.created_at,
            'updated_at': request.created_at
        }
        print(f"[DataService] Stored secret {secret_id}")
        return vault_pb2.ReplicateSecretResponse(success=True)

    def ReplicateUpdate(self, request, context):
        """Update an existing secret"""
        secret_id = request.secret_id
        if secret_id in secrets_db:
            secrets_db[secret_id]['data'] = request.data
            secrets_db[secret_id]['updated_at'] = request.updated_at
            print(f"[DataService] Updated secret {secret_id}")
            return vault_pb2.ReplicateUpdateResponse(success=True)
        return vault_pb2.ReplicateUpdateResponse(success=False)

    def ReplicateDeletion(self, request, context):
        """Delete a secret"""
        secret_id = request.secret_id
        if secret_id in secrets_db:
            del secrets_db[secret_id]
        if secret_id in access_db:
            del access_db[secret_id]
        print(f"[DataService] Deleted secret {secret_id}")
        return vault_pb2.ReplicateDeletionResponse(success=True)

    def ReplicateShare(self, request, context):
        """Store share information"""
        secret_id = request.secret_id
        if secret_id not in access_db:
            access_db[secret_id] = {
                'owner_id': request.owner_id,
                'shared_with': []
            }
        if request.target_user_id not in access_db[secret_id]['shared_with']:
            access_db[secret_id]['shared_with'].append(request.target_user_id)
        print(f"[DataService] Stored share for {secret_id}")
        return vault_pb2.ReplicateShareResponse(success=True)

def serve():
    port = os.environ.get("DATA_SERVICE_PORT", "50055")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vault_pb2_grpc.add_ReplicationServiceServicer_to_server(DataServiceImpl(), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"[DataService] Centralized Data Service started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
