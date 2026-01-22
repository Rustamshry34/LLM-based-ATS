#!/bin/bash
set -e

# GitHub Actions tarafından sağlanacak
LLAMA_API_KEY="$1"
RDS_ENDPOINT="$2"
POSTGRES_PASSWORD="$3"

sudo apt update
sudo apt install -y python3-pip python3-venv git nginx

git clone https://github.com/rustamshiriyev/your-ats-repo.git /home/ubuntu/ats
cd /home/ubuntu/ats

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env dosyası
cat > .env <<EOF
LLAMA_CLOUD_API_KEY=$LLAMA_API_KEY
DATABASE_URL=postgresql://postgres:$POSTGRES_PASSWORD@$RDS_ENDPOINT/ats_system
EOF

# Systemd servisi
sudo tee /etc/systemd/system/ats.service > /dev/null <<EOT
[Unit]
Description=ATS FastAPI App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ats
EnvironmentFile=/home/ubuntu/ats/.env
ExecStart=/home/ubuntu/ats/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl start ats
sudo systemctl enable ats

# Nginx
sudo tee /etc/nginx/sites-available/ats > /dev/null <<EOT
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOT

sudo ln -sf /etc/nginx/sites-available/ats /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
