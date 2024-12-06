# Test server connection
$SERVER = "192.168.20.7"
$USER = Read-Host "Enter your Ubuntu username"

Write-Host "Testing connection to Ubuntu server..."
Write-Host "Server: $SERVER"
Write-Host "Username: $USER"

# Test ping
Write-Host "`nTesting ping..."
ping $SERVER

# Test SSH port
Write-Host "`nTesting SSH port (22)..."
Test-NetConnection -ComputerName $SERVER -Port 22

# Test RDP port
Write-Host "`nTesting RDP port (3389)..."
Test-NetConnection -ComputerName $SERVER -Port 3389

Write-Host "`nIf all tests fail, please check:"
Write-Host "1. Is the Ubuntu server powered on?"
Write-Host "2. Is the IP address correct? ($SERVER)"
Write-Host "3. Are you on the same network?"
Write-Host "4. Is SSH server installed and running?"
Write-Host "   Run on Ubuntu: sudo apt install openssh-server && sudo systemctl start ssh"
Write-Host "5. Is the firewall allowing connections?"
Write-Host "   Run on Ubuntu: sudo ufw allow ssh && sudo ufw allow 3389/tcp"
