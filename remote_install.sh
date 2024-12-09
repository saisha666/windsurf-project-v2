#!/bin/bash

# Remote server details
SERVER_IP="192.168.20.7"
SERVER_USER="$1"  # First argument should be the username

# Check if username is provided
if [ -z "$SERVER_USER" ]; then
    echo "Usage: ./remote_install.sh <username>"
    exit 1
fi

echo "Setting up Windsurf Project on Ubuntu server ($SERVER_IP)..."

# Install required packages on remote server
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    # Update package list
    sudo apt-get update

    # Install Python and required packages
    sudo apt-get install -y python3.8 python3.8-venv python3-pip xrdp

    # Configure xRDP
    sudo systemctl enable xrdp
    sudo systemctl restart xrdp

    # Install CUDA if not present (optional)
    if ! command -v nvidia-smi &> /dev/null; then
        echo "Installing CUDA..."
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
        sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
        sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
        sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
        sudo apt-get update
        sudo apt-get -y install cuda
    fi

    # Create project directory
    mkdir -p ~/windsurf-project
EOF

# Copy project files to remote server
echo "Copying project files..."
scp -r ./* $SERVER_USER@$SERVER_IP:~/windsurf-project/

# Run installation on remote server
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    cd ~/windsurf-project

    # Make install script executable
    chmod +x install.sh

    # Run installation
    ./install.sh

    # Setup RDP access
    echo "Setting up RDP access..."
    sudo apt-get install -y ubuntu-desktop
    sudo systemctl set-default graphical.target
    
    # Configure firewall
    sudo ufw allow 3389/tcp
    sudo ufw reload

    echo "Installation complete!"
    echo "You can now connect to the server using RDP:"
    echo "Address: $SERVER_IP"
    echo "Username: $SERVER_USER"
    echo "Port: 3389"
EOF

echo "Remote installation completed successfully!"
echo "RDP Connection Details:"
echo "  Address: $SERVER_IP"
echo "  Port: 3389"
echo "  Username: $SERVER_USER"
