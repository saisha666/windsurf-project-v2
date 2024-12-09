import os
import shutil
from datetime import datetime
import json

def create_backup():
    # Source directories
    project_dir = os.getcwd()
    try:
        with open(os.path.join(project_dir, 'src', 'config', 'storage.json'), 'r', encoding='utf-8') as f:
            storage_config = json.load(f)
        data_dir = storage_config['data_root']
    except:
        print("Warning: Could not load storage config")
        data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'RouletteData')

    # Create backup timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup destination
    backup_root = "C:/Users/shaonsai/CascadeProjects/windsurf-project/backup"
    backup_dir = os.path.join(backup_root, f"backup_{timestamp}")
    
    try:
        # Create backup directories
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "project"), exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "data"), exist_ok=True)
        
        print("\nBacking up project files...")
        shutil.copytree(
            project_dir, 
            os.path.join(backup_dir, "project", "windsurf-project"),
            ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git', '.venv', 'backup_*'),
            dirs_exist_ok=True
        )
        
        print("Backing up data files...")
        if os.path.exists(data_dir):
            shutil.copytree(
                data_dir,
                os.path.join(backup_dir, "data", "RouletteData"),
                ignore=shutil.ignore_patterns('*.tmp'),
                dirs_exist_ok=True
            )
        
        # Create backup info file
        info = {
            "backup_time": timestamp,
            "project_source": project_dir,
            "data_source": data_dir,
            "contents": {
                "project": os.listdir(os.path.join(backup_dir, "project")),
                "data": os.listdir(os.path.join(backup_dir, "data")) if os.path.exists(data_dir) else []
            }
        }
        
        with open(os.path.join(backup_dir, "backup_info.json"), 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=4)
            
        print(f"\nBackup completed successfully!")
        print(f"Location: {backup_dir}")
        print("\nBackup structure:")
        print("backup_" + timestamp + "/")
        print("  |-- project/")
        print("  |     |-- windsurf-project/")
        print("  |-- data/")
        print("  |     |-- RouletteData/")
        print("  |-- backup_info.json")
        
    except Exception as e:
        print(f"\nError during backup: {str(e)}")
        print("Please ensure you have write permissions to the backup location.")

if __name__ == "__main__":
    create_backup()
