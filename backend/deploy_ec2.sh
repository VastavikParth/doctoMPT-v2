#!/bin/bash
set -e

echo "=== DoctoMPT AWS EC2 Backend Deployment ==="

# 1. Update system packages
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
fi

# 3. Setup Swap memory for t3.micro (1GB RAM) to prevent OOM
if [ ! -f /swapfile ]; then
    echo "Creating 2GB swap space for t3.micro..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# 4. Start Docker Compose services
echo "Starting Neo4j and Backend services..."
docker compose down || true
docker compose up -d --build

echo "=== Deployment Complete ==="
echo "Backend running on port 8000"
echo "Neo4j running on port 7474 / 7687"
