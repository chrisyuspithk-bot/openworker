# Dockerfile for OpenWorker on Fly.io
FROM python:3.12-slim

# Install Node.js for building the frontend
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all source files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Build the React frontend
RUN cd surfaces/gui && npm ci && npm run build

# Expose the port Fly.io expects
EXPOSE 8080

# Start the web server
CMD ["openworker-web", "--host", "0.0.0.0", "--port", "8080"]