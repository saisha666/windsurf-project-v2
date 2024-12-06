##c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.py:103: SyntaxWarning: invalid escape sequence '
cmd = "top -bn1 | grep 'Cpu\|Mem'"
Traceback (most recent call last):
  File "c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.rpy2", line 1, in <module>
    import rpy2.robjects as robjects
ModuleNotFoundError: No module named 'rpy2'
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
import pandas as pd
import numpy as np
from subprocess import run, PIPE
import platform
import json
import os

class RTrainingController:
    def __init__(self):
        # Initialize R interface
        self.r = robjects.r
        pandas2ri.activate()
        
        # Import required R packages
        self.stats = importr('stats')
        self.base = importr('base')
        self.tidyverse = importr('tidyverse')
        
        # System configurations
        self.systems = {
            'ubuntu': {'ip': '192.168.20.7', 'port': 3389},
            'windows': {'ip': '192.168.20.11', 'port': 3389}
        }
        
        # Training parameters
        self.training_config = {
            'iterations': 1000,
            'learning_rate': 0.01,
            'batch_size': 32
        }

    def install_r_packages(self, packages):
        """Install required R packages."""
        utils = importr('utils')
        for package in packages:
            try:
                utils.install_packages(package)
                print(f"Successfully installed {package}")
            except Exception as e:
                print(f"Error installing {package}: {str(e)}")

    def load_data(self, filepath, type='csv'):
        """Load data from various formats."""
        try:
            if type == 'csv':
                data = pd.read_csv(filepath)
            elif type == 'excel':
                data = pd.read_excel(filepath)
            elif type == 'json':
                data = pd.read_json(filepath)
            else:
                raise ValueError("Unsupported file type")
            
            return pandas2ri.py2rpy(data)
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None

    def train_model(self, data, model_type='linear'):
        """Train various types of models."""
        try:
            if model_type == 'linear':
                model = self.stats.lm('y ~ x', data=data)
            elif model_type == 'logistic':
                model = self.stats.glm('y ~ x', family='binomial', data=data)
            elif model_type == 'random_forest':
                randomForest = importr('randomForest')
                model = randomForest.randomForest(robjects.Formula('y ~ .'), data=data)
            
            return model
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return None

    def execute_r_script(self, script_path):
        """Execute an R script file."""
        try:
            result = self.r.source(script_path)
            return result
        except Exception as e:
            print(f"Error executing R script: {str(e)}")
            return None

    def system_command(self, system, command):
        """Execute system commands on target machines."""
        if system == 'ubuntu':
            # SSH command execution
            ssh_cmd = f"ssh user@{self.systems['ubuntu']['ip']} '{command}'"
            result = run(ssh_cmd, shell=True, stdout=PIPE, stderr=PIPE)
            return result.stdout.decode()
        elif system == 'windows':
            # PowerShell remote command execution
            ps_cmd = f"Invoke-Command -ComputerName {self.systems['windows']['ip']} -ScriptBlock {{ {command} }}"
            result = run(['powershell', '-Command', ps_cmd], stdout=PIPE, stderr=PIPE)
            return result.stdout.decode()

    def monitor_resources(self, system):
        """Monitor system resources."""
        if system == 'ubuntu':
            cmd = "top -bn1 | grep 'Cpu\|Mem'"
        else:
            cmd = "Get-Counter '\\Processor(_Total)\\% Processor Time','\\Memory\\Available MBytes'"
        
        return self.system_command(system, cmd)

    def control_training(self, data_path, model_config):
        """Control and monitor training process."""
        # Load data
        data = self.load_data(data_path)
        if data is None:
            return False

        # Configure training
        self.training_config.update(model_config)

        # Monitor system resources
        ubuntu_resources = self.monitor_resources('ubuntu')
        windows_resources = self.monitor_resources('windows')

        # Train model
        model = self.train_model(data, model_config.get('model_type', 'linear'))
        if model is None:
            return False

        # Save results
        results = {
            'model': str(model),
            'ubuntu_resources': ubuntu_resources,
            'windows_resources': windows_resources,
            'training_config': self.training_config
        }

        with open('training_results.json', 'w') as f:
            json.dump(results, f, indent=4)

        return True

    def optimize_system(self, system):
        """Optimize system for R training."""
        if system == 'ubuntu':
            commands = [
                "sudo apt-get clean",
                "sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches",
                "sudo swapoff -a && sudo swapon -a"
            ]
        else:
            commands = [
                "Stop-Service -Name 'SysMain' -Force",
                "Clear-RecycleBin -Force",
                "Remove-Item -Path '$env:TEMP\\*' -Recurse -Force"
            ]

        for cmd in commands:
            self.system_command(system, cmd)

def main():
    # Initialize controller
    controller = RTrainingController()

    # Example usage
    required_packages = ['tidyverse', 'randomForest', 'caret']
    controller.install_r_packages(required_packages)

    # Optimize systems
    controller.optimize_system('ubuntu')
    controller.optimize_system('windows')

    # Training configuration
    model_config = {
        'model_type': 'random_forest',
        'iterations': 2000,
        'learning_rate': 0.005
    }

    # Start training
    success = controller.control_training('data/training_data.csv', model_config)
    
    if success:
        print("Training completed successfully!")
        # Execute post-training R script
        controller.execute_r_script('scripts/post_training_analysis.R')
    else:
        print("Training failed!")

if __name__ == "__main__":
    main()
