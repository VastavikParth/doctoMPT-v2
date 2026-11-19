#!/bin/bash
set -e

echo '>>> 1. Creating 2GB swap for t3.micro memory stability...'
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo '>>> 2. Installing Nginx, fail2ban, UFW, python3-venv, and Docker...'
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx fail2ban ufw python3-venv python3-pip docker.io docker-compose-v2
sudo usermod -aG docker ubuntu || true

echo '>>> 3. Hardening docker-compose to bind Neo4j STRICTLY to localhost...'
sed -i 's/"7474:7474"/"127.0.0.1:7474:7474"/g' /home/ubuntu/doctompt-backend/docker-compose.yml
sed -i 's/"7687:7687"/"127.0.0.1:7687:7687"/g' /home/ubuntu/doctompt-backend/docker-compose.yml

echo '>>> 4. Configuring UFW Firewall...'
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw limit 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo '>>> 5. Enabling fail2ban...'
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

echo '>>> 6. Configuring Nginx reverse proxy with security headers & rate limiting...'
cat << 'NGINX_CONF' | sudo tee /etc/nginx/sites-available/doctompt
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=15r/s;

server {
    listen 80;
    server_name _;

    server_tokens off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        limit_req zone=api_limit burst=30 nodelay;

        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts to prevent slowloris attacks
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX_CONF

sudo ln -sf /etc/nginx/sites-available/doctompt /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo '>>> Server hardening complete! Nginx, UFW, and fail2ban are live.'
