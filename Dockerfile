# Dockerfile
FROM python:3.11

WORKDIR /app

# Install dependencies for both HTTP and gRPC architectures
# Using latest compatible versions
RUN pip install --no-cache-dir \
    Flask==3.0.0 \
    requests==2.31.0 \
    pycryptodome==3.19.0 \
    protobuf>=4.21.0 \
    grpcio>=1.60.0 \
    grpcio-tools>=1.60.0 \
    redis==5.0.1

# Copy application files
COPY . .

# Default command (can be overridden in docker-compose)
# For HTTP architecture: python http_server.py
# For gRPC microservices: Use specific service files
CMD ["python", "http_server.py"]