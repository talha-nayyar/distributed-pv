# performance_test.py
import time
import uuid
import grpc
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# --- Import your project's gRPC and crypto files ---
import vault_pb2
import vault_pb2_grpc
from crypto_utils import CryptoUtils

# --- Configuration ---
# General settings
NUM_REQUESTS = 200  # Total requests to send in the workload
CONCURRENT_USERS = 10 # Number of parallel threads to simulate users
RESULTS_FILE = 'performance_results.json' # File to store results between runs

# HTTP endpoint
HTTP_BASE_URL = "http://localhost:5001"

# gRPC endpoint
GRPC_GATEWAY_ADDRESS = "localhost:50050"

# --- Test Functions ---

# Initialize a crypto utility for encrypting data
crypto = CryptoUtils("benchmark-password")

def perform_http_add_secret():
    """Performs a single HTTP POST request to add a secret."""
    secret_value = str(uuid.uuid4())
    payload = {
        "secret_id": str(uuid.uuid4()),
        "user_id": "benchmark_user",
        "secret_name": "PerfTestSecret",
        "data": crypto.encrypt(secret_value)
    }
    start_time = time.monotonic()
    try:
        response = requests.post(f"{HTTP_BASE_URL}/secrets", json=payload, timeout=10)
        response.raise_for_status()
        latency = time.monotonic() - start_time
        return latency
    except requests.exceptions.RequestException as e:
        # Suppress errors during benchmark runs for cleaner output
        return None

def perform_grpc_add_secret(stub):
    """Performs a single gRPC call to add a secret."""
    secret_value = str(uuid.uuid4())
    request = vault_pb2.AddSecretRequest(
        user_id="benchmark_user",
        secret_name="PerfTestSecret",
        data=crypto.encrypt(secret_value)
    )
    start_time = time.monotonic()
    try:
        response = stub.AddSecret(request, timeout=10)
        if not response.success:
            return None # Failed request
        latency = time.monotonic() - start_time
        return latency
    except (grpc.RpcError, Exception):
        # Suppress errors during benchmark runs
        return None


def run_benchmark(test_function, num_requests, num_concurrent_users):
    """
    Runs a benchmark for a given test function.
    Returns avg_latency (float) and throughput (float).
    """
    latencies = []
    total_start_time = time.monotonic()

    grpc_channel = None
    if "grpc" in test_function.__name__:
        grpc_channel = grpc.insecure_channel(GRPC_GATEWAY_ADDRESS)
        grpc_stub = vault_pb2_grpc.SecretManagementServiceStub(grpc_channel)

    with ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
        if "grpc" in test_function.__name__:
            futures = [executor.submit(test_function, grpc_stub) for _ in range(num_requests)]
        else:
            futures = [executor.submit(test_function) for _ in range(num_requests)]
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                latencies.append(result)

    total_time_taken = time.monotonic() - total_start_time
    
    if grpc_channel:
        grpc_channel.close()

    if not latencies:
        return 0, 0

    avg_latency = sum(latencies) / len(latencies)
    throughput = len(latencies) / total_time_taken

    return avg_latency, throughput


def plot_results(results):
    """Generates and saves bar charts for the benchmark results."""
    labels = list(results.keys())
    
    # --- Latency Chart ---
    avg_latencies = [res['latency'] * 1000 for res in results.values()] # convert to ms
    x = np.arange(len(labels))
    width = 0.4
    
    fig, ax = plt.subplots(figsize=(8, 6))
    rects = ax.bar(x, avg_latencies, width, color=['skyblue', 'lightcoral'])
    
    ax.set_ylabel('Average Latency (ms)')
    ax.set_title(f'Latency Comparison (Lower is Better)\n{NUM_REQUESTS} requests, {CONCURRENT_USERS} concurrent users')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.bar_label(rects, fmt='%.2f ms', padding=3)
    
    fig.tight_layout()
    plt.savefig('latency_comparison.png')
    print("\nSaved latency comparison graph to latency_comparison.png")
    plt.close()

    # --- Throughput Chart ---
    throughputs = [res['throughput'] for res in results.values()]
    fig, ax = plt.subplots(figsize=(8, 6))
    rects = ax.bar(x, throughputs, width, color=['skyblue', 'lightcoral'])
    
    ax.set_ylabel('Requests per Second')
    ax.set_title(f'Throughput Comparison (Higher is Better)\n{NUM_REQUESTS} requests, {CONCURRENT_USERS} concurrent users')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.bar_label(rects, fmt='%.2f req/s', padding=3)
    
    fig.tight_layout()
    plt.savefig('throughput_comparison.png')
    print("Saved throughput comparison graph to throughput_comparison.png")
    plt.close()


if __name__ == "__main__":
    print("Starting performance benchmark...")
    
    # Load previous results if they exist
    results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            results = json.load(f)

    # --- Check which server is running ---
    is_http_running, is_grpc_running = False, False
    try:
        requests.get(HTTP_BASE_URL, timeout=1)
        is_http_running = True
    except requests.exceptions.RequestException: pass
    try:
        with grpc.insecure_channel(GRPC_GATEWAY_ADDRESS) as channel:
            grpc.channel_ready_future(channel).result(timeout=1)
        is_grpc_running = True
    except (grpc.FutureTimeoutError, grpc.RpcError): pass

    if not is_http_running and not is_grpc_running:
        print("\nERROR: No running server detected. Please start a system with 'docker-compose up'.")
        if os.path.exists(RESULTS_FILE):
            os.remove(RESULTS_FILE) # Clean up for next run
            print(f"Cleared stale results file '{RESULTS_FILE}'.")

    if is_http_running:
        print(f"\n--- Benchmarking HTTP/REST ---")
        latency, throughput = run_benchmark(perform_http_add_secret, NUM_REQUESTS, CONCURRENT_USERS)
        if throughput > 0:
            results['HTTP/REST'] = {'latency': latency, 'throughput': throughput}
            print(f"  Average Latency: {latency * 1000:.2f} ms | Throughput: {throughput:.2f} req/s")
    
    if is_grpc_running:
        print(f"\n--- Benchmarking gRPC ---")
        latency, throughput = run_benchmark(perform_grpc_add_secret, NUM_REQUESTS, CONCURRENT_USERS)
        if throughput > 0:
            results['gRPC'] = {'latency': latency, 'throughput': throughput}
            print(f"  Average Latency: {latency * 1000:.2f} ms | Throughput: {throughput:.2f} req/s")

    # Save results to a file
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f)

    # If we have both results, plot them
    if 'HTTP/REST' in results and 'gRPC' in results:
        print("\n--- Both systems benchmarked. Generating Comparison Graphs ---")
        plot_results(results)
        os.remove(RESULTS_FILE) # Clean up for next run
        print(f"Cleared results file '{RESULTS_FILE}'.")
    elif results:
        print("\nBenchmark completed for one system. Please run the other system and execute this script again.")
    else:
        print("\nBenchmark failed to collect any data.")