# Evolution Gaming Data Collection System

## Project Overview
Advanced data collection system designed to gather real-time data from Evolution Gaming's live casino platform.

## Key Components

### 1. Environment Setup (WSL2 Ubuntu)
```bash
# Install WSL2 Ubuntu
wsl --install -d Ubuntu

# Update and install essential packages
sudo apt update && sudo apt upgrade
sudo apt install -y python3-pip chromium-browser xvfb

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. VPN/Network Configuration
- Use WSL for isolated network stack
- Configure VPN inside WSL container
- Use Docker networks for additional isolation

### 3. Browser Management
```python
# Multiple browser strategies:
- Undetected ChromeDriver (versions 110-114)
- Brave Browser
- Firefox (fallback)
- Chrome DevTools Protocol
```

### 4. Data Collection Phases

#### Phase 1: Scout Mode
- Uses browser extensions
- Records network traffic (HAR files)
- Monitors:
  - WebSocket connections
  - XHR requests
  - Vue.js state updates
  - Game events

#### Phase 2: Collection Mode
- Uses discovered endpoints
- Rotates browsers/proxies
- Implements stealth measures

### 5. Anti-Detection Measures
```python
# Browser fingerprint randomization
- Random user agents
- Viewport variations
- Plugin spoofing
- WebDriver hiding
```

### 6. Data Storage
```
/data
  /raw        # Raw network captures
  /processed  # Cleaned game data
  /archive    # Historical data
```

## Quick Start

### 1. WSL Setup
```bash
# 1. Enable WSL2
wsl --set-default-version 2

# 2. Install Ubuntu
wsl --install -d Ubuntu

# 3. Setup Development Environment
sudo apt update && sudo apt upgrade
sudo apt install -y python3-pip python3-venv
```

### 2. Project Setup
```bash
# 1. Create virtual environment
python3 -m venv env
source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install browser drivers
./scripts/setup_drivers.sh
```

### 3. Running the Scraper
```bash
# Scout mode (with browser UI)
python src/main.py --mode scout

# Collection mode (headless)
python src/main.py --mode collect
```

## Troubleshooting

### Common Issues
1. **Browser Detection**
   - Solution: Rotate user agents and use undetected-chromedriver
   
2. **Network Blocks**
   - Solution: Use WSL2 with VPN/Docker isolation
   
3. **Data Inconsistency**
   - Solution: Implement retry mechanism with different browsers

### Recovery Procedures
1. **Connection Lost**
   ```python
   # Automatic recovery
   while True:
       try:
           # Collection logic
       except ConnectionError:
           switch_proxy()
           continue
   ```

2. **Browser Crash**
   - System auto-switches to next browser in pool
   - Maintains separate logs for each browser type

## Data Processing

### 1. Raw Data
```python
{
    'websockets': set(),   # WebSocket endpoints
    'xhr_requests': [],    # XHR requests
    'game_states': [],     # Game state updates
}
```

### 2. Processed Data
```python
{
    'game_id': str,
    'timestamp': datetime,
    'results': List[int],
    'metrics': Dict
}
```

## Security Notes

### 1. Browser Security
- Use isolated browser profiles
- Rotate fingerprints regularly
- Clear data between sessions

### 2. Network Security
- Use WSL2 for network isolation
- Implement proxy rotation
- Monitor request patterns

### 3. Data Security
- Encrypt sensitive data
- Use secure storage
- Implement access logging

## Maintenance

### Daily Tasks
1. Check error logs
2. Verify data consistency
3. Update proxy list
4. Rotate browser profiles

### Weekly Tasks
1. Update ChromeDriver versions
2. Analyze detection patterns
3. Optimize collection strategies

## Future Improvements

### Planned Features
1. Machine learning for pattern detection
2. Automated proxy testing
3. Real-time data validation
4. Advanced browser fingerprinting

### Research Areas
1. WebRTC handling
2. Browser extension development
3. Network traffic analysis
4. Automated recovery strategies

## Emergency Contacts
- System Administrator: [Contact]
- Network Support: [Contact]
- Data Team: [Contact]

Remember: This is a living document. Update it as new patterns are discovered or when implementation details change.
