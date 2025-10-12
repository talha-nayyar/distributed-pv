# access_control_service.py
# Microservice responsible for: Share Secret, Check Access
from concurrent import futures
import grpc
import os
import threading

import vault_pb2
import vault_pb2_grpc
import shared_data

# Replication service addresses
REPLICATION_SERVICE_ADDRS = os.environ.get("REPLICATION_NODES", "").split(',')

def replicate_share(secret_id, owner_id, target_user_id):
    """Replicate share operation to other nodes"""
    for addr in REPLICATION_SERVICE_ADDRS:
        if not addr:
            continue
        try:
            with grpc.insecure_channel(addr) as channel:
                stub = vault_pb2_grpc.ReplicationServiceStub(channel)
                request = vault_pb2.ReplicateShareRequest(
                    secret_id=secret_id,
                    owner_id=owner_id,
                    target_user_id=target_user_id
                )
                stub.ReplicateShare(request, timeout=2)
                print(f"[AccessControl] Replicated share {secret_id} to {addr}")
        except grpc.RpcError as e:
            print(f"[AccessControl] Failed to replicate share to {addr}: {e}")

class AccessControlServiceImpl(vault_pb2_grpc.AccessControlServiceServicer):

    def ShareSecret(self, request, context):
        """Requirement 5: Share Secret"""
        secret_id = request.secret_id
        owner_id = request.owner_id
        target_user_id = request.target_user_id

        # Verify secret exists
        secret = shared_data.get_secret(secret_id)
        if not secret:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Secret not found")
            return vault_pb2.ShareSecretResponse(
                message="Secret not found",
                success=False
            )

        # Verify ownership
        if secret['user_id'] != owner_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Only owner can share secrets")
            return vault_pb2.ShareSecretResponse(
                message="Only owner can share secrets",
                success=False
            )

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

        print(f"[AccessControl] Shared secret {secret_id} with user {target_user_id}")

        # Replicate share operation
        threading.Thread(
            target=replicate_share,
            args=(secret_id, owner_id, target_user_id)
        ).start()

        return vault_pb2.ShareSecretResponse(
            message=f"Secret shared successfully with user {target_user_id}",
            success=True
        )

    def CheckAccess(self, request, context):
        """Check if a user has access to a secret"""
        user_id = request.user_id
        secret_id = request.secret_id

        # Secret doesn't exist
        secret = shared_data.get_secret(secret_id)
        if not secret:
            return vault_pb2.CheckAccessResponse(
                has_access=False,
                owner_id=""
            )

        owner_id = secret['user_id']

        # Check if user is owner
        if owner_id == user_id:
            return vault_pb2.CheckAccessResponse(
                has_access=True,
                owner_id=owner_id
            )

        # Check if secret is shared with user
        access_control = shared_data.get_access_control(secret_id)
        if access_control:
            if user_id in access_control.get('shared_with', []):
                return vault_pb2.CheckAccessResponse(
                    has_access=True,
                    owner_id=owner_id
                )

        # No access
        return vault_pb2.CheckAccessResponse(
            has_access=False,
            owner_id=owner_id
        )

def serve():
    port = os.environ.get("PORT", "50053")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vault_pb2_grpc.add_AccessControlServiceServicer_to_server(
        AccessControlServiceImpl(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    print(f"[AccessControl] Service started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
