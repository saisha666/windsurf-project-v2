# Advanced Data Collection System

## 1. Environment Reset Procedure

### Windows PATH Reset
```powershell
# Run as Administrator in PowerShell
[Environment]::SetEnvironmentVariable(
    "Path",
    "C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\",
    "Machine"
)
```

### WSL Reset Steps
1. Open PowerShell as Administrator
2. Commands to remove existing WSL:
```powershell
wsl --shutdown
wsl --unregister Ubuntu-22.04
wsl --unregister docker-desktop
wsl --unregister docker-desktop-data
```

## 2. Fresh System Setup

### Core Components
1. **WSL2 Ubuntu 22.04 LTS**
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

2. **Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install with WSL2 backend
   - Enable Ubuntu-22.04 integration

3. **Dev Home**
   - Install from Microsoft Store
   - Configure for VM management

## 3. Agent Roles Configuration

### 1. Research Agent
```python
class ResearchAgent:
    """
    Responsibilities:
    - Analyze real-time data streams
    - Identify websocket patterns
    - Document state changes
    """
    def __init__(self):
        self.research_data = []
        self.patterns_discovered = set()
```

### 2. Engineering Agent
```python
class EngineeringAgent:
    """
    Responsibilities:
    - Implement data collection logic
    - Manage network connections
    - Handle connection stability
    """
    def __init__(self):
        self.connection_configs = {}
        self.stability_patterns = []
```

### 3. Analysis Agent
```python
class AnalysisAgent:
    """
    Responsibilities:
    - Process real-time streams
    - Identify numerical patterns
    - Generate statistical insights
    """
    def __init__(self):
        self.data_patterns = {}
        self.insights = []
```

## 4. Development Environment

### WSL Ubuntu Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Development tools
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    chromium-browser \
    xvfb

# Create Python virtual environment
python3 -m venv ~/venv
source ~/venv/bin/activate
```

### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  collector:
    build: .
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - collector_net
```

## 5. Network Configuration

### Proxy Setup in WSL
```bash
# Install proxy tools
sudo apt install -y proxychains4 tor

# Configure proxychains
sudo nano /etc/proxychains4.conf
# Add your proxy servers
```

### VPN Configuration
```bash
# OpenVPN setup
sudo apt install -y openvpn
sudo openvpn --config /path/to/config.ovpn
```

## 6. Recovery Procedures

### System Recovery
1. Save all configurations
2. Document current state
3. Backup important data
4. Reset environment if needed

### Session Recovery
```python
def recover_session():
    """
    Restore previous session state
    """
    save_point = load_last_checkpoint()
    restore_connection_state(save_point)
    reconnect_network()
```

## 7. Maintenance Schedule

### Daily Tasks
1. Check system logs
2. Update proxy list
3. Verify data collection
4. Backup configurations

### Weekly Tasks
1. Update connection profiles
2. Analyze connection patterns
3. Update stability measures
4. System health check

## 8. Emergency Procedures

### Quick Recovery Steps
1. Stop all running processes
2. Reset WSL if needed:
   ```powershell
   wsl --shutdown
   wsl --export Ubuntu-22.04 backup.tar
   ```
3. Restore from backup:
   ```powershell
   wsl --import Ubuntu-22.04 .\backup.tar
   ```

## 9. Version Control

### Git Configuration
```bash
# Setup Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Create .gitignore
echo "venv/
*.log
*.pyc
__pycache__/
.env" > .gitignore
```

Remember to update this document whenever significant changes are made to the system or new patterns are discovered.
