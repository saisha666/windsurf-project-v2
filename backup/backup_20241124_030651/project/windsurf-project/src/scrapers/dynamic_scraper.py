import keyboard
import pyautogui
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
from datetime import datetime
import pandas as pd

class DynamicScraper:
    def __init__(self):
        """Initialize the dynamic scraper with recording and playback capabilities"""
        self.actions = []
        self.is_recording = False
        self.config_file = "scraper_config.json"
        self.data_file = "scraped_data.csv"
        
        # Get all monitors
        self.monitors = []
        print("\nDetected Monitors:")
        for i, monitor in enumerate(pyautogui.getAllMonitors()):
            print(f"Monitor {i}: {monitor}")
            self.monitors.append(monitor)
        
        # Let user select monitor
        if len(self.monitors) > 1:
            monitor_num = int(input("\nEnter monitor number (0, 1, etc.): "))
            self.monitor = self.monitors[monitor_num]
        else:
            self.monitor = self.monitors[0]
        
        # Initialize Selenium
        chrome_options = Options()
        # Position browser on selected monitor
        chrome_options.add_argument(f"--window-position={self.monitor.left},{self.monitor.top}")
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        print("\n=== Dynamic Web Scraper ===")
        print("Controls:")
        print("- Press 'r' to start/stop recording actions")
        print("- Press 'p' to play recorded actions")
        print("- Press 's' to save recorded actions")
        print("- Press 'l' to load saved actions")
        print("- Press 'c' to clear recorded actions")
        print("- Press 'q' to quit")
        print("=" * 25 + "\n")
    
    def start_recording(self):
        """Start recording user actions"""
        self.is_recording = True
        self.actions = []
        print("\nRecording started. Perform your actions...")
        
        # Record initial URL
        url = input("Enter the website URL: ")
        self.actions.append({
            'type': 'navigate',
            'url': url
        })
        self.driver.get(url)
    
    def stop_recording(self):
        """Stop recording user actions"""
        self.is_recording = False
        print("\nRecording stopped. Actions recorded:")
        for i, action in enumerate(self.actions, 1):
            print(f"{i}. {action['type']}: {action.get('selector', '')} {action.get('value', '')}")
    
    def record_click(self, x, y):
        """Record a mouse click action"""
        if not self.is_recording:
            return
            
        # Adjust coordinates relative to browser window
        browser_x = x - self.monitor.left
        browser_y = y - self.monitor.top
            
        # Try to find a unique selector for the clicked element
        element = self.driver.execute_script(
            'return document.elementFromPoint(arguments[0], arguments[1]);',
            browser_x - self.driver.execute_script('return window.pageXOffset;'),
            browser_y - self.driver.execute_script('return window.pageYOffset;')
        )
        
        if element:
            # Try different strategies to create a unique selector
            selectors = []
            
            # Try ID
            if element.get_attribute('id'):
                selectors.append(f"#{element.get_attribute('id')}")
            
            # Try class
            if element.get_attribute('class'):
                selectors.append(f".{element.get_attribute('class').replace(' ', '.')}")
            
            # Try XPath
            xpath = self.driver.execute_script("""
                function getPathTo(element) {
                    if (element.id !== '')
                        return "//*[@id='" + element.id + "']";
                    if (element === document.body)
                        return element.tagName;
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element)
                            return getPathTo(element.parentNode) + '/' + element.tagName +
                                   '[' + (ix + 1) + ']';
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                            ix++;
                    }
                }
                return getPathTo(arguments[0]);
            """, element)
            selectors.append(xpath)
            
            self.actions.append({
                'type': 'click',
                'selectors': selectors,
                'x': browser_x,
                'y': browser_y,
                'text_content': element.text
            })
            print(f"Recorded click at ({browser_x}, {browser_y}) on element: {element.tag_name}")
    
    def record_keypress(self, key):
        """Record a keyboard input action"""
        if not self.is_recording:
            return
            
        # Get the active element
        active_element = self.driver.switch_to.active_element
        
        if active_element:
            selectors = []
            
            # Try different strategies to create a unique selector
            if active_element.get_attribute('id'):
                selectors.append(f"#{active_element.get_attribute('id')}")
            if active_element.get_attribute('name'):
                selectors.append(f"[name='{active_element.get_attribute('name')}']")
            if active_element.get_attribute('class'):
                selectors.append(f".{active_element.get_attribute('class').replace(' ', '.')}")
            
            self.actions.append({
                'type': 'input',
                'selectors': selectors,
                'value': key
            })
            print(f"Recorded keypress: {key}")
    
    def save_actions(self):
        """Save recorded actions to a file"""
        if not self.actions:
            print("No actions to save!")
            return
            
        with open(self.config_file, 'w') as f:
            json.dump(self.actions, f, indent=2)
        print(f"\nActions saved to {self.config_file}")
    
    def load_actions(self):
        """Load actions from a file"""
        if not os.path.exists(self.config_file):
            print("No saved actions found!")
            return
            
        with open(self.config_file, 'r') as f:
            self.actions = json.load(f)
        print(f"\nLoaded {len(self.actions)} actions from {self.config_file}")
    
    def play_actions(self):
        """Play recorded actions"""
        if not self.actions:
            print("No actions to play!")
            return
            
        print("\nPlaying recorded actions...")
        
        try:
            for action in self.actions:
                if action['type'] == 'navigate':
                    self.driver.get(action['url'])
                    print(f"Navigated to: {action['url']}")
                    
                elif action['type'] == 'click':
                    # Try each selector until one works
                    clicked = False
                    for selector in action['selectors']:
                        try:
                            element = self.wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR if selector.startswith(('.', '#')) 
                                                          else By.XPATH, selector))
                            )
                            element.click()
                            clicked = True
                            print(f"Clicked element: {selector}")
                            break
                        except:
                            continue
                    
                    if not clicked:
                        # Fallback to coordinates
                        ActionChains(self.driver).move_by_offset(action['x'], action['y']).click().perform()
                        print(f"Clicked at coordinates: ({action['x']}, {action['y']})")
                
                elif action['type'] == 'input':
                    # Try each selector until one works
                    input_done = False
                    for selector in action['selectors']:
                        try:
                            element = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR if selector.startswith(('.', '#')) 
                                                              else By.XPATH, selector))
                            )
                            element.send_keys(action['value'])
                            input_done = True
                            print(f"Entered text in element: {selector}")
                            break
                        except:
                            continue
                    
                    if not input_done:
                        keyboard.write(action['value'])
                        print(f"Typed text: {action['value']}")
                
                time.sleep(1)  # Wait between actions
            
            # After playing actions, extract data
            self.extract_data()
            
        except Exception as e:
            print(f"Error playing actions: {e}")
    
    def extract_data(self):
        """Extract data from the current page"""
        try:
            # Get all text content
            text_elements = self.driver.find_elements(By.XPATH, "//*[not(self::script)]/text()")
            text_data = [elem.text for elem in text_elements if elem.text.strip()]
            
            # Get all links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            link_data = [{'text': link.text, 'href': link.get_attribute('href')} 
                        for link in links if link.text.strip()]
            
            # Create a DataFrame
            df = pd.DataFrame({
                'timestamp': datetime.now(),
                'url': self.driver.current_url,
                'text_content': [text_data],
                'links': [link_data]
            })
            
            # Save to CSV
            df.to_csv(self.data_file, mode='a', header=not os.path.exists(self.data_file), index=False)
            print(f"\nData saved to {self.data_file}")
            
        except Exception as e:
            print(f"Error extracting data: {e}")
    
    def run(self):
        """Main loop for the scraper"""
        try:
            while True:
                if keyboard.is_pressed('r'):
                    if not self.is_recording:
                        self.start_recording()
                    else:
                        self.stop_recording()
                    time.sleep(0.5)  # Prevent multiple triggers
                
                elif keyboard.is_pressed('p'):
                    self.play_actions()
                    time.sleep(0.5)
                
                elif keyboard.is_pressed('s'):
                    self.save_actions()
                    time.sleep(0.5)
                
                elif keyboard.is_pressed('l'):
                    self.load_actions()
                    time.sleep(0.5)
                
                elif keyboard.is_pressed('c'):
                    self.actions = []
                    print("\nActions cleared!")
                    time.sleep(0.5)
                
                elif keyboard.is_pressed('q'):
                    print("\nQuitting...")
                    break
                
                if self.is_recording:
                    # Record mouse clicks
                    if pyautogui.mouseDown():
                        x, y = pyautogui.position()
                        self.record_click(x, y)
                        time.sleep(0.1)
                    
                    # Record keyboard input
                    for event in keyboard.get_typed_strings():
                        if event:
                            self.record_keypress(event)
                
                time.sleep(0.01)  # Prevent high CPU usage
                
        except KeyboardInterrupt:
            print("\nStopping the scraper...")
        finally:
            self.driver.quit()

def main():
    scraper = DynamicScraper()
    scraper.run()

if __name__ == "__main__":
    main()
