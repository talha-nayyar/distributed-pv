# api_gateway.py
# API Gateway that routes client requests to appropriate microservices
from concurrent import futures
import grpc
import os

import vault_pb2
import vault_pb2_grpc

# Microservice addresses
SECRET_MANAGEMENT_ADDR = os.environ.get("SECRET_MGMT_ADDR", "localhost:50051")
SECRET_RETRIEVAL_ADDR = os.environ.get("SECRET_RETRIEVAL_ADDR", "localhost:50052")
ACCESS_CONTROL_ADDR = os.environ.get("ACCESS_CONTROL_ADDR", "localhost:50053")

class GatewaySecretManagementService(vault_pb2_grpc.SecretManagementServiceServicer):
    """Gateway for Secret Management operations"""

    def AddSecret(self, request, context):
        """Forward to Secret Management Service"""
        try:
            with grpc.insecure_channel(SECRET_MANAGEMENT_ADDR) as channel:
                stub = vault_pb2_grpc.SecretManagementServiceStub(channel)
                response = stub.AddSecret(request, timeout=5)
                print(f"[Gateway] AddSecret routed to SecretManagement")
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.AddSecretResponse(
                secret_id="",
                message=f"Service unavailable: {e.details()}",
                success=False
            )

    def UpdateSecret(self, request, context):
        """Forward to Secret Management Service"""
        try:
            with grpc.insecure_channel(SECRET_MANAGEMENT_ADDR) as channel:
                stub = vault_pb2_grpc.SecretManagementServiceStub(channel)
                response = stub.UpdateSecret(request, timeout=5)
                print(f"[Gateway] UpdateSecret routed to SecretManagement")
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.UpdateSecretResponse(
                secret_id=request.secret_id,
                message=f"Service unavailable: {e.details()}",
                success=False
            )

    def DeleteSecret(self, request, context):
        """Forward to Secret Management Service"""
        try:
            with grpc.insecure_channel(SECRET_MANAGEMENT_ADDR) as channel:
                stub = vault_pb2_grpc.SecretManagementServiceStub(channel)
                response = stub.DeleteSecret(request, timeout=5)
                print(f"[Gateway] DeleteSecret routed to SecretManagement")
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.DeleteSecretResponse(
                secret_id=request.secret_id,
                message=f"Service unavailable: {e.details()}",
                success=False
            )

class GatewaySecretRetrievalService(vault_pb2_grpc.SecretRetrievalServiceServicer):
    """Gateway for Secret Retrieval operations"""

    def RetrieveSecret(self, request, context):
        """Forward to Secret Retrieval Service"""
        try:
            with grpc.insecure_channel(SECRET_RETRIEVAL_ADDR) as channel:
                stub = vault_pb2_grpc.SecretRetrievalServiceStub(channel)
                response = stub.RetrieveSecret(request, timeout=5)
                print(f"[Gateway] RetrieveSecret routed to SecretRetrieval")
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.RetrieveSecretResponse(
                secret_id=request.secret_id,
                data="",
                success=False
            )

    def ListSecrets(self, request, context):
        """Forward to Secret Retrieval Service"""
        try:
            with grpc.insecure_channel(SECRET_RETRIEVAL_ADDR) as channel:
                stub = vault_pb2_grpc.SecretRetrievalServiceStub(channel)
                response = stub.ListSecrets(request, timeout=5)
                print(f"[Gateway] ListSecrets routed to SecretRetrieval")
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.ListSecretsResponse(secrets=[], total_count=0)

class GatewayAccessControlService(vault_pb2_grpc.AccessControlServiceServicer):
    """Gateway for Access Control operations"""

    def ShareSecret(self, request, context):
        """Forward to Access Control Service"""
        try:
            with grpc.insecure_channel(ACCESS_CONTROL_ADDR) as channel:
                stub = vault_pb2_grpc.AccessControlServiceStub(channel)
                response = stub.ShareSecret(request, timeout=5)
                print(f"[Gateway] ShareSecret routed to AccessControl")
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.ShareSecretResponse(
                message=f"Service unavailable: {e.details()}",
                success=False
            )

    def CheckAccess(self, request, context):
        """Forward to Access Control Service"""
        try:
            with grpc.insecure_channel(ACCESS_CONTROL_ADDR) as channel:
                stub = vault_pb2_grpc.AccessControlServiceStub(channel)
                response = stub.CheckAccess(request, timeout=5)
                return response
        except grpc.RpcError as e:
            context.set_code(e.code())
            context.set_details(e.details())
            return vault_pb2.CheckAccessResponse(has_access=False, owner_id="")

def serve():
    port = os.environ.get("PORT", "50050")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))

    # Register all gateway services
    vault_pb2_grpc.add_SecretManagementServiceServicer_to_server(
        GatewaySecretManagementService(), server
    )
    vault_pb2_grpc.add_SecretRetrievalServiceServicer_to_server(
        GatewaySecretRetrievalService(), server
    )
    vault_pb2_grpc.add_AccessControlServiceServicer_to_server(
        GatewayAccessControlService(), server
    )

    server.add_insecure_port(f'[::]:{port}')
    print(f"[Gateway] API Gateway started on port {port}")
    print(f"[Gateway] Routing to:")
    print(f"  - Secret Management: {SECRET_MANAGEMENT_ADDR}")
    print(f"  - Secret Retrieval: {SECRET_RETRIEVAL_ADDR}")
    print(f"  - Access Control: {ACCESS_CONTROL_ADDR}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
