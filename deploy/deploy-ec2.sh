#!/bin/bash
# PATH: deploy/deploy-ec2.sh
# PURPOSE: Deploy Physics AI to AWS EC2
#
# USAGE:
#   1. Run: aws configure (enter your credentials)
#   2. Run: chmod +x deploy/deploy-ec2.sh && ./deploy/deploy-ec2.sh

set -e

echo "=========================================="
echo "  Physics AI - EC2 Deployment Script"
echo "=========================================="

# Configuration
INSTANCE_TYPE="t2.micro"
AMI_ID="ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS in us-east-1
KEY_NAME="physics-ai-key"
SECURITY_GROUP_NAME="physics-ai-sg"
INSTANCE_NAME="physics-ai-server"
REGION="us-east-1"

# Set region
export AWS_DEFAULT_REGION=$REGION

echo ""
echo "[1/7] Verifying AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run: aws configure"
    exit 1
fi
echo "✅ AWS credentials verified"

echo ""
echo "[2/7] Creating key pair..."
if aws ec2 describe-key-pairs --key-names $KEY_NAME > /dev/null 2>&1; then
    echo "⚠️  Key pair '$KEY_NAME' already exists, using existing"
else
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ~/.ssh/${KEY_NAME}.pem
    chmod 400 ~/.ssh/${KEY_NAME}.pem
    echo "✅ Key pair created: ~/.ssh/${KEY_NAME}.pem"
fi

echo ""
echo "[3/7] Creating security group..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)

if aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME > /dev/null 2>&1; then
    SG_ID=$(aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME --query 'SecurityGroups[0].GroupId' --output text)
    echo "⚠️  Security group already exists: $SG_ID"
else
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for Physics AI" \
        --vpc-id $VPC_ID \
        --query 'GroupId' --output text)
    
    # Allow SSH
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
    # Allow HTTP
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
    # Allow HTTPS
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
    # Allow Frontend (3000)
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 3000 --cidr 0.0.0.0/0
    # Allow Backend API (5002)
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 5002 --cidr 0.0.0.0/0
    
    echo "✅ Security group created: $SG_ID"
fi

echo ""
echo "[4/7] Creating user data script..."
USER_DATA=$(cat <<'USERDATA'
#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y git curl nginx python3 python3-pip python3-venv nodejs npm

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Clone repository
cd /opt
git clone https://github.com/vastdreams/physics-ai.git
cd physics-ai

# Setup Python backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Frontend
cd frontend
npm install
npm run build

# Configure Nginx
cat > /etc/nginx/sites-available/physics-ai <<'NGINX'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /opt/physics-ai/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket proxy
    location /socket.io {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/physics-ai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Create systemd service for backend
cat > /etc/systemd/system/physics-ai-api.service <<'SERVICE'
[Unit]
Description=Physics AI API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/physics-ai
Environment=PATH=/opt/physics-ai/venv/bin
ExecStart=/opt/physics-ai/venv/bin/python -m api.app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable physics-ai-api
systemctl start physics-ai-api

echo "Physics AI deployment complete!" > /var/log/physics-ai-deploy.log
USERDATA
)

echo "✅ User data script prepared"

echo ""
echo "[5/7] Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --user-data "$USER_DATA" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

echo ""
echo "[6/7] Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID
echo "✅ Instance is running"

echo ""
echo "[7/7] Getting instance details..."
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

PUBLIC_DNS=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicDnsName' \
    --output text)

echo ""
echo "=========================================="
echo "  🚀 DEPLOYMENT SUCCESSFUL!"
echo "=========================================="
echo ""
echo "Instance ID:  $INSTANCE_ID"
echo "Public IP:    $PUBLIC_IP"
echo "Public DNS:   $PUBLIC_DNS"
echo ""
echo "URLs (wait 3-5 minutes for setup to complete):"
echo "  Frontend:   http://$PUBLIC_IP"
echo "  API:        http://$PUBLIC_IP/api/health"
echo ""
echo "SSH Access:"
echo "  ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
echo "To check deployment progress:"
echo "  ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'tail -f /var/log/cloud-init-output.log'"
echo ""
echo "=========================================="
