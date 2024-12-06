import asyncio
import json
import logging
import websockets
import aiohttp
import platform
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DeviceConfig:
    device_type: str
    platform: str = platform.system()
    version: str = "1.0.0"
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["basic", "sync", "realtime"]

class DeviceConnector:
    """Handles device connectivity with the real-time server"""
    
    def __init__(self, 
                 server_url: str,
                 device_config: DeviceConfig,
                 storage_path: Path):
        self.server_url = server_url
        self.device_config = device_config
        self.storage_path = storage_path
        self.device_id = None
        self.access_token = None
        self.websocket = None
        self.connected = False
        self.message_handlers = {}
        self.sync_queue = asyncio.Queue()
        
        # Setup logging
        self.logger = logging.getLogger("DeviceConnector")
        self.logger.setLevel(logging.INFO)
        
        # Setup storage
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sync_file = self.storage_path / "sync_status.json"
        self._load_sync_status()
        
    def _load_sync_status(self):
        """Load sync status from storage"""
        if self.sync_file.exists():
            with open(self.sync_file, 'r') as f:
                self.sync_status = json.load(f)
        else:
            self.sync_status = {
                "last_sync": {},
                "pending_updates": []
            }
            
    def _save_sync_status(self):
        """Save sync status to storage"""
        with open(self.sync_file, 'w') as f:
            json.dump(self.sync_status, f)
            
    async def connect(self):
        """Connect to the real-time server"""
        try:
            if not self.device_id or not self.access_token:
                await self._register_device()
                
            # Connect WebSocket
            self.websocket = await websockets.connect(
                f"{self.server_url}/ws/connect"
            )
            
            # Authenticate
            await self.websocket.send(json.dumps({
                "type": "auth",
                "token": self.access_token
            }))
            
            self.connected = True
            self.logger.info("Connected to real-time server")
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._sync_loop())
            
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            self.connected = False
            raise
            
    async def _register_device(self):
        """Register device with server"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.server_url}/api/register_device",
                json={
                    "device_type": self.device_config.device_type,
                    "platform": self.device_config.platform,
                    "version": self.device_config.version,
                    "capabilities": self.device_config.capabilities
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.device_id = data["device_id"]
                    self.access_token = data["access_token"]
                    self.logger.info(f"Registered device: {self.device_id}")
                else:
                    raise Exception("Device registration failed")
                    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.connected:
            try:
                await self.websocket.send(json.dumps({
                    "type": "heartbeat"
                }))
                await asyncio.sleep(30)
            except Exception as e:
                self.logger.error(f"Heartbeat error: {str(e)}")
                break
                
    async def _handle_messages(self):
        """Handle incoming messages"""
        while self.connected:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if data["type"] in self.message_handlers:
                    await self.message_handlers[data["type"]](data)
                    
            except websockets.exceptions.ConnectionClosed:
                self.logger.info("Connection closed")
                self.connected = False
                break
            except Exception as e:
                self.logger.error(f"Message handling error: {str(e)}")
                
    async def _sync_loop(self):
        """Handle data synchronization"""
        while self.connected:
            try:
                # Process sync queue
                while not self.sync_queue.empty():
                    sync_item = await self.sync_queue.get()
                    await self._sync_data(sync_item)
                    
                # Check for pending updates
                if self.sync_status["pending_updates"]:
                    update = self.sync_status["pending_updates"].pop(0)
                    await self._sync_data(update)
                    self._save_sync_status()
                    
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Sync error: {str(e)}")
                await asyncio.sleep(5)
                
    async def _sync_data(self, sync_item: Dict):
        """Sync data with server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/api/sync",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={
                        "device_id": self.device_id,
                        "data_type": sync_item["type"],
                        "last_sync": self.sync_status["last_sync"].get(
                            sync_item["type"],
                            datetime.min.isoformat()
                        ),
                        "batch_size": sync_item.get("batch_size", 100)
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._handle_sync_response(sync_item["type"], data)
                    else:
                        self.logger.error(f"Sync failed: {await response.text()}")
                        
        except Exception as e:
            self.logger.error(f"Sync error: {str(e)}")
            # Add back to pending updates
            self.sync_status["pending_updates"].append(sync_item)
            self._save_sync_status()
            
    async def _handle_sync_response(self, data_type: str, response: Dict):
        """Handle sync response data"""
        # Update sync status
        self.sync_status["last_sync"][data_type] = response["sync_time"]
        self._save_sync_status()
        
        # Process received data
        if data_type in self.message_handlers:
            await self.message_handlers[data_type](response["data"])
            
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler
        
    async def request_sync(self, data_type: str, batch_size: int = 100):
        """Request data synchronization"""
        await self.sync_queue.put({
            "type": data_type,
            "batch_size": batch_size
        })
        
    async def subscribe_topics(self, topics: List[str]):
        """Subscribe to topics"""
        if self.connected:
            await self.websocket.send(json.dumps({
                "type": "subscribe",
                "topics": topics
            }))
            
    async def unsubscribe_topics(self, topics: List[str]):
        """Unsubscribe from topics"""
        if self.connected:
            await self.websocket.send(json.dumps({
                "type": "unsubscribe",
                "topics": topics
            }))
            
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        self.logger.info("Disconnected from server")
