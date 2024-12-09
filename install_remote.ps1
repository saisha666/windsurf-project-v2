# Remote server details
$SERVER = "192.168.20.7"
$USER = Read-Host "Enter your Ubuntu username"

Write-Host "Starting remote installation on Ubuntu server ($SERVER)..."

# Create SSH command function
function Invoke-RemoteCommand {
    param($Command)
    ssh "${USER}@${SERVER}" $Command
}

# Test SSH connection
Write-Host "Testing SSH connection..."
try {
    Invoke-RemoteCommand "echo 'SSH connection successful'"
} catch {
    Write-Host "Error: Could not connect to server. Please check your SSH connection."
    exit 1
}

# Install required packages
Write-Host "Installing required packages..."
Invoke-RemoteCommand @"
    sudo apt-get update
    sudo apt-get install -y python3.8 python3.8-venv python3-pip xrdp ubuntu-desktop
    sudo systemctl enable xrdp
    sudo systemctl restart xrdp
"@

# Setup RDP
Write-Host "Configuring RDP access..."
Invoke-RemoteCommand @"
    sudo ufw allow 3389/tcp
    sudo ufw reload
"@

# Create project directory
Write-Host "Creating project directory..."
Invoke-RemoteCommand "mkdir -p ~/windsurf-project"

# Copy project files
Write-Host "Copying project files..."
scp -r ./* "${USER}@${SERVER}:~/windsurf-project/"

# Run installation script
Write-Host "Running installation script..."
Invoke-RemoteCommand @"
    cd ~/windsurf-project
    chmod +x install.sh
    ./install.sh
"@

Write-Host "`nInstallation completed successfully!"
Write-Host "`nRDP Connection Details:"
Write-Host "  Server: $SERVER"
Write-Host "  Port: 3389"
Write-Host "  Username: $USER"
Write-Host "`nYou can now connect using Windows Remote Desktop:"
Write-Host "1. Press Win + R"
Write-Host "2. Type 'mstsc'"
Write-Host "3. Enter: ${SERVER}:3389"
Write-Host "4. Use your Ubuntu credentials to log in"
