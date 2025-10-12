# replication_service.py
# Microservice responsible for: Internal replication across nodes
from concurrent import futures
import grpc
import os

import vault_pb2
import vault_pb2_grpc
import shared_data

class ReplicationServiceImpl(vault_pb2_grpc.ReplicationServiceServicer):
    """
    Internal service that receives replication requests from other microservices
    and maintains data consistency across distributed nodes.
    """

    def ReplicateSecret(self, request, context):
        """Receive and store replicated secret from another node"""
        secret_id = request.secret_id

        shared_data.set_secret(secret_id, {
            'user_id': request.user_id,
            'secret_name': request.secret_name,
            'data': request.data,
            'created_at': request.created_at,
            'updated_at': request.created_at
        })

        print(f"[Replication] Replicated secret {secret_id} for user {request.user_id}")

        return vault_pb2.ReplicateSecretResponse(success=True)

    def ReplicateUpdate(self, request, context):
        """Receive and apply secret update from another node"""
        secret_id = request.secret_id

        secret = shared_data.get_secret(secret_id)
        if not secret:
            print(f"[Replication] Warning: Cannot update non-existent secret {secret_id}")
            return vault_pb2.ReplicateUpdateResponse(success=False)

        secret['data'] = request.data
        secret['updated_at'] = request.updated_at
        shared_data.set_secret(secret_id, secret)

        print(f"[Replication] Replicated update for secret {secret_id}")

        return vault_pb2.ReplicateUpdateResponse(success=True)

    def ReplicateDeletion(self, request, context):
        """Receive and apply secret deletion from another node"""
        secret_id = request.secret_id

        shared_data.delete_secret(secret_id)
        shared_data.delete_access_control(secret_id)
        print(f"[Replication] Replicated deletion of secret {secret_id}")

        return vault_pb2.ReplicateDeletionResponse(success=True)

    def ReplicateShare(self, request, context):
        """Receive and apply share operation from another node"""
        secret_id = request.secret_id
        owner_id = request.owner_id
        target_user_id = request.target_user_id

        # Initialize access control entry if doesn't exist
        access_control = shared_data.get_access_control(secret_id)
        if not access_control:
            access_control = {
                'owner_id': owner_id,
                'shared_with': []
            }

        # Add target user to shared list
        if target_user_id not in access_control['shared_with']:
            access_control['shared_with'].append(target_user_id)

        shared_data.set_access_control(secret_id, access_control)

        print(f"[Replication] Replicated share of secret {secret_id} with user {target_user_id}")

        return vault_pb2.ReplicateShareResponse(success=True)

def serve():
    port = os.environ.get("PORT", "50054")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vault_pb2_grpc.add_ReplicationServiceServicer_to_server(
        ReplicationServiceImpl(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    print(f"[Replication] Service started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
