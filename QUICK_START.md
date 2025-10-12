# Quick Start

## TL;DR

### Test HTTP Architecture
```bash
# 1. Start HTTP nodes
docker-compose up http-node1 http-node2 http-node3 http-node4 http-node5

# 2. Test (in another terminal)
python3 http_client.py
```

### Test gRPC Microservices
```bash
# 1. Start all microservices
docker-compose up

# 2. Test (in another terminal)
python3 microservices_client.py
```

---

## Key Files

| File | Purpose |
|------|---------|
| `http_server.py` | Monolithic server (Architecture 1) |
| `http_client.py` | HTTP test client |
| `api_gateway.py` | gRPC gateway (Architecture 2) |
| `secret_management_service.py` | Add/Update/Delete microservice |
| `secret_retrieval_service.py` | Retrieve/List microservice |
| `access_control_service.py` | Share microservice |
| `replication_service.py` | Cross-node sync |
| `microservices_client.py` | gRPC test client (comprehensive) |
| `grpc_client.py` | gRPC test client (simple) |
| `docker-compose.yml` | Container orchestration |
| `vault.proto` | gRPC service definitions |

---

## Endpoints

### HTTP (Port 5001)
```
POST   /secrets              - Add secret
GET    /secrets/<id>         - Retrieve secret
PUT    /secrets/<id>         - Update secret
DELETE /secrets/<id>         - Delete secret
GET    /secrets              - List secrets
POST   /secrets/<id>/share   - Share secret
```

### gRPC (Port 50050)
```
SecretManagementService:
  - AddSecret()
  - UpdateSecret()
  - DeleteSecret()

SecretRetrievalService:
  - RetrieveSecret()
  - ListSecrets()

AccessControlService:
  - ShareSecret()
  - CheckAccess()
```

---

## Quick Tests

### HTTP Test
```bash
# Add a secret
curl -X POST http://localhost:5001/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "secret_id": "test-123",
    "user_id": "alice",
    "secret_name": "Test Secret",
    "data": "encrypted-data-here"
  }'

# List secrets
curl "http://localhost:5001/secrets?user_id=alice"
```

### gRPC Test
```python
import grpc
import vault_pb2
import vault_pb2_grpc

channel = grpc.insecure_channel('localhost:50050')
stub = vault_pb2_grpc.SecretManagementServiceStub(channel)

response = stub.AddSecret(vault_pb2.AddSecretRequest(
    user_id="alice",
    secret_name="Test",
    data="encrypted"
))
print(response.secret_id)
```

---

## Common Commands

### Docker
```bash
# Start everything
docker-compose up

# Start specific architecture
docker-compose up http-node1 http-node2 http-node3 http-node4 http-node5
docker-compose up grpc-node1-gateway grpc-node2-gateway

# Stop everything
docker-compose down

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up

# View logs
docker-compose logs -f
docker-compose logs -f http-node1
docker-compose logs -f grpc-node1-gateway
```

### Development
```bash
# Regenerate gRPC code
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. vault.proto

# Run tests
python3 http_client.py
python3 microservices_client.py

# Check syntax
python3 -m py_compile http_server.py
python3 -m py_compile api_gateway.py
```

---

## Architecture Overview

### HTTP (Monolithic)
```
5 Nodes × 1 Service = 5 Containers
Each node runs identical http_server.py
Communication: HTTP/REST + JSON
```

### gRPC (Microservices)
```
5 Nodes × 5 Services = 25 Containers
Each node runs:
  - API Gateway
  - Secret Management
  - Secret Retrieval
  - Access Control
  - Replication
Communication: gRPC + Protocol Buffers
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | `lsof -ti:5001 \| xargs kill -9` |
| Container won't start | Check logs: `docker-compose logs <service>` |
| Connection refused | Verify service is running: `docker-compose ps` |
| gRPC error | Check gateway: `docker-compose logs grpc-node1-gateway` |
| Import error | Install deps: `pip install Flask requests pycryptodome grpcio grpcio-tools` |

---

## Full Documentation

For complete documentation, see [README.md](README.md)

**Need help? Check logs first:** `docker-compose logs -f`
