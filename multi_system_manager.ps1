# Advanced Multi-System Management Script
param(
    [string]$action = "menu"
)

# System Configuration
$systems = @{
    "Ubuntu" = @{
        "IP" = "192.168.20.7"
        "Type" = "Linux"
        "Port" = 3389
    }
    "Windows11" = @{
        "IP" = "192.168.20.11"
        "Type" = "Windows"
        "Port" = 3389
    }
}

function Show-Menu {
    Clear-Host
    Write-Host "================ Multi-System Management Wizard ================"
    Write-Host "1: System Connections"
    Write-Host "2: System Status Dashboard"
    Write-Host "3: Performance Management"
    Write-Host "4: Security Settings"
    Write-Host "5: Backup & Sync"
    Write-Host "Q: Quit"
    Write-Host "=========================================================="
}

function Show-ConnectionMenu {
    Clear-Host
    Write-Host "================ System Connections ================"
    Write-Host "1: Connect to Ubuntu (192.168.20.7)"
    Write-Host "2: Connect to Windows 11 (192.168.20.11)"
    Write-Host "3: Test All Connections"
    Write-Host "4: Back to Main Menu"
    
    $choice = Read-Host "`nEnter your choice"
    switch ($choice) {
        "1" { Connect-ToSystem "Ubuntu" }
        "2" { Connect-ToSystem "Windows11" }
        "3" { Test-AllConnections }
        "4" { return }
    }
}

function Connect-ToSystem {
    param($systemName)
    
    $system = $systems[$systemName]
    Write-Host "`nConnecting to $systemName (${$system.IP})..."
    
    $rdpTest = Test-NetConnection -ComputerName $system.IP -Port $system.Port
    if ($rdpTest.TcpTestSucceeded) {
        Start-Process "mstsc.exe" -ArgumentList "/v:$($system.IP):$($system.Port)"
        Write-Host "RDP connection initiated!"
    } else {
        Write-Host "Cannot connect to $systemName. Check if:"
        Write-Host "- System is running"
        Write-Host "- RDP is enabled"
        Write-Host "- Firewall allows connection"
    }
}

function Test-AllConnections {
    Write-Host "`nTesting all system connections..."
    
    foreach ($system in $systems.GetEnumerator()) {
        Write-Host "`nTesting $($system.Key) ($($system.Value.IP)):"
        
        # Test ping
        $ping = Test-Connection -ComputerName $system.Value.IP -Count 1 -Quiet
        Write-Host "Ping: $(if($ping){'Success'}else{'Failed'})"
        
        # Test RDP
        $rdp = Test-NetConnection -ComputerName $system.Value.IP -Port $system.Value.Port -WarningAction SilentlyContinue
        Write-Host "RDP: $(if($rdp.TcpTestSucceeded){'Available'}else{'Not Available'})"
    }
}

function Show-StatusDashboard {
    Clear-Host
    Write-Host "================ System Status Dashboard ================"
    
    foreach ($system in $systems.GetEnumerator()) {
        Write-Host "`n$($system.Key) Status ($($system.Value.IP)):"
        $status = Test-Connection -ComputerName $system.Value.IP -Count 1 -Quiet
        Write-Host "Status: $(if($status){'Online'}else{'Offline'})"
        
        if ($status) {
            $rdp = Test-NetConnection -ComputerName $system.Value.IP -Port $system.Value.Port -WarningAction SilentlyContinue
            Write-Host "RDP Access: $(if($rdp.TcpTestSucceeded){'Available'}else{'Not Available'})"
            
            # For Windows systems, get additional info
            if ($system.Value.Type -eq "Windows") {
                try {
                    $os = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $system.Value.IP -ErrorAction SilentlyContinue
                    if ($os) {
                        $memory = @{
                            "Total Memory (GB)" = [math]::Round($os.TotalVisibleMemorySize/1MB, 2)
                            "Free Memory (GB)" = [math]::Round($os.FreePhysicalMemory/1MB, 2)
                        }
                        Write-Host "Memory Status:"
                        $memory | Format-Table -AutoSize
                    }
                } catch {
                    Write-Host "Could not retrieve detailed system information"
                }
            }
        }
    }
}

