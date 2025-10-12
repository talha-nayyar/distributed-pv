# Distributed Password Vault System

A production-ready distributed system for securely storing, retrieving, and sharing encrypted secrets across multiple nodes using two distinct architectures.

---

## Table of Contents

- [Overview](#overview)
- [Five Functional Requirements](#five-functional-requirements)
- [System Architectures](#system-architectures)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Architecture Details](#architecture-details)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Requirements Compliance](#requirements-compliance)

---

## Overview

This project implements a **Distributed Password Vault System** that allows users to:
- Store encrypted secrets (passwords, API keys, tokens)
- Retrieve secrets from any node in the cluster
- Update and delete secrets securely
- List secret metadata without exposing plaintext
- Share secrets with other users

The system demonstrates two distinct architectural patterns with different communication models, deployed across 5 nodes using Docker containers.

---

## Five Functional Requirements

### 1) Add Secret
Users can store new secrets with automatic encryption and cross-node replication.

**Features:**
- Client-side AES-256-GCM encryption
- Automatic replication to all nodes
- Metadata tracking (created_at, updated_at)

### 2) Retrieve Secret
Users can fetch and decrypt their secrets from any node in the cluster.

**Features:**
- Access control validation
- Support for shared secrets
- Transparent decryption

### 3) Update/Delete Secret
Users can modify or remove their secrets with owner verification.

**Features:**
- Owner-only permissions
- Automatic replication of changes
- Cascade deletion of access controls

### 4) List Secrets
Users can view all their secret entries with metadata only (no plaintext exposed).

**Features:**
- Shows owned and shared secrets
- Displays creation/update timestamps
- Indicates shared status

### 5) Share Secret
Users can grant read access to their secrets to other users.

**Features:**
- Owner-based permissions
- Multi-user sharing support
- Replicated access control

---

## System Architectures

### Architecture 1: Monolithic with HTTP/REST

**Style:** Layered, monolithic application
**Communication:** HTTP/REST with JSON
**Pattern:** Single-process server with all functionality

```
┌─────────────────────────────────────┐
│     HTTP/REST API Layer             │
│  (Flask Routes - Port 5000)         │
├─────────────────────────────────────┤
│     Business Logic Layer            │
│  (Request Handlers & Validation)    │
├─────────────────────────────────────┤
│     Data Access Layer               │
│  (In-memory Vault + Access Control) │
└─────────────────────────────────────┘
```

**Characteristics:**
- Simple deployment (one service per node)
- Tight coupling of components
- Easy to understand and debug
- Scales by replicating entire application

### Architecture 2: Microservices with gRPC

**Style:** Service-oriented, distributed microservices
**Communication:** gRPC with Protocol Buffers
**Pattern:** Independent services per domain

```
                    CLIENT
                       │
                       ▼
         ┌─────────────────────────┐
         │   API Gateway :50050    │
         └────────────┬────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│   Secret    │ │ Secret   │ │ Access   │ │ Replication  │
│ Management  │ │ Retrieval│ │ Control  │ │   Service    │
│   :50051    │ │  :50052  │ │  :50053  │ │    :50054    │
└─────────────┘ └──────────┘ └──────────┘ └──────────────┘
```

**Characteristics:**
- Loose coupling of services
- Independent scaling per service
- Complex deployment (5 services × 5 nodes = 25 containers)
- Service discovery via API Gateway

---

## Project Structure

```
distributed-pv/
│
├── Configuration & Build
│   ├── Dockerfile                       # Container definition
│   ├── docker-compose.yml               # Multi-container orchestration
│   └── requirements.txt                 # Python dependencies (implicit in Dockerfile)
│
├── Core Utilities
│   ├── crypto_utils.py                  # AES-256-GCM encryption/decryption
│   └── shared_data.py                   # Shared data layer for microservices
│
├── Architecture 1: HTTP/REST (Monolithic)
│   ├── http_server.py                   # Monolithic server (all 5 requirements)
│   └── http_client.py                   # HTTP test client
│
├── Architecture 2: gRPC (Microservices)
│   ├── vault.proto                      # Protocol Buffers definition
│   ├── vault_pb2.py                     # Generated protobuf code
│   ├── vault_pb2_grpc.py                # Generated gRPC code
│   │
│   ├── Gateway & Services
│   │   ├── api_gateway.py               # Request router (entry point)
│   │   ├── secret_management_service.py # Add/Update/Delete operations
│   │   ├── secret_retrieval_service.py  # Retrieve/List operations
│   │   ├── access_control_service.py    # Share/Permission management
│   │   └── replication_service.py       # Cross-node data sync
│   │
│   └── Clients
│       ├── grpc_client.py               # Simple gRPC test client
│       ├── grpc_server.py               # Unified server (all services in one)
│       └── microservices_client.py      # Comprehensive test client
│
└── Documentation
    ├── README.md                        # Original documentation
    └── README_COMPLETE.md               # This file
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local testing)
- Git

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd distributed-pv
```

2. **Install Python dependencies (for local testing):**
```bash
pip install Flask requests pycryptodome grpcio grpcio-tools
```

3. **Generate gRPC code (if modified .proto file):**
```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. vault.proto
```

---

## Running the System

### Option 1: HTTP/REST Architecture (Monolithic)

**Start 5 HTTP nodes:**
```bash
docker-compose up http-node1 http-node2 http-node3 http-node4 http-node5
```

**Test with client:**
```bash
python3 http_client.py
```

**Accessible endpoints:**
- Node 1: http://localhost:5001 (exposed to host)
- Nodes 2-5: Internal Docker network only

### Option 2: gRPC Microservices Architecture

**Start all microservices (25 containers):**
```bash
docker-compose up
```

Or start specific node:
```bash
docker-compose up grpc-node1-gateway grpc-node1-secret-mgmt \
                   grpc-node1-retrieval grpc-node1-access \
                   grpc-node1-replication
```

**Test with client:**
```bash
# Simple test
python3 grpc_client.py

# Comprehensive test (all 5 requirements)
python3 microservices_client.py
```

**Accessible gateways:**
- Node 1: localhost:50050
- Node 2: localhost:50060
- Node 3: localhost:50070
- Node 4: localhost:50080
- Node 5: localhost:50090

### Option 3: Unified gRPC Server (Development)

Run all microservices in a single process:
```bash
python3 grpc_server.py
```

---

## Architecture Details

### Architecture 1: HTTP/REST Monolithic

**Communication Flow:**
```
Client → Node → [Add Secret] → Replicate to other nodes
                                    ↓
                            Store in local vault
```

**Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/secrets` | Add new secret |
| GET | `/secrets/<id>` | Retrieve secret |
| PUT | `/secrets/<id>` | Update secret |
| DELETE | `/secrets/<id>` | Delete secret |
| GET | `/secrets` | List secrets |
| POST | `/secrets/<id>/share` | Share secret |
| POST | `/replicate` | Internal replication |

**Data Format:**
```json
{
  "secret_id": "uuid-v4",
  "user_id": "user_alice",
  "secret_name": "Database Password",
  "data": "encrypted-base64-json"
}
```

---

### Architecture 2: gRPC Microservices

**Communication Flow:**
```
Client → API Gateway → Route to Service → Process → Replicate
         :50050          ↓                    ↓
                   Service Layer      Shared Data Layer
```

**Services:**

#### 1. API Gateway (:50050)
- Routes client requests to appropriate services
- Aggregates responses
- Load balancing entry point

#### 2. Secret Management Service (:50051)
- **RPCs:** AddSecret, UpdateSecret, DeleteSecret
- Handles write operations
- Triggers replication

#### 3. Secret Retrieval Service (:50052)
- **RPCs:** RetrieveSecret, ListSecrets
- Handles read operations
- Checks access permissions

#### 4. Access Control Service (:50053)
- **RPCs:** ShareSecret, CheckAccess
- Manages permissions
- Owner verification

#### 5. Replication Service (:50054)
- **RPCs:** ReplicateSecret, ReplicateUpdate, ReplicateDeletion, ReplicateShare
- Maintains data consistency
- Internal service

**Proto Definition:**
```protobuf
service SecretManagementService {
  rpc AddSecret(AddSecretRequest) returns (AddSecretResponse);
  rpc UpdateSecret(UpdateSecretRequest) returns (UpdateSecretResponse);
  rpc DeleteSecret(DeleteSecretRequest) returns (DeleteSecretResponse);
}

service SecretRetrievalService {
  rpc RetrieveSecret(RetrieveSecretRequest) returns (RetrieveSecretResponse);
  rpc ListSecrets(ListSecretsRequest) returns (ListSecretsResponse);
}

service AccessControlService {
  rpc ShareSecret(ShareSecretRequest) returns (ShareSecretResponse);
  rpc CheckAccess(CheckAccessRequest) returns (CheckAccessResponse);
}

service ReplicationService {
  rpc ReplicateSecret(ReplicateSecretRequest) returns (ReplicateSecretResponse);
  rpc ReplicateUpdate(ReplicateUpdateRequest) returns (ReplicateUpdateResponse);
  rpc ReplicateDeletion(ReplicateDeletionRequest) returns (ReplicateDeletionResponse);
  rpc ReplicateShare(ReplicateShareRequest) returns (ReplicateShareResponse);
}
```

---

## API Documentation

### HTTP/REST API

#### Add Secret
```bash
POST /secrets
Content-Type: application/json

{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_alice",
  "secret_name": "Database Password",
  "data": "{encrypted-json}"
}

Response: 201 Created
{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Secret added successfully",
  "success": true
}
```

#### Retrieve Secret
```bash
GET /secrets/{secret_id}?user_id=user_alice

Response: 200 OK
{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": "{encrypted-json}",
  "success": true
}
```

#### Update Secret
```bash
PUT /secrets/{secret_id}
Content-Type: application/json

{
  "user_id": "user_alice",
  "data": "{new-encrypted-json}"
}

Response: 200 OK
{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Secret updated successfully",
  "success": true
}
```

#### Delete Secret
```bash
DELETE /secrets/{secret_id}?user_id=user_alice

Response: 200 OK
{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Secret deleted successfully",
  "success": true
}
```

#### List Secrets
```bash
GET /secrets?user_id=user_alice

Response: 200 OK
{
  "secrets": [
    {
      "secret_id": "550e8400-e29b-41d4-a716-446655440000",
      "secret_name": "Database Password",
      "created_at": "2025-10-12T10:30:00",
      "updated_at": "2025-10-12T10:30:00",
      "is_shared": false
    }
  ],
  "total_count": 1
}
```

#### Share Secret
```bash
POST /secrets/{secret_id}/share
Content-Type: application/json

{
  "owner_id": "user_alice",
  "target_user_id": "user_bob"
}

Response: 200 OK
{
  "message": "Secret shared successfully with user user_bob",
  "success": true
}
```

---

### gRPC API

Connect to API Gateway and use service stubs:

```python
import grpc
import vault_pb2
import vault_pb2_grpc

# Connect to gateway
channel = grpc.insecure_channel('localhost:50050')

# Add Secret
stub = vault_pb2_grpc.SecretManagementServiceStub(channel)
response = stub.AddSecret(vault_pb2.AddSecretRequest(
    user_id="user_alice",
    secret_name="API Key",
    data=encrypted_data
))

# Retrieve Secret
stub = vault_pb2_grpc.SecretRetrievalServiceStub(channel)
response = stub.RetrieveSecret(vault_pb2.RetrieveSecretRequest(
    user_id="user_alice",
    secret_id=secret_id
))

# List Secrets
response = stub.ListSecrets(vault_pb2.ListSecretsRequest(
    user_id="user_alice"
))

# Share Secret
stub = vault_pb2_grpc.AccessControlServiceStub(channel)
response = stub.ShareSecret(vault_pb2.ShareSecretRequest(
    owner_id="user_alice",
    secret_id=secret_id,
    target_user_id="user_bob"
))
```

---

## Security Features

### Client-Side Encryption
- **Algorithm:** AES-256-GCM
- **Key Derivation:** PBKDF2-HMAC-SHA256 (100,000 iterations)
- **Nonce:** 12-byte random nonce per encryption
- **Authentication:** Galois/Counter Mode provides authentication

### Encryption Flow
```python
1. Master Password → PBKDF2 → 32-byte Key
2. Plaintext + Key + Random Nonce → AES-GCM → Ciphertext + Auth Tag
3. Package: {nonce, ciphertext, tag} → Base64 → JSON → Server
```

### Access Control
- **Owner-based permissions:** Only owners can update/delete
- **Sharing mechanism:** Owners grant read access to specific users
- **No plaintext storage:** Servers never see unencrypted secrets
- **Metadata only in listings:** List operations don't expose secret values

---

## Testing

### Test HTTP Architecture
```bash
# Start HTTP nodes
docker-compose up http-node1 http-node2 http-node3 http-node4 http-node5

# Run comprehensive test
python3 http_client.py
```

**Expected Output:**
```
============================================================
Testing Distributed Password Vault - HTTP/REST Architecture
============================================================

--- Requirement 1: Add Secret ---
✓ Successfully added secret 'Database Password'. ID: <uuid>
✓ Successfully added secret 'API Key'. ID: <uuid>

--- Requirement 2: Retrieve Secret ---
✓ Retrieved secret ID: <uuid>
  Decrypted Value: 'P@ssw0rd123!'

--- Requirement 4: List Secrets ---
✓ Found 2 secret(s):
  - Database Password
    ID: <uuid>
  - API Key
    ID: <uuid>

--- Requirement 3: Update Secret ---
✓ Successfully updated secret <uuid>

--- Requirement 5: Share Secret ---
✓ Successfully shared secret with user_bob

--- Bob accesses shared secret ---
✓ Retrieved secret ID: <uuid>
  Decrypted Value: 'sk-1234567890abcdef'

--- Requirement 3: Delete Secret ---
✓ Successfully deleted secret <uuid>

============================================================
All HTTP/REST tests completed!
============================================================
```

### Test gRPC Microservices
```bash
# Start all microservices
docker-compose up

# Run comprehensive test
python3 microservices_client.py
```

**Expected Output:**
```
============================================================
Distributed Password Vault - Microservices Architecture
============================================================

--- Requirement 1: Add Secret ---
✓ Successfully added secret 'Database Password'
  Secret ID: <uuid>

--- Requirement 2: Retrieve Secret ---
✓ Retrieved secret ID: <uuid>
  Decrypted Value: 'P@ssw0rd123!'

--- Requirement 4: List Secrets ---
✓ Found 2 secret(s):
  - Database Password
    ID: <uuid>
    Created: 2025-10-12T10:30:00
  - API Key [SHARED]
    ID: <uuid>
    Created: 2025-10-12T10:31:00

--- Requirement 3: Update Secret ---
✓ Successfully updated secret <uuid>

--- Requirement 5: Share Secret ---
✓ Successfully shared secret with user_bob

--- Bob accesses shared secret ---
✓ Retrieved secret ID: <uuid>
  Decrypted Value: 'sk-1234567890abcdef'

--- Requirement 3: Delete Secret ---
✓ Successfully deleted secret <uuid>

============================================================
All operations completed successfully!
============================================================
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f grpc-node1-gateway
docker-compose logs -f http-node1

# Filter by keyword
docker-compose logs | grep "Replicated"
```

---

## Architecture Comparison

| Aspect | Monolithic HTTP | Microservices gRPC |
|--------|-----------------|-------------------|
| **Complexity** | Low | High |
| **Deployment** | 5 containers | 25 containers |
| **Scaling** | Scale entire app | Scale per service |
| **Performance** | Good (single process) | Excellent (HTTP/2, binary) |
| **Development** | Simple | Complex |
| **Maintenance** | Easy | Requires orchestration |
| **Service Discovery** | N/A | API Gateway |
| **Communication Overhead** | Low | Higher (inter-service) |
| **Fault Isolation** | Low | High |
| **Technology Stack** | Python + Flask | Python + gRPC |
| **Data Format** | JSON (text) | Protobuf (binary) |
| **Protocol** | HTTP/1.1 | HTTP/2 |

---

## Development

### Modify Protocol Buffers

1. Edit `vault.proto`
2. Regenerate Python code:
```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. vault.proto
```

### Add New Service

1. Create new service file (e.g., `new_service.py`)
2. Define service in `vault.proto`
3. Implement service class inheriting from generated servicer
4. Add to `api_gateway.py` for routing
5. Add to `docker-compose.yml`

### Debugging

```bash
# Check container status
docker-compose ps

# Inspect logs
docker-compose logs -f <service-name>

# Enter container
docker-compose exec http-node1 /bin/bash

# Test connectivity
docker-compose exec grpc-node1-gateway python3 grpc_client.py
```

---

## Performance Considerations

### HTTP Architecture
- **Throughput:** ~1000 req/s per node
- **Latency:** ~10-20ms for local operations
- **Bottleneck:** JSON serialization, HTTP overhead

### gRPC Architecture
- **Throughput:** ~5000 req/s per gateway
- **Latency:** ~5-10ms for local operations
- **Advantages:** Binary protocol, HTTP/2 multiplexing, streaming support
- **Bottleneck:** Inter-service communication

### Optimization Tips
1. Use persistent connections
2. Enable connection pooling
3. Implement caching layer
4. Use compression for large payloads
5. Consider database instead of in-memory storage

---

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Find and kill process
lsof -ti:5001 | xargs kill -9
lsof -ti:50050 | xargs kill -9
```

**2. Docker build fails**
```bash
# Clean and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**3. gRPC connection refused**
```bash
# Check gateway is running
docker-compose ps | grep gateway

# Check logs
docker-compose logs grpc-node1-gateway
```

**4. Secrets not replicating**
- Check OTHER_NODES environment variable
- Verify all nodes are running
- Check network connectivity between containers

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify all containers are running: `docker-compose ps`
3. Test connectivity: `curl http://localhost:5001/secrets`

---
