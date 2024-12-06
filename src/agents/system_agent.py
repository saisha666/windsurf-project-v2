import os
import json
import glob
import shutil
import psutil
import pyautogui
import webbrowser
import subprocess
from datetime import datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import logging
from pathlib import Path

class SystemAgent:
    def __init__(self):
        self.setup_logging()
        self.setup_ai()
        self.command_history = []
        self.research_cache = {}
        self.file_index = {}
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path.home() / 'AppData' / 'Local' / 'AI_OS' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'system_agent_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def setup_ai(self):
        """Initialize AI models"""
        try:
            # Text understanding model
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
            self.model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")
            
            # Text generation
            self.generator = pipeline('text-generation', model='gpt2')
            
            # Text classification
            self.classifier = pipeline('sentiment-analysis')
            
        except Exception as e:
            logging.error(f"Error setting up AI models: {str(e)}")
            
    def index_files(self, directory):
        """Index all files in a directory for quick search"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    path = os.path.join(root, file)
                    try:
                        if file.endswith(('.txt', '.py', '.md', '.json')):
                            with open(path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Create embeddings for content
                                inputs = self.tokenizer(content, return_tensors="pt", 
                                                      max_length=512, truncation=True)
                                with torch.no_grad():
                                    embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
                                self.file_index[path] = {
                                    'content': content,
                                    'embeddings': embeddings,
                                    'modified': os.path.getmtime(path)
                                }
                    except Exception as e:
                        logging.error(f"Error indexing file {path}: {str(e)}")
                        
        except Exception as e:
            logging.error(f"Error walking directory {directory}: {str(e)}")

    def search_files(self, query):
        """Search indexed files using semantic similarity"""
        try:
            # Create query embedding
            inputs = self.tokenizer(query, return_tensors="pt", 
                                  max_length=512, truncation=True)
            with torch.no_grad():
                query_embedding = self.model(**inputs).last_hidden_state.mean(dim=1)

            # Calculate similarities
            results = []
            for path, data in self.file_index.items():
                similarity = torch.nn.functional.cosine_similarity(
                    query_embedding, data['embeddings']
                ).item()
                results.append((path, similarity))

            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:5]  # Return top 5 results
            
        except Exception as e:
            logging.error(f"Error searching files: {str(e)}")
            return []

    def analyze_project(self, project_dir):
        """Analyze a project directory"""
        try:
            analysis = {
                'structure': self.analyze_structure(project_dir),
                'dependencies': self.analyze_dependencies(project_dir),
                'complexity': self.analyze_complexity(project_dir),
                'patterns': self.analyze_patterns(project_dir)
            }
            return analysis
        except Exception as e:
            logging.error(f"Error analyzing project: {str(e)}")
            return None

    def analyze_structure(self, directory):
        """Analyze project structure"""
        structure = {'directories': [], 'files': []}
        try:
            for root, dirs, files in os.walk(directory):
                rel_path = os.path.relpath(root, directory)
                structure['directories'].append(rel_path)
                for file in files:
                    structure['files'].append(os.path.join(rel_path, file))
        except Exception as e:
            logging.error(f"Error analyzing structure: {str(e)}")
        return structure

    def analyze_dependencies(self, directory):
        """Analyze project dependencies"""
        dependencies = set()
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file == 'requirements.txt':
                        with open(os.path.join(root, file), 'r') as f:
                            for line in f:
                                if line.strip() and not line.startswith('#'):
                                    dependencies.add(line.strip())
        except Exception as e:
            logging.error(f"Error analyzing dependencies: {str(e)}")
        return list(dependencies)

    def analyze_complexity(self, directory):
        """Analyze code complexity"""
        complexity = {'files': 0, 'lines': 0, 'functions': 0, 'classes': 0}
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            complexity['files'] += 1
                            complexity['lines'] += len(content.splitlines())
                            complexity['functions'] += content.count('def ')
                            complexity['classes'] += content.count('class ')
        except Exception as e:
            logging.error(f"Error analyzing complexity: {str(e)}")
        return complexity

    def analyze_patterns(self, directory):
        """Analyze code patterns"""
        patterns = {}
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            # Analyze imports
                            imports = [line for line in content.splitlines() 
                                     if line.strip().startswith(('import ', 'from '))]
                            patterns[file] = {
                                'imports': imports,
                                'async': 'async ' in content,
                                'classes': content.count('class '),
                                'functions': content.count('def ')
                            }
        except Exception as e:
            logging.error(f"Error analyzing patterns: {str(e)}")
        return patterns

    def research_topic(self, topic, max_results=5):
        """Research a topic online"""
        try:
            # Check cache first
            if topic in self.research_cache:
                return self.research_cache[topic]

            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            
            results = []
            
            # Search using DuckDuckGo
            url = f"https://duckduckgo.com/html/?q={topic}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            for result in soup.find_all('div', {'class': 'result'}):
                if len(results) >= max_results:
                    break
                    
                title = result.find('a', {'class': 'result__a'})
                link = title.get('href') if title else None
                snippet = result.find('a', {'class': 'result__snippet'})
                
                if title and link and snippet:
                    results.append({
                        'title': title.text,
                        'url': link,
                        'snippet': snippet.text
                    })
            
            # Cache results
            self.research_cache[topic] = results
            return results
            
        except Exception as e:
            logging.error(f"Error researching topic: {str(e)}")
            return []

    def system_control(self, command):
        """Control system operations"""
        try:
            if command.startswith('open '):
                app = command[5:]
                subprocess.Popen(app)
                return f"Opened {app}"
                
            elif command.startswith('close '):
                app = command[6:]
                os.system(f"taskkill /f /im {app}")
                return f"Closed {app}"
                
            elif command == 'system info':
                info = {
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent
                }
                return info
                
            elif command.startswith('browse '):
                url = command[7:]
                webbrowser.open(url)
                return f"Opened {url} in browser"
                
            else:
                return "Unknown command"
                
        except Exception as e:
            logging.error(f"Error in system control: {str(e)}")
            return f"Error: {str(e)}"

    def process_command(self, command):
        """Process user command"""
        try:
            # Log command
            self.command_history.append({
                'timestamp': datetime.now().isoformat(),
                'command': command
            })
            
            # Analyze command intent
            if 'search' in command or 'find' in command:
                query = command.replace('search', '').replace('find', '').strip()
                return self.search_files(query)
                
            elif 'analyze' in command:
                path = command.replace('analyze', '').strip()
                return self.analyze_project(path)
                
            elif 'research' in command:
                topic = command.replace('research', '').strip()
                return self.research_topic(topic)
                
            elif any(cmd in command for cmd in ['open', 'close', 'system', 'browse']):
                return self.system_control(command)
                
            else:
                return "I don't understand that command"
                
        except Exception as e:
            logging.error(f"Error processing command: {str(e)}")
            return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test the system agent
    agent = SystemAgent()
    
    # Index current directory
    print("Indexing files...")
    agent.index_files(os.getcwd())
    
    # Process some test commands
    test_commands = [
        "analyze .",
        "search python files",
        "research machine learning",
        "system info"
    ]
    
    for cmd in test_commands:
        print(f"\nProcessing command: {cmd}")
        result = agent.process_command(cmd)
        print(f"Result: {result}")
