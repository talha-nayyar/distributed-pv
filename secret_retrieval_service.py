# secret_retrieval_service.py
# Microservice responsible for: Retrieve Secret, List Secrets
from concurrent import futures
import grpc
import os

import vault_pb2
import vault_pb2_grpc
import shared_data

# Access Control Service address (to check permissions)
ACCESS_CONTROL_SERVICE_ADDR = os.environ.get("ACCESS_CONTROL_ADDR", "")

def check_access(user_id, secret_id):
    """Check if user has access to a secret via Access Control Service"""
    if not ACCESS_CONTROL_SERVICE_ADDR:
        # Fallback: check locally
        secret = shared_data.get_secret(secret_id)
        if secret:
            if secret['user_id'] == user_id:
                return True
            access_control = shared_data.get_access_control(secret_id)
            if access_control and user_id in access_control.get('shared_with', []):
                return True
        return False

    try:
        with grpc.insecure_channel(ACCESS_CONTROL_SERVICE_ADDR) as channel:
            stub = vault_pb2_grpc.AccessControlServiceStub(channel)
            request = vault_pb2.CheckAccessRequest(user_id=user_id, secret_id=secret_id)
            response = stub.CheckAccess(request, timeout=2)
            return response.has_access
    except grpc.RpcError as e:
        print(f"[SecretRetrieval] Error checking access: {e}")
        # Fallback to local check
        secret = shared_data.get_secret(secret_id)
        return secret and secret['user_id'] == user_id

class SecretRetrievalServiceImpl(vault_pb2_grpc.SecretRetrievalServiceServicer):

    def RetrieveSecret(self, request, context):
        """Requirement 2: Retrieve Secret"""
        secret_id = request.secret_id
        user_id = request.user_id

        secret = shared_data.get_secret(secret_id)
        if not secret:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Secret not found")
            return vault_pb2.RetrieveSecretResponse(
                secret_id=secret_id,
                data="",
                success=False
            )

        # Check access permission
        if not check_access(user_id, secret_id):
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Not authorized to access this secret")
            return vault_pb2.RetrieveSecretResponse(
                secret_id=secret_id,
                data="",
                success=False
            )

        print(f"[SecretRetrieval] Retrieved secret {secret_id} for user {user_id}")

        return vault_pb2.RetrieveSecretResponse(
            secret_id=secret_id,
            data=secret['data'],
            success=True
        )

    def ListSecrets(self, request, context):
        """Requirement 4: List Secrets (metadata only)"""
        user_id = request.user_id
        user_secrets = []

        # Find all secrets owned by or shared with the user
        for secret_id, secret in shared_data.get_all_secrets().items():
            # Check if user is owner
            is_owner = secret['user_id'] == user_id

            # Check if secret is shared with user
            is_shared = False
            access_control = shared_data.get_access_control(secret_id)
            if access_control:
                is_shared = user_id in access_control.get('shared_with', [])

            if is_owner or is_shared:
                metadata = vault_pb2.SecretMetadata(
                    secret_id=secret_id,
                    secret_name=secret['secret_name'],
                    created_at=secret['created_at'],
                    updated_at=secret['updated_at'],
                    is_shared=is_shared
                )
                user_secrets.append(metadata)

        print(f"[SecretRetrieval] Listed {len(user_secrets)} secrets for user {user_id}")

        return vault_pb2.ListSecretsResponse(
            secrets=user_secrets,
            total_count=len(user_secrets)
        )

def serve():
    port = os.environ.get("PORT", "50052")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vault_pb2_grpc.add_SecretRetrievalServiceServicer_to_server(
        SecretRetrievalServiceImpl(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    print(f"[SecretRetrieval] Service started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
