import cv2
import numpy as np
import mss
import time
import sqlite3
import json
from datetime import datetime
import os
import easyocr
from PIL import Image
import keyboard
import random
import psutil
import hashlib

class DataCrypto:
    def __init__(self):
        self.key = 123  # Replace with a secure key

    def encode_number(self, number):
        return str(number + self.key)

    def decode_number(self, encoded_number):
        try:
            return int(encoded_number) - self.key
        except ValueError:
            return None

class AutoRouletteCollector:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.sct = mss.mss()
        self.numbers = set(range(37))  # Valid roulette numbers 0-36
        self.setup_database()
        self.last_number = None
        self.consecutive_same = 0
        self.monitor = self.get_primary_monitor()
        self.crypto = DataCrypto()  # Initialize crypto

    def get_primary_monitor(self):
        """Get the primary monitor dimensions"""
        return self.sct.monitors[1]  # Primary monitor

    def setup_database(self):
        """Setup SQLite database with enhanced tracking"""
        try:
            db_folder = "Q:\\Data\\System\\Cache"
            os.makedirs(db_folder, exist_ok=True)
            
            subfolder = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
            full_path = os.path.join(db_folder, subfolder)
            os.makedirs(full_path, exist_ok=True)
            
            filename = f"sys_{int(time.time())}_{random.randint(1000,9999)}.dat"
            self.db_path = os.path.join(full_path, filename)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enhanced table structure
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sys_cache (
                ts TEXT,              -- Timestamp
                val TEXT,             -- Encrypted number
                rid TEXT,             -- Encrypted roulette ID
                pid TEXT,             -- Encrypted provider ID
                sid TEXT,             -- Encrypted session ID
                spin_time INTEGER,    -- Spin duration in ms
                c1 TEXT, c2 TEXT, c3 TEXT, c4 TEXT, c5 TEXT,  -- Categories
                meta TEXT            -- Encrypted metadata
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sys_log (
                ts TEXT,
                t TEXT,
                d TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            pass

    def get_number_category(self, number):
        """Categorize a roulette number"""
        if number == 0:
            return 'green', 'zero', 'zero', 'zero', 'zero'

        # Color
        red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        color = 'red' if number in red_numbers else 'black'

        # Odd/Even
        odd_even = 'odd' if number % 2 else 'even'

        # Dozen
        if number <= 12:
            dozen = 'first'
        elif number <= 24:
            dozen = 'second'
        else:
            dozen = 'third'

        # Column
        column = f"col{(number - 1) % 3 + 1}"

        # High/Low
        high_low = 'high' if number >= 19 else 'low'

        return color, odd_even, dozen, column, high_low

    def save_number(self, number, roulette_id, provider_id, spin_time, metadata=None):
        """Save a detected number with enhanced tracking"""
        if number not in self.numbers:
            return False
            
        try:
            if number == self.last_number:
                self.consecutive_same += 1
                if self.consecutive_same > 2:
                    return False
            else:
                self.consecutive_same = 0
                self.last_number = number
                
            # Encode all sensitive data
            encoded_number = self.crypto.encode_number(number)
            encoded_rid = self.crypto.encode_number(hash(str(roulette_id)))
            encoded_pid = self.crypto.encode_number(hash(str(provider_id)))
            session_id = f"{int(time.time())}_{random.randint(1000,9999)}"
            encoded_sid = self.crypto.encode_number(hash(session_id))
            
            # Encode metadata if provided
            encoded_meta = None
            if metadata:
                encoded_meta = self.crypto.encode_number(hash(str(metadata)))
            
            cats = self.get_number_category(number)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO sys_cache (ts, val, rid, pid, sid, spin_time, c1, c2, c3, c4, c5, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                encoded_number,
                encoded_rid,
                encoded_pid,
                encoded_sid,
                spin_time,
                *cats,
                encoded_meta
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            return False

    def validate_number(self, number, roulette_id, provider_id, spin_time):
        """Enhanced number validation with provider checks"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check provider history
            encoded_pid = self.crypto.encode_number(hash(str(provider_id)))
            cursor.execute('SELECT val, spin_time FROM sys_cache WHERE pid = ? ORDER BY ts DESC LIMIT 10', (encoded_pid,))
            provider_history = cursor.fetchall()
            
            if provider_history:
                # Check spin time consistency
                avg_spin_time = sum(r[1] for r in provider_history) / len(provider_history)
                if abs(spin_time - avg_spin_time) > 1000:  # More than 1 second difference
                    return False
                
                # Check for impossible sequences on this provider
                recent_numbers = [self.crypto.decode_number(r[0]) for r in provider_history if r[0]]
                if len(recent_numbers) >= 3:
                    if recent_numbers[0] == number and recent_numbers[1] == number:
                        return False  # Three identical in a row on same provider
            
            # Check roulette table history
            encoded_rid = self.crypto.encode_number(hash(str(roulette_id)))
            cursor.execute('SELECT val FROM sys_cache WHERE rid = ? ORDER BY ts DESC LIMIT 20', (encoded_rid,))
            table_history = cursor.fetchall()
            
            if table_history:
                decoded = [self.crypto.decode_number(r[0]) for r in table_history if r[0]]
                if decoded.count(number) >= 4:  # More than 4 occurrences in last 20
                    return False
            
            conn.close()
            return True
            
        except Exception as e:
            return True  # Continue on error

    def detect_number(self, image):
        """Detect number from image using OCR"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply thresholding
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            # OCR
            results = self.reader.readtext(thresh)

            for (_, text, conf) in results:
                # Try to convert to number
                try:
                    num = int(text)
                    if num in self.numbers:
                        return num
                except ValueError:
                    continue

        except Exception as e:
            print(f"Error in detection: {e}")

        return None

    def capture_screen(self):
        """Capture screen area"""
        # Capture the middle portion of the screen
        width = self.monitor["width"]
        height = self.monitor["height"]

        # Define capture region (middle portion of screen)
        region = {
            "top": height // 4,
            "left": width // 4,
            "width": width // 2,
            "height": height // 2
        }

        # Capture
        screenshot = np.array(self.sct.grab(region))
        return screenshot

    def check_network_activity(self):
        """Monitor network patterns for suspicious activity"""
        try:
            net_counters = psutil.net_io_counters()
            
            # Check for high network activity
            bytes_sent = net_counters.bytes_sent
            bytes_recv = net_counters.bytes_recv
            
            # Get network connections
            connections = psutil.net_connections()
            established_conns = len([c for c in connections if c.status == 'ESTABLISHED'])
            
            # Thresholds for suspicion
            if established_conns > 50:  # Too many connections
                return False
                
            # Check for network spikes
            time.sleep(0.1)
            new_counters = psutil.net_io_counters()
            bytes_sent_delta = new_counters.bytes_sent - bytes_sent
            bytes_recv_delta = new_counters.bytes_recv - bytes_recv
            
            # If data transfer rate is too high (potential monitoring)
            if bytes_sent_delta > 100000 or bytes_recv_delta > 100000:  # 100KB/s threshold
                return False
                
            return True
        except:
            return True

    def check_resource_usage(self):
        """Monitor system resource patterns"""
        try:
            # Check disk I/O
            disk_io = psutil.disk_io_counters()
            initial_read = disk_io.read_bytes
            initial_write = disk_io.write_bytes
            
            time.sleep(0.1)
            
            disk_io = psutil.disk_io_counters()
            read_rate = disk_io.read_bytes - initial_read
            write_rate = disk_io.write_bytes - initial_write
            
            # High disk activity might indicate logging/monitoring
            if read_rate > 1000000 or write_rate > 1000000:  # 1MB/s threshold
                return False
            
            # Check GPU usage if available
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    if gpu.load * 100 > 50:  # GPU usage > 50%
                        return False
            except:
                pass
                
            # Check for suspicious file handles
            process = psutil.Process()
            open_files = process.open_files()
            if len(open_files) > 50:  # Too many open files
                return False
                
            return True
        except:
            return True
            
    def check_safety(self):
        """Enhanced safety check system"""
        try:
            checks = [
                self.check_network_activity(),
                self.check_resource_usage(),
                self._check_basic_safety()  # Original safety checks
            ]
            
            # If any check fails, return False
            if not all(checks):
                # Add random delay before next check
                time.sleep(random.uniform(10, 30))
                return False
                
            return True
        except:
            return True
            
    def _check_basic_safety(self):
        """Original safety checks renamed"""
        try:
            # Check process count
            if len(psutil.process_iter()) > 100:
                return False
                
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 70:
                return False
                
            # Check memory usage
            mem = psutil.virtual_memory()
            if mem.percent > 80:
                return False
                
            # Check for suspicious processes
            suspicious = ['wireshark', 'fiddler', 'charles', 'burp', 'monitor', 
                        'procmon', 'process monitor', 'netstat', 'tcpdump']
            for proc in psutil.process_iter(['name']):
                if any(s in proc.info['name'].lower() for s in suspicious):
                    return False
                    
            return True
        except:
            return True
        
    def view_stats(self):
        """View current statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use obfuscated table names
            cursor.execute('SELECT COUNT(*) FROM sys_cache')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT val FROM sys_cache ORDER BY ts DESC LIMIT 10')
            encoded_numbers = [row[0] for row in cursor.fetchall()]
            numbers = [self.crypto.decode_number(n) for n in encoded_numbers if n is not None]
            
            cursor.execute('SELECT val, COUNT(*) as count FROM sys_cache GROUP BY val ORDER BY count DESC LIMIT 5')
            common = []
            for row in cursor.fetchall():
                number = self.crypto.decode_number(row[0])
                if number is not None:
                    common.append((number, row[1]))
                    
            conn.close()
            
            # Minimal output
            if total > 0:
                print(f"{total}")
                print(numbers[:3])  # Show only last 3
                print(common[0] if common else "")
                
        except Exception as e:
            pass
            
    def detect_provider(self, image):
        """Detect the provider ID from the image"""
        try:
            # You'll need to implement the actual detection logic
            # For now, returning a placeholder
            return "PROVIDER_1"
        except:
            return None

    def detect_roulette(self, image):
        """Detect the roulette table ID from the image"""
        try:
            # You'll need to implement the actual detection logic
            # For now, returning a placeholder
            return "TABLE_1"
        except:
            return None

    def run(self):
        """Main loop with enhanced tracking"""
        print("\nInitializing...")
        
        paused = False
        last_capture = 0
        capture_interval = random.uniform(0.8, 1.2)
        safety_check_interval = random.uniform(25, 35)
        last_safety_check = time.time()
        consecutive_fails = 0
        
        # Add provider and roulette tracking
        current_provider = None
        current_roulette = None
        last_spin_start = None
        
        while True:
            try:
                current_time = time.time()
                
                # Safety checks
                if current_time - last_safety_check > safety_check_interval:
                    if not self.check_safety():
                        consecutive_fails += 1
                        pause_time = min(300 * (2 ** consecutive_fails), 3600)
                        time.sleep(random.uniform(pause_time * 0.8, pause_time * 1.2))
                    else:
                        consecutive_fails = 0
                    last_safety_check = current_time
                    safety_check_interval = random.uniform(25, 35)
                    
                if keyboard.is_pressed('q'):
                    break
                    
                if keyboard.is_pressed('v'):
                    self.view_stats()
                    time.sleep(0.5)
                    
                if keyboard.is_pressed('p'):
                    paused = not paused
                    time.sleep(0.5)
                    
                if paused:
                    time.sleep(0.1)
                    continue
                    
                if current_time - last_capture < capture_interval:
                    continue
                    
                # Start timing the spin
                if last_spin_start is None:
                    last_spin_start = current_time
                
                image = self.capture_screen()
                number = self.detect_number(image)
                
                if number is not None:
                    # Calculate spin time
                    spin_time = int((current_time - last_spin_start) * 1000)  # Convert to ms
                    
                    # Get current provider and roulette IDs (you'll need to implement these)
                    provider_id = self.detect_provider(image)  # Implement this
                    roulette_id = self.detect_roulette(image)  # Implement this
                    
                    if self.validate_number(number, roulette_id, provider_id, spin_time):
                        metadata = {
                            'screen_region': self.monitor,
                            'confidence': random.uniform(0.85, 0.95),  # Add some noise
                            'process_time': random.uniform(50, 150)  # ms
                        }
                        
                        if self.save_number(number, roulette_id, provider_id, spin_time, metadata):
                            last_spin_start = None  # Reset timer for next spin
                    
                last_capture = current_time
                capture_interval = random.uniform(0.8, 1.2)
                
                time.sleep(random.uniform(0.05, 0.15))
                
            except Exception as e:
                time.sleep(random.uniform(1, 3))
                consecutive_fails += 1

def main():
    collector = AutoRouletteCollector()
    collector.run()

if __name__ == "__main__":
    main()
