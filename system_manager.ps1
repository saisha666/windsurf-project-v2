# Advanced System Management Script
param(
    [string]$action = "menu"
)

$ubuntuServer = "192.168.20.7"
$configFile = "system_config.json"

function Show-Menu {
    Clear-Host
    Write-Host "================ System Management Wizard ================"
    Write-Host "1: Connect to Ubuntu (RDP)"
    Write-Host "2: System Status Check"
    Write-Host "3: Quick Settings"
    Write-Host "4: Performance Optimization"
    Write-Host "5: Backup & Restore"
    Write-Host "Q: Quit"
    Write-Host "====================================================="
}

function Connect-Ubuntu {
    Write-Host "`nConnecting to Ubuntu Server..."
    $rdpTest = Test-NetConnection -ComputerName $ubuntuServer -Port 3389
    if ($rdpTest.TcpTestSucceeded) {
        Start-Process "mstsc.exe" -ArgumentList "/v:${ubuntuServer}:3389"
        Write-Host "RDP connection initiated!"
    } else {
        Write-Host "Cannot connect to Ubuntu server. Check if:"
        Write-Host "- Server is running"
        Write-Host "- RDP is enabled"
        Write-Host "- Firewall allows connection"
    }
}

function Check-SystemStatus {
    Write-Host "`nChecking System Status..."
    
    # Windows Status
    Write-Host "`nWindows Status:"
    Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, FreePhysicalMemory, TotalVisibleMemorySize | Format-List
    
    # CPU Usage
    $cpu = Get-Counter '\Processor(_Total)\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
    Write-Host "CPU Usage: $([math]::Round($cpu,2))%"
    
    # Memory Usage
    $os = Get-Ciminstance Win32_OperatingSystem
    $memory = @{
        "Total Memory" = [math]::Round($os.TotalVisibleMemorySize/1MB,2)
        "Free Memory" = [math]::Round($os.FreePhysicalMemory/1MB,2)
        "Used Memory" = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/1MB,2)
    }
    Write-Host "`nMemory Status (GB):"
    $memory | Format-Table -AutoSize
    
    # Ubuntu Status
    Write-Host "`nUbuntu Server Status:"
    $rdpStatus = Test-NetConnection -ComputerName $ubuntuServer -Port 3389 -WarningAction SilentlyContinue
    Write-Host "RDP Connection: $(if($rdpStatus.TcpTestSucceeded){'Available'}else{'Not Available'})"
}

function Show-QuickSettings {
    Write-Host "`nQuick Settings:"
    Write-Host "1: Disable Ubuntu Auto-Lock"
    Write-Host "2: Enable Performance Mode"
    Write-Host "3: Configure Auto-Start"
    Write-Host "4: Back to Main Menu"
    
    $choice = Read-Host "`nEnter your choice"
    switch ($choice) {
        "1" { 
            Write-Host "Launching Ubuntu auto-lock disable script..."
            Start-Process "mstsc.exe" -ArgumentList "/v:${ubuntuServer}:3389"
            Write-Host "After connecting, run: ./disable_lock.sh"
        }
        "2" { 
            Write-Host "Enabling Performance Mode..."
            powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
            Write-Host "Performance mode enabled!"
        }
        "3" { 
            Write-Host "Configuring Auto-Start..."
            # Add auto-start configuration here
        }
        "4" { return }
    }
}

function Optimize-Performance {
    Write-Host "`nOptimizing System Performance..."
    
    # Windows Optimization
    Write-Host "Optimizing Windows..."
    Stop-Service -Name "SysMain" -Force
    Set-Service -Name "SysMain" -StartupType Disabled
    
    # Clear temporary files
    Write-Host "Cleaning temporary files..."
    Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    
    # Disable unnecessary visual effects
    Write-Host "Optimizing visual effects..."
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2
    
    Write-Host "Performance optimization complete!"
}

function Backup-System {
    Write-Host "`nBackup & Restore Options:"
    Write-Host "1: Backup Configuration"
    Write-Host "2: Restore Configuration"
    Write-Host "3: Back to Main Menu"
    
    $choice = Read-Host "`nEnter your choice"
    switch ($choice) {
        "1" { 
            Write-Host "Creating backup..."
            # Add backup logic here
        }
        "2" { 
            Write-Host "Restoring from backup..."
            # Add restore logic here
        }
        "3" { return }
    }
}

# Main Loop
do {
    Show-Menu
    $selection = Read-Host "`nEnter your choice"
    switch ($selection) {
        '1' { Connect-Ubuntu }
        '2' { Check-SystemStatus }
        '3' { Show-QuickSettings }
        '4' { Optimize-Performance }
        '5' { Backup-System }
        'Q' { return }
    }
    pause
} until ($selection -eq 'Q')
