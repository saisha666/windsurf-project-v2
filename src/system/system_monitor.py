import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import json
import numpy as np
from collections import deque

class SystemMonitor:
    """Monitors system performance and handles scaling decisions"""
    
    def __init__(self, system_manager, base_path: Path):
        self.system_manager = system_manager
        self.base_path = base_path
        self.monitoring = False
        self.metrics_history = {
            "cpu": deque(maxlen=60),  # Last 60 readings
            "memory": deque(maxlen=60),
            "disk": deque(maxlen=60)
        }
        self.performance_stats = {
            "cpu_avg": 0,
            "memory_avg": 0,
            "disk_avg": 0,
            "scaling_events": 0,
            "last_scale_time": None
        }
        self.alert_thresholds = {
            "cpu_sustained": 85,
            "memory_sustained": 80,
            "disk_sustained": 90,
            "sustained_duration": 300  # 5 minutes
        }
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup monitoring logging"""
        log_dir = self.base_path / "logs" / "monitoring"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("SystemMonitor")
        handler = logging.FileHandler(log_dir / "monitoring.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def start_monitoring(self, interval: int = 60):
        """Start system monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get current system status
                status = self.system_manager.check_system_resources()
                
                # Update metrics history
                self._update_metrics(status)
                
                # Check for sustained high usage
                self._check_sustained_usage()
                
                # Update performance stats
                self._update_performance_stats()
                
                # Save monitoring data
                self._save_monitoring_data()
                
                # Sleep for the specified interval
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(interval)
    
    def _update_metrics(self, status: Dict):
        """Update metrics history"""
        try:
            self.metrics_history["cpu"].append(status["cpu"]["percent"])
            self.metrics_history["memory"].append(status["memory"]["percent"])
            self.metrics_history["disk"].append(status["disk"]["percent"])
        except Exception as e:
            self.logger.error(f"Error updating metrics: {str(e)}")
    
    def _check_sustained_usage(self):
        """Check for sustained high resource usage"""
        try:
            # Calculate moving averages
            if len(self.metrics_history["cpu"]) >= 5:  # At least 5 readings
                cpu_avg = np.mean(list(self.metrics_history["cpu"])[-5:])
                memory_avg = np.mean(list(self.metrics_history["memory"])[-5:])
                disk_avg = np.mean(list(self.metrics_history["disk"])[-5:])
                
                # Check thresholds
                if (cpu_avg > self.alert_thresholds["cpu_sustained"] or
                    memory_avg > self.alert_thresholds["memory_sustained"] or
                    disk_avg > self.alert_thresholds["disk_sustained"]):
                    
                    self.logger.warning(
                        f"Sustained high usage detected - CPU: {cpu_avg:.1f}%, "
                        f"Memory: {memory_avg:.1f}%, Disk: {disk_avg:.1f}%"
                    )
                    
                    # Trigger scaling if needed
                    self._handle_scaling_decision({
                        "cpu": cpu_avg,
                        "memory": memory_avg,
                        "disk": disk_avg
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking sustained usage: {str(e)}")
    
    def _handle_scaling_decision(self, metrics: Dict):
        """Handle resource scaling decisions"""
        try:
            # Check if enough time has passed since last scaling
            if (self.performance_stats["last_scale_time"] is None or
                (datetime.now() - self.performance_stats["last_scale_time"]) > 
                timedelta(minutes=5)):
                
                # Trigger scaling
                self.system_manager.scale_resources({
                    "cpu": {"percent": metrics["cpu"]},
                    "memory": {"percent": metrics["memory"]},
                    "disk": {"percent": metrics["disk"]}
                })
                
                self.performance_stats["scaling_events"] += 1
                self.performance_stats["last_scale_time"] = datetime.now()
                
                self.logger.info("Triggered resource scaling")
                
        except Exception as e:
            self.logger.error(f"Error handling scaling decision: {str(e)}")
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        try:
            if self.metrics_history["cpu"]:
                self.performance_stats.update({
                    "cpu_avg": np.mean(self.metrics_history["cpu"]),
                    "memory_avg": np.mean(self.metrics_history["memory"]),
                    "disk_avg": np.mean(self.metrics_history["disk"])
                })
        except Exception as e:
            self.logger.error(f"Error updating performance stats: {str(e)}")
    
    def _save_monitoring_data(self):
        """Save monitoring data to file"""
        try:
            data_dir = self.base_path / "data" / "monitoring"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create monitoring data
            monitoring_data = {
                "timestamp": datetime.now().isoformat(),
                "metrics_history": {
                    "cpu": list(self.metrics_history["cpu"]),
                    "memory": list(self.metrics_history["memory"]),
                    "disk": list(self.metrics_history["disk"])
                },
                "performance_stats": self.performance_stats,
                "scaling_events": self.performance_stats["scaling_events"]
            }
            
            # Save to daily file
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = data_dir / f"monitoring_{date_str}.json"
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
                existing_data["data"].append(monitoring_data)
                data_to_save = existing_data
            else:
                data_to_save = {
                    "date": date_str,
                    "data": [monitoring_data]
                }
            
            with open(file_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
                
        except Exception as e:
            self.logger.error(f"Error saving monitoring data: {str(e)}")
    
    def get_performance_report(self, time_range: Optional[str] = "1h") -> Dict:
        """Generate performance report"""
        try:
            time_ranges = {
                "1h": 60,
                "6h": 360,
                "12h": 720,
                "24h": 1440
            }
            
            if time_range not in time_ranges:
                raise ValueError(f"Invalid time range: {time_range}")
            
            # Calculate statistics
            readings = time_ranges[time_range]
            cpu_data = list(self.metrics_history["cpu"])[-readings:]
            memory_data = list(self.metrics_history["memory"])[-readings:]
            disk_data = list(self.metrics_history["disk"])[-readings:]
            
            report = {
                "time_range": time_range,
                "cpu": {
                    "current": cpu_data[-1] if cpu_data else 0,
                    "average": np.mean(cpu_data) if cpu_data else 0,
                    "max": np.max(cpu_data) if cpu_data else 0,
                    "min": np.min(cpu_data) if cpu_data else 0
                },
                "memory": {
                    "current": memory_data[-1] if memory_data else 0,
                    "average": np.mean(memory_data) if memory_data else 0,
                    "max": np.max(memory_data) if memory_data else 0,
                    "min": np.min(memory_data) if memory_data else 0
                },
                "disk": {
                    "current": disk_data[-1] if disk_data else 0,
                    "average": np.mean(disk_data) if disk_data else 0,
                    "max": np.max(disk_data) if disk_data else 0,
                    "min": np.min(disk_data) if disk_data else 0
                },
                "scaling_events": self.performance_stats["scaling_events"],
                "generated_at": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {}
