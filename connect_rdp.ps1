# RDP Connection Script
$SERVER = "192.168.20.7"
$PORT = "3389"

Write-Host "Connecting to Ubuntu Server via RDP..."
Write-Host "Server: $SERVER"
Write-Host "Port: $PORT"

# Test RDP port first
Write-Host "`nTesting RDP connection..."
$rdpTest = Test-NetConnection -ComputerName $SERVER -Port $PORT
if ($rdpTest.TcpTestSucceeded) {
    Write-Host "RDP port is open and ready!"
    
    # Launch Remote Desktop Connection
    Write-Host "`nLaunching Remote Desktop Connection..."
    Start-Process "mstsc.exe" -ArgumentList "/v:${SERVER}:${PORT}"
    
    Write-Host "`nRemote Desktop window should open."
    Write-Host "Please enter your Ubuntu credentials when prompted."
} else {
    Write-Host "Error: Cannot connect to RDP port!"
    Write-Host "Please check if:"
    Write-Host "1. The Ubuntu server is running"
    Write-Host "2. XRDP is installed and running on Ubuntu"
    Write-Host "3. Firewall allows RDP connections"
    Write-Host "`nRun these commands on Ubuntu to fix RDP:"
    Write-Host "sudo apt-get update"
    Write-Host "sudo apt-get install -y xrdp ubuntu-desktop"
    Write-Host "sudo systemctl enable xrdp"
    Write-Host "sudo systemctl restart xrdp"
    Write-Host "sudo ufw allow 3389/tcp"
    Write-Host "sudo ufw reload"
}
