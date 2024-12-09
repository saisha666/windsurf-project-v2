import os
import json
import shutil
from pathlib import Path
import logging
from typing import Dict, List, Optional

class InstallationManager:
    """Manages multiple installations of the AI OS system across different drives"""
    
    def __init__(self):
        self.installations = {}
        self.config_file = "installation_config.json"
        self.required_dirs = [
            "bin",
            "config",
            "data/database",
            "data/models",
            "logs",
            "src"
        ]
        
    def add_installation(self, drive: str, name: str, is_primary: bool = False) -> bool:
        """Add a new installation location"""
        base_path = Path(f"{drive}:/AI_OS")
        
        try:
            # Create installation directory structure
            for dir_path in self.required_dirs:
                full_path = base_path / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
            
            # Create installation config
            installation_config = {
                "name": name,
                "drive": drive,
                "base_path": str(base_path),
                "is_primary": is_primary,
                "status": "active",
                "sync_enabled": True,
                "created_at": str(Path(base_path).stat().st_ctime)
            }
            
            self.installations[drive] = installation_config
            self._save_config()
            
            logging.info(f"Added new installation on drive {drive}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add installation on drive {drive}: {str(e)}")
            return False
    
    def sync_installations(self, source_drive: str, target_drive: str, 
                         sync_data: bool = True, sync_models: bool = True,
                         sync_config: bool = True) -> bool:
        """Synchronize data between installations"""
        try:
            source = Path(f"{source_drive}:/AI_OS")
            target = Path(f"{target_drive}:/AI_OS")
            
            if sync_data:
                self._sync_directory(source / "data/database", 
                                   target / "data/database")
            
            if sync_models:
                self._sync_directory(source / "data/models", 
                                   target / "data/models")
            
            if sync_config:
                self._sync_directory(source / "config", 
                                   target / "config")
            
            logging.info(f"Synchronized installations between {source_drive} and {target_drive}")
            return True
            
        except Exception as e:
            logging.error(f"Sync failed: {str(e)}")
            return False
    
    def _sync_directory(self, source: Path, target: Path):
        """Synchronize contents of two directories"""
        if not source.exists():
            return
            
        target.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        for item in source.glob('*'):
            if item.is_file():
                shutil.copy2(item, target / item.name)
            elif item.is_dir():
                self._sync_directory(item, target / item.name)
    
    def get_installation_info(self, drive: str) -> Optional[Dict]:
        """Get information about a specific installation"""
        return self.installations.get(drive)
    
    def list_installations(self) -> List[Dict]:
        """List all registered installations"""
        return list(self.installations.values())
    
    def set_primary_installation(self, drive: str) -> bool:
        """Set an installation as primary"""
        if drive not in self.installations:
            return False
            
        for d, config in self.installations.items():
            config["is_primary"] = (d == drive)
        
        self._save_config()
        return True
    
    def _save_config(self):
        """Save installation configurations to file"""
        config_path = Path("config") / self.config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.installations, f, indent=4)
    
    def _load_config(self):
        """Load installation configurations from file"""
        config_path = Path("config") / self.config_file
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.installations = json.load(f)
    
    def validate_installation(self, drive: str) -> Dict:
        """Validate an installation's directory structure and files"""
        base_path = Path(f"{drive}:/AI_OS")
        validation = {
            "exists": base_path.exists(),
            "directories": {},
            "permissions": {},
            "space_available": shutil.disk_usage(drive + ":/").free
        }
        
        if validation["exists"]:
            for dir_path in self.required_dirs:
                full_path = base_path / dir_path
                validation["directories"][dir_path] = full_path.exists()
                try:
                    # Test write permission
                    test_file = full_path / ".test"
                    test_file.touch()
                    test_file.unlink()
                    validation["permissions"][dir_path] = True
                except:
                    validation["permissions"][dir_path] = False
        
        return validation
