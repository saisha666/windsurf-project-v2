import os
import random
import time
from datetime import datetime

# Define the directory structure
project_directories = [
    'src/voice',
    'src/scrapers',
    'src/config',
    'tests',
    'logs'
]

# Data storage structure (local instead of Q: drive)
DATA_ROOT = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'RouletteData')
data_directories = [
    os.path.join(DATA_ROOT, 'System', 'Cache'),
    os.path.join(DATA_ROOT, 'System', 'Backup'),
    os.path.join(DATA_ROOT, 'System', 'Archive'),
    os.path.join(DATA_ROOT, 'System', 'Temp')
]

def create_random_subfolder(base_path):
    """Create a random subfolder for stealth"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_id = str(random.randint(1000, 9999))
    folder_name = f"sys_{timestamp}_{random_id}"
    full_path = os.path.join(base_path, folder_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path

# Create project directories
for dir_path in project_directories:
    full_path = os.path.join(os.getcwd(), dir_path)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created project directory: {full_path}")

# Create data directories locally
try:
    for dir_path in data_directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created data directory: {dir_path}")
        
        # Create random subfolder in Cache directory
        if 'Cache' in dir_path:
            subfolder = create_random_subfolder(dir_path)
            print(f"Created stealth cache folder: {subfolder}")
            
            # Create a .nomedia file to hide from media scanners
            nomedia_path = os.path.join(dir_path, '.nomedia')
            open(nomedia_path, 'a').close()
            
except Exception as e:
    print(f"Warning: Could not create data directories - {str(e)}")

# Move files to appropriate directories
file_moves = {
    'agent.py': 'src/voice/agent.py',
    'enhanced_voice_agent.py': 'src/voice/enhanced_voice_agent.py',
    'voice_to_text.py': 'src/voice/voice_to_text.py',
    'scraper.py': 'src/scrapers/scraper.py',
    'sports_scraper.py': 'src/scrapers/sports_scraper.py',
    '.env': 'src/config/.env'
}

for source, dest in file_moves.items():
    if os.path.exists(source):
        dest_path = os.path.join(os.getcwd(), dest)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            os.rename(source, dest_path)
            print(f"Moved {source} to {dest}")
        except Exception as e:
            print(f"Error moving {source}: {e}")

print("\nDirectory setup complete!")
print("\nData Storage Structure:")
print(f"{DATA_ROOT}/System/")
print("├── Cache/")
print("│   └── sys_[timestamp]_[random]/")
print("├── Backup/")
print("├── Archive/")
print("└── Temp/")

# Create a config file with storage location
config_path = os.path.join(os.getcwd(), 'src', 'config', 'storage.json')
config = {
    'data_root': DATA_ROOT,
    'cache_dir': os.path.join(DATA_ROOT, 'System', 'Cache'),
    'backup_dir': os.path.join(DATA_ROOT, 'System', 'Backup'),
    'archive_dir': os.path.join(DATA_ROOT, 'System', 'Archive'),
    'temp_dir': os.path.join(DATA_ROOT, 'System', 'Temp')
}

with open(config_path, 'w') as f:
    import json
    json.dump(config, f, indent=4)
