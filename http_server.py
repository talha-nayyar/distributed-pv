# http_server.py
# Monolithic HTTP/REST server implementing all 5 functional requirements
from flask import Flask, request, jsonify
import os
import requests
import threading
from datetime import datetime

app = Flask(__name__)

# In-memory data store for this node
# Structure: { secret_id: { user_id, secret_name, data, created_at, updated_at } }
vault = {}

# Access control database
# Structure: { secret_id: { owner_id, shared_with: [user_id1, user_id2] } }
access_control = {}

# List of other nodes in the cluster
OTHER_NODES = os.environ.get("OTHER_NODES", "").split(',') if os.environ.get("OTHER_NODES") else []

# --- Helper for Replication ---
def replicate_to_nodes(action, data):
    """Sends operations to all other nodes."""
    for node_url in OTHER_NODES:
        if not node_url: continue
        try:
            requests.post(f"{node_url}/replicate", json={"action": action, "data": data}, timeout=2)
            print(f"Replicated {action} to {node_url}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to replicate to {node_url}: {e}")


# --- API Endpoints ---

# Requirement 1: Add Secret
@app.route('/secrets', methods=['POST'])
def add_secret():
    """Add a new secret to the vault."""
    data = request.json
    user_id = data.get('user_id')
    secret_name = data.get('secret_name')
    secret_data = data.get('data')
    secret_id = data.get('secret_id')

    if not all([user_id, secret_name, secret_data, secret_id]):
        return jsonify({"error": "Missing required fields"}), 400

    timestamp = datetime.utcnow().isoformat()
    vault[secret_id] = {
        'user_id': user_id,
        'secret_name': secret_name,
        'data': secret_data,
        'created_at': timestamp,
        'updated_at': timestamp
    }
    print(f"[HTTP] Added secret {secret_id} for user {user_id}")

    # Replicate to other nodes
    threading.Thread(target=replicate_to_nodes, args=("add", {
        "secret_id": secret_id,
        "user_id": user_id,
        "secret_name": secret_name,
        "data": secret_data,
        "created_at": timestamp,
        "updated_at": timestamp
    })).start()

    return jsonify({
        "secret_id": secret_id,
        "message": "Secret added successfully",
        "success": True
    }), 201

# Requirement 2: Retrieve Secret
@app.route('/secrets/<secret_id>', methods=['GET'])
def retrieve_secret(secret_id):
    """Retrieve a secret from the vault."""
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    if secret_id not in vault:
        return jsonify({"error": "Secret not found"}), 404

    secret = vault[secret_id]

    # Check access permission
    if secret['user_id'] != user_id:
        # Check if shared
        if secret_id not in access_control or user_id not in access_control[secret_id].get('shared_with', []):
            return jsonify({"error": "Access denied"}), 403

    print(f"[HTTP] Retrieved secret {secret_id} for user {user_id}")
    return jsonify({
        "secret_id": secret_id,
        "data": secret['data'],
        "success": True
    })

# Requirement 3: Update Secret
@app.route('/secrets/<secret_id>', methods=['PUT'])
def update_secret(secret_id):
    """Update an existing secret."""
    data = request.json
    user_id = data.get('user_id')
    new_data = data.get('data')

    if not all([user_id, new_data]):
        return jsonify({"error": "Missing required fields"}), 400

    if secret_id not in vault:
        return jsonify({"error": "Secret not found"}), 404

    secret = vault[secret_id]

    # Verify ownership
    if secret['user_id'] != user_id:
        return jsonify({"error": "Only owner can update secret"}), 403

    timestamp = datetime.utcnow().isoformat()
    vault[secret_id]['data'] = new_data
    vault[secret_id]['updated_at'] = timestamp

    print(f"[HTTP] Updated secret {secret_id}")

    # Replicate update
    threading.Thread(target=replicate_to_nodes, args=("update", {
        "secret_id": secret_id,
        "data": new_data,
        "updated_at": timestamp
    })).start()

    return jsonify({
        "secret_id": secret_id,
        "message": "Secret updated successfully",
        "success": True
    })