function Show-PerformanceMenu {
    Clear-Host
    Write-Host "================ Performance Management ================"
    Write-Host "1: Optimize Ubuntu"
    Write-Host "2: Optimize Windows 11"
    Write-Host "3: System Cleanup"
    Write-Host "4: Back to Main Menu"
    
    $choice = Read-Host "`nEnter your choice"
    switch ($choice) {
        "1" { Optimize-Ubuntu }
        "2" { Optimize-Windows11 }
        "3" { Clear-SystemTemp }
        "4" { return }
    }
}

function Optimize-Ubuntu {
    Write-Host "`nOptimizing Ubuntu system..."
    $ubuntuSystem = $systems["Ubuntu"]
    
    # Launch RDP connection
    Start-Process "mstsc.exe" -ArgumentList "/v:$($ubuntuSystem.IP):$($ubuntuSystem.Port)"
    
    Write-Host "Please run these commands on Ubuntu:"
    Write-Host "1. ./disable_lock.sh"
    Write-Host "2. ./disable_lock_gui.sh"
    Write-Host "3. sudo apt-get clean"
    Write-Host "4. sudo apt-get autoremove"
}

function Optimize-Windows11 {
    Write-Host "`nOptimizing Windows 11 system..."
    
    # Performance settings
    Write-Host "Applying performance optimizations..."
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2
    
    # Disable unnecessary services
    $services = @("SysMain", "WSearch")
    foreach ($service in $services) {
        Stop-Service -Name $service -Force
        Set-Service -Name $service -StartupType Disabled
    }
    
    # Clear temp files
    Clear-SystemTemp
    
    Write-Host "Windows 11 optimization complete!"
}

function Clear-SystemTemp {
    Write-Host "`nCleaning temporary files..."
    
    # Clean Windows temp
    Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "System cleanup complete!"
}

function Show-SecurityMenu {
    Clear-Host
    Write-Host "================ Security Settings ================"
    Write-Host "1: Configure Ubuntu Firewall"
    Write-Host "2: Configure Windows 11 Firewall"
    Write-Host "3: Check Security Status"
    Write-Host "4: Back to Main Menu"
    
    $choice = Read-Host "`nEnter your choice"
    switch ($choice) {
        "1" { Configure-UbuntuFirewall }
        "2" { Configure-WindowsFirewall }
        "3" { Check-SecurityStatus }
        "4" { return }
    }
}

function update Configure-UbuntuFirewall-UbuntuFirewall {
    Write-Host "`nConfiguring Ubuntu Firewall..."
    Write-Host "Run these commands on Ubuntu:"
    Write-Host "sudo ufw allow 3389/tcp"
    Write-Host "sudo ufw allow 22/tcp"
    Write-Host "sudo ufw enable"
c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py:103: SyntaxWarning: invalid escape sequence '\|'
  cmd = "top -bn1 | grep 'Cpu\|Mem'"
Traceback (most recent call last):
  File "c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py", line 1, in <module>
    import rpy2.robjects as robjects
ModuleNotFoundError: No module named 'rpy2'
c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py:103: SyntaxWarning: invalid escape sequence '\|'
  cmd = "top -bn1 | grep 'Cpu\|Mem'"
Traceback (most recent call last):
  File "c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py", line 1, in <module>
    import rpy2.robjects as robjects
ModuleNotFoundError: No module named 'rpy2'c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py:103: SyntaxWarning: invalid escape sequence '\|'
  cmd = "top -bn1 | grep 'Cpu\|Mem'"
Traceback (most recent call last):
  File "c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py", line 1, in <module>
    import rpy2.robjects as robjects
ModuleNotFoundError: No module named 'rpy2'
c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py:103: SyntaxWarning: invalid escape sequence '\|'
  cmd = "top -bn1 | grep 'Cpu\|Mem'"
Traceback (most recent call last):
  File "c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py", line 1, in <module>
    import rpy2.robjects as robjects
ModuleNotFoundError: No module named 'rpy2'

function update Configure-WindowsFirewall {

    Write-Host "`nConfiguring Windows Firewall.{"
    
    # Allow RDP
    New-NetFirewallRule -DisplayName "RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow
    
    Write-Host "Windows Firewall configured!"
}

# Main Loop
do {
    Show-Menu
    $selection = Read-Host "`nEnter your choice"
    switch ($selection) {
        '1' { Show-ConnectionMenu }
        '2' { Show-StatusDashboard }
        '3' { Show-PerformanceMenu }
        '4' { Show-SecurityMenu }
        '5' { Show-BackupMenu }
        'Q' { return }
    }
    pause
} until ($selection -eq 'Q')
