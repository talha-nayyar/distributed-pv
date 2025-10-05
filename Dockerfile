# Dockerfile
FROM python:3.11

WORKDIR /app

# Install dependencies
RUN pip install Flask requests pycryptodome grpcio grpcio-tools

# Copy application files
COPY . .

# Default command (can be overridden in docker-compose)
CMD ["python", "http_server.py"]