import os
import sys
import json
import shutil
import psutil
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import concurrent.futures

class SystemManager:
    """Manages system resources, upgrades, and scalability"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.config_path = base_path / "config"
        self.system_config = self._load_system_config()
        self.resource_limits = {
            "cpu_percent": 80,
            "memory_percent": 75,
            "disk_percent": 85
        }
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.system_config.get("max_threads", 4)
        )
        self.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.system_config.get("max_processes", 2)
        )
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup system logging"""
        log_dir = self.base_path / "logs" / "system"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "system.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SystemManager")
    
    def _load_system_config(self) -> Dict:
        """Load system configuration"""
        config_file = self.config_path / "system_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default system configuration"""
        config = {
            "version": "1.0.0",
            "max_threads": 4,
            "max_processes": 2,
            "auto_upgrade": True,
            "resource_monitoring": True,
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "log_retention_days": 7,
            "performance_mode": "balanced",
            "scaling_rules": {
                "cpu_threshold": 80,
                "memory_threshold": 75,
                "auto_scale": True,
                "scale_up_increment": 1,
                "scale_down_increment": 1,
                "min_instances": 1,
                "max_instances": 4
            }
        }
        
        self.config_path.mkdir(parents=True, exist_ok=True)
        with open(self.config_path / "system_config.json", 'w') as f:
            json.dump(config, f, indent=4)
        
        return config
    
    def check_system_resources(self) -> Dict:
        """Monitor system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = {
                "cpu": {
                    "percent": cpu_percent,
                    "warning": cpu_percent > self.resource_limits["cpu_percent"]
                },
                "memory": {
                    "percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "warning": memory.percent > self.resource_limits["memory_percent"]
                },
                "disk": {
                    "percent": disk.percent,
                    "free_gb": disk.free / (1024**3),
                    "warning": disk.percent > self.resource_limits["disk_percent"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Log warnings
            for resource, data in status.items():
                if isinstance(data, dict) and data.get("warning"):
                    self.logger.warning(f"High {resource} usage: {data['percent']}%")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error checking system resources: {str(e)}")
            return {}
    
    def scale_resources(self, resource_status: Dict):
        """Scale system resources based on usage"""
        try:
            rules = self.system_config["scaling_rules"]
            if not rules["auto_scale"]:
                return
                
            current_processes = len(self.process_pool._processes)
            
            # Scale up
            if (resource_status["cpu"]["percent"] > rules["cpu_threshold"] or 
                resource_status["memory"]["percent"] > rules["memory_threshold"]):
                if current_processes < rules["max_instances"]:
                    new_processes = min(
                        current_processes + rules["scale_up_increment"],
                        rules["max_instances"]
                    )
                    self._resize_process_pool(new_processes)
                    self.logger.info(f"Scaled up to {new_processes} processes")
            
            # Scale down
            elif (resource_status["cpu"]["percent"] < rules["cpu_threshold"] * 0.7 and 
                  resource_status["memory"]["percent"] < rules["memory_threshold"] * 0.7):
                if current_processes > rules["min_instances"]:
                    new_processes = max(
                        current_processes - rules["scale_down_increment"],
                        rules["min_instances"]
                    )
                    self._resize_process_pool(new_processes)
                    self.logger.info(f"Scaled down to {new_processes} processes")
                    
        except Exception as e:
            self.logger.error(f"Error scaling resources: {str(e)}")
    
    def _resize_process_pool(self, new_size: int):
        """Resize the process pool"""
        self.process_pool.shutdown(wait=True)
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=new_size)
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check for system updates"""
        try:
            # Simulate checking for updates
            # In production, this would connect to an update server
            updates = {
                "available": True,
                "version": "1.1.0",
                "changes": [
                    "Improved ML model performance",
                    "Enhanced resource management",
                    "New analysis features"
                ],
                "priority": "high",
                "size_mb": 25.5
            }
            
            if updates["available"]:
                self.logger.info(f"Update available: version {updates['version']}")
            
            return updates
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            return None
    
    def perform_upgrade(self, version: str) -> bool:
        """Perform system upgrade"""
        try:
            self.logger.info(f"Starting upgrade to version {version}")
            
            # Backup current system
            backup_path = self._create_backup()
            if not backup_path:
                return False
            
            # Simulate upgrade process
            # In production, this would download and apply updates
            success = True  # Simulate successful upgrade
            
            if success:
                self.system_config["version"] = version
                with open(self.config_path / "system_config.json", 'w') as f:
                    json.dump(self.system_config, f, indent=4)
                self.logger.info(f"Successfully upgraded to version {version}")
                return True
            else:
                self._restore_backup(backup_path)
                return False
                
        except Exception as e:
            self.logger.error(f"Error during upgrade: {str(e)}")
            return False
    
    def _create_backup(self) -> Optional[Path]:
        """Create system backup"""
        try:
            backup_dir = self.base_path / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"
            
            # Copy system files
            shutil.copytree(self.base_path / "src", backup_path / "src")
            shutil.copytree(self.base_path / "config", backup_path / "config")
            
            self.logger.info(f"Created backup at {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            return None
    
    def _restore_backup(self, backup_path: Path) -> bool:
        """Restore from backup"""
        try:
            # Restore system files
            shutil.rmtree(self.base_path / "src")
            shutil.rmtree(self.base_path / "config")
            shutil.copytree(backup_path / "src", self.base_path / "src")
            shutil.copytree(backup_path / "config", self.base_path / "config")
            
            self.logger.info(f"Restored backup from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}")
            return False
    
    def optimize_performance(self, mode: str = "balanced"):
        """Optimize system performance"""
        try:
            modes = {
                "power_save": {
                    "max_threads": 2,
                    "max_processes": 1,
                    "cpu_threshold": 60,
                    "memory_threshold": 60
                },
                "balanced": {
                    "max_threads": 4,
                    "max_processes": 2,
                    "cpu_threshold": 80,
                    "memory_threshold": 75
                },
                "performance": {
                    "max_threads": 8,
                    "max_processes": 4,
                    "cpu_threshold": 90,
                    "memory_threshold": 85
                }
            }
            
            if mode not in modes:
                raise ValueError(f"Invalid performance mode: {mode}")
            
            settings = modes[mode]
            self.system_config["performance_mode"] = mode
            self.system_config["max_threads"] = settings["max_threads"]
            self.system_config["max_processes"] = settings["max_processes"]
            self.system_config["scaling_rules"]["cpu_threshold"] = settings["cpu_threshold"]
            self.system_config["scaling_rules"]["memory_threshold"] = settings["memory_threshold"]
            
            # Apply new settings
            self._resize_process_pool(settings["max_processes"])
            self.thread_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=settings["max_threads"]
            )
            
            with open(self.config_path / "system_config.json", 'w') as f:
                json.dump(self.system_config, f, indent=4)
                
            self.logger.info(f"Applied {mode} performance mode")
            
        except Exception as e:
            self.logger.error(f"Error optimizing performance: {str(e)}")
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        try:
            resources = self.check_system_resources()
            updates = self.check_for_updates()
            
            return {
                "version": self.system_config["version"],
                "performance_mode": self.system_config["performance_mode"],
                "resources": resources,
                "updates": updates,
                "processes": len(self.process_pool._processes),
                "threads": self.thread_pool._max_workers,
                "config": self.system_config,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {}
