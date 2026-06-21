#!/bin/bash
set -e

echo "==========================================="
echo "Updating apt and installing dependencies..."
echo "==========================================="
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python3-venv nginx git

echo "==========================================="
echo "Setting up Virtual Environment..."
echo "==========================================="
cd /home/ubuntu/videoStraming
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "==========================================="
echo "Setting up Systemd Service..."
echo "==========================================="
sudo bash -c 'cat > /etc/systemd/system/streamtube.service << EOF
[Unit]
Description=StreamTube Uvicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/videoStraming
ExecStart=/home/ubuntu/videoStraming/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
EnvironmentFile=/home/ubuntu/videoStraming/.env

[Install]
WantedBy=multi-user.target
EOF'

echo "==========================================="
echo "Enabling and starting service..."
echo "==========================================="
sudo systemctl daemon-reload
sudo systemctl enable streamtube
sudo systemctl restart streamtube

echo "==========================================="
echo "Setting up Nginx..."
echo "==========================================="
sudo bash -c 'cat > /etc/nginx/sites-available/streamtube << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_addrs;
    }
}
EOF'

sudo ln -sf /etc/nginx/sites-available/streamtube /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "==========================================="
echo "Deployment completed successfully! \U0001F680"
echo "==========================================="
