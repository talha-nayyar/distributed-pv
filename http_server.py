# http_server.py
from flask import Flask, request, jsonify
import os
import requests
import threading

app = Flask(__name__)

# In-memory data store for this node
vault = {}

# List of other nodes in the cluster. In a real system, this would be dynamic.
# We'll get this from an environment variable, e.g., "http://node2:5000,http://node3:5000"
OTHER_NODES = os.environ.get("OTHER_NODES", "").split(',') if os.environ.get("OTHER_NODES") else []

# --- Helper for Replication ---
def replicate_to_nodes(secret_id, data):
    """Sends the new secret to all other nodes."""
    for node_url in OTHER_NODES:
        if not node_url: continue
        try:
            # This internal endpoint bypasses the replication logic on the receiving node
            requests.post(f"{node_url}/replicate", json={"id": secret_id, "data": data}, timeout=2)
            print(f"Replicated {secret_id} to {node_url}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to replicate {secret_id} to {node_url}: {e}")


# --- API Endpoints ---
@app.route('/secrets', methods=['POST'])
def add_secret():
    """Endpoint to add a new secret. This is the primary entry point."""
    data = request.json
    secret_id = data.get('id')
    secret_data = data.get('data')

    if not secret_id or not secret_data:
        return jsonify({"error": "Missing id or data"}), 400

    vault[secret_id] = secret_data
    print(f"Added secret {secret_id} locally.")

    # Replicate to other nodes in the background
    threading.Thread(target=replicate_to_nodes, args=(secret_id, secret_data)).start()
    
    return jsonify({"message": "Secret added successfully"}), 201

@app.route('/secrets/<secret_id>', methods=['GET'])
def retrieve_secret(secret_id):
    """Endpoint to retrieve a secret."""
    secret_data = vault.get(secret_id)
    if not secret_data:
        return jsonify({"error": "Secret not found"}), 404
    
    return jsonify({"id": secret_id, "data": secret_data})

# --- Internal Endpoints ---
@app.route('/replicate', methods=['POST'])
def handle_replication():
    """Internal endpoint for receiving replicated data."""
    data = request.json
    secret_id = data.get('id')
    secret_data = data.get('data')
    vault[secret_id] = secret_data
    print(f"Received replicated secret {secret_id}.")
    return jsonify({"message": "Replication successful"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)