# Requirement 3: Delete Secret
@app.route('/secrets/<secret_id>', methods=['DELETE'])
def delete_secret(secret_id):
    """Delete a secret from the vault."""
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    if secret_id not in vault:
        return jsonify({"error": "Secret not found"}), 404

    secret = vault[secret_id]

    # Verify ownership
    if secret['user_id'] != user_id:
        return jsonify({"error": "Only owner can delete secret"}), 403

    del vault[secret_id]
    if secret_id in access_control:
        del access_control[secret_id]

    print(f"[HTTP] Deleted secret {secret_id}")

    # Replicate deletion
    threading.Thread(target=replicate_to_nodes, args=("delete", {
        "secret_id": secret_id
    })).start()

    return jsonify({
        "secret_id": secret_id,
        "message": "Secret deleted successfully",
        "success": True
    })

# Requirement 4: List Secrets
@app.route('/secrets', methods=['GET'])
def list_secrets():
    """List all secrets for a user (metadata only)."""
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    user_secrets = []

    for secret_id, secret in vault.items():
        # Check if user is owner
        is_owner = secret['user_id'] == user_id

        # Check if secret is shared with user
        is_shared = False
        if secret_id in access_control:
            is_shared = user_id in access_control[secret_id].get('shared_with', [])

        if is_owner or is_shared:
            user_secrets.append({
                'secret_id': secret_id,
                'secret_name': secret['secret_name'],
                'created_at': secret['created_at'],
                'updated_at': secret['updated_at'],
                'is_shared': is_shared
            })

    print(f"[HTTP] Listed {len(user_secrets)} secrets for user {user_id}")
    return jsonify({
        "secrets": user_secrets,
        "total_count": len(user_secrets)
    })

# Requirement 5: Share Secret
@app.route('/secrets/<secret_id>/share', methods=['POST'])
def share_secret(secret_id):
    """Share a secret with another user."""
    data = request.json
    owner_id = data.get('owner_id')
    target_user_id = data.get('target_user_id')

    if not all([owner_id, target_user_id]):
        return jsonify({"error": "Missing required fields"}), 400

    if secret_id not in vault:
        return jsonify({"error": "Secret not found"}), 404

    secret = vault[secret_id]

    # Verify ownership
    if secret['user_id'] != owner_id:
        return jsonify({"error": "Only owner can share secret"}), 403

    # Initialize access control
    if secret_id not in access_control:
        access_control[secret_id] = {
            'owner_id': owner_id,
            'shared_with': []
        }

    # Add target user
    if target_user_id not in access_control[secret_id]['shared_with']:
        access_control[secret_id]['shared_with'].append(target_user_id)

    print(f"[HTTP] Shared secret {secret_id} with user {target_user_id}")

    # Replicate share
    threading.Thread(target=replicate_to_nodes, args=("share", {
        "secret_id": secret_id,
        "owner_id": owner_id,
        "target_user_id": target_user_id
    })).start()

    return jsonify({
        "message": f"Secret shared successfully with user {target_user_id}",
        "success": True
    })

# --- Internal Endpoints ---
@app.route('/replicate', methods=['POST'])
def handle_replication():
    """Internal endpoint for receiving replicated data."""
    req_data = request.json
    action = req_data.get('action')
    data = req_data.get('data')

    if action == 'add':
        vault[data['secret_id']] = {
            'user_id': data['user_id'],
            'secret_name': data['secret_name'],
            'data': data['data'],
            'created_at': data['created_at'],
            'updated_at': data['updated_at']
        }
        print(f"[HTTP-Replication] Added secret {data['secret_id']}")

    elif action == 'update':
        if data['secret_id'] in vault:
            vault[data['secret_id']]['data'] = data['data']
            vault[data['secret_id']]['updated_at'] = data['updated_at']
            print(f"[HTTP-Replication] Updated secret {data['secret_id']}")

    elif action == 'delete':
        if data['secret_id'] in vault:
            del vault[data['secret_id']]
        if data['secret_id'] in access_control:
            del access_control[data['secret_id']]
        print(f"[HTTP-Replication] Deleted secret {data['secret_id']}")

    elif action == 'share':
        secret_id = data['secret_id']
        if secret_id not in access_control:
            access_control[secret_id] = {
                'owner_id': data['owner_id'],
                'shared_with': []
            }
        if data['target_user_id'] not in access_control[secret_id]['shared_with']:
            access_control[secret_id]['shared_with'].append(data['target_user_id'])
        print(f"[HTTP-Replication] Shared secret {secret_id}")

    return jsonify({"message": "Replication successful"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)