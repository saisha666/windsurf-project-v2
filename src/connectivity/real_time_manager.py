import asyncio
import json
import logging
import websockets
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
from pathlib import Path

class DeviceInfo(BaseModel):
    device_id: str
    device_type: str  # mobile, pda, desktop, etc.
    platform: str
    version: str
    capabilities: List[str]
    
class ConnectionStatus(BaseModel):
    device_id: str
    status: str
    last_seen: datetime
    connection_type: str
    sync_status: Dict

class SyncRequest(BaseModel):
    device_id: str
    data_type: str
    last_sync: datetime
    batch_size: int = 100

@dataclass
class ConnectedDevice:
    device_id: str
    websocket: WebSocket
    device_type: str
    last_heartbeat: datetime
    sync_status: Dict[str, datetime]

class RealTimeManager:
    """Manages real-time connectivity with various devices"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.app = FastAPI(title="Roulette Analysis Real-time API")
        self.setup_api()
        self.redis = Redis.from_url(redis_url)
        self.connected_devices: Dict[str, ConnectedDevice] = {}
        self.active_subscriptions: Dict[str, Set[str]] = {}
        self.security = HTTPBearer()
        self.secret_key = "your-secret-key"  # In production, use secure key management
        
        # Setup logging
        self.logger = logging.getLogger("RealTimeManager")
        self.logger.setLevel(logging.INFO)
        
    def setup_api(self):
        """Configure API settings and middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self.app.post("/api/register_device")(self.register_device)
        self.app.get("/api/device_status")(self.get_device_status)
        self.app.post("/api/sync")(self.handle_sync_request)
        self.app.websocket("/ws/connect")(self.handle_websocket)
        
    async def register_device(self, device_info: DeviceInfo) -> Dict:
        """Register a new device and return access token"""
        try:
            device_id = str(uuid.uuid4())
            token = self._generate_token(device_id, device_info.device_type)
            
            # Store device info in Redis
            device_data = {
                "device_id": device_id,
                "info": device_info.dict(),
                "registered_at": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
            self.redis.hset(f"device:{device_id}", mapping=device_data)
            
            return {
                "device_id": device_id,
                "access_token": token,
                "expires_in": 3600 * 24  # 24 hours
            }
            
        except Exception as e:
            self.logger.error(f"Error registering device: {str(e)}")
            raise HTTPException(status_code=500, detail="Registration failed")
            
    async def get_device_status(self, 
                              credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> ConnectionStatus:
        """Get current device connection status"""
        try:
            device_id = self._verify_token(credentials.credentials)
            device = self.connected_devices.get(device_id)
            
            if not device:
                # Check Redis for offline device
                device_data = self.redis.hgetall(f"device:{device_id}")
                if not device_data:
                    raise HTTPException(status_code=404, detail="Device not found")
                    
                return ConnectionStatus(
                    device_id=device_id,
                    status="offline",
                    last_seen=datetime.fromisoformat(device_data[b'last_seen'].decode()),
                    connection_type="none",
                    sync_status={}
                )
                
            return ConnectionStatus(
                device_id=device_id,
                status="online",
                last_seen=device.last_heartbeat,
                connection_type="websocket",
                sync_status=device.sync_status
            )
            
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    async def handle_sync_request(self, 
                                sync_req: SyncRequest,
                                credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Dict:
        """Handle data synchronization request"""
        try:
            device_id = self._verify_token(credentials.credentials)
            
            # Get sync data from Redis
            sync_key = f"sync:{device_id}:{sync_req.data_type}"
            pending_data = self.redis.zrangebyscore(
                sync_key,
                min=sync_req.last_sync.timestamp(),
                max="+inf",
                start=0,
                num=sync_req.batch_size
            )
            
            # Update sync status
            if device_id in self.connected_devices:
                self.connected_devices[device_id].sync_status[sync_req.data_type] = datetime.now()
                
            return {
                "data": [json.loads(d) for d in pending_data],
                "has_more": len(pending_data) == sync_req.batch_size,
                "sync_time": datetime.now().isoformat()
            }
            
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections"""
        await websocket.accept()
        device_id = None
        
        try:
            # Authenticate connection
            auth_msg = await websocket.receive_json()
            try:
                device_id = self._verify_token(auth_msg.get("token"))
            except:
                await websocket.close(code=4001, reason="Invalid token")
                return
                
            # Register connection
            device_info = self.redis.hgetall(f"device:{device_id}")
            if not device_info:
                await websocket.close(code=4004, reason="Device not found")
                return
                
            device = ConnectedDevice(
                device_id=device_id,
                websocket=websocket,
                device_type=device_info[b'info'][b'device_type'].decode(),
                last_heartbeat=datetime.now(),
                sync_status={}
            )
            self.connected_devices[device_id] = device
            
            # Handle messages
            while True:
                message = await websocket.receive_json()
                await self._handle_device_message(device, message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Connection closed for device {device_id}")
        finally:
            if device_id:
                self._cleanup_device(device_id)
                
    async def broadcast_update(self, update_type: str, data: Dict, target_types: Optional[List[str]] = None):
        """Broadcast updates to connected devices"""
        message = {
            "type": update_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        for device in self.connected_devices.values():
            if not target_types or device.device_type in target_types:
                try:
                    await device.websocket.send_json(message)
                except Exception as e:
                    self.logger.error(f"Error broadcasting to device {device.device_id}: {str(e)}")
                    
    async def _handle_device_message(self, device: ConnectedDevice, message: Dict):
        """Handle incoming device messages"""
        msg_type = message.get("type")
        
        if msg_type == "heartbeat":
            device.last_heartbeat = datetime.now()
            await device.websocket.send_json({"type": "heartbeat_ack"})
            
        elif msg_type == "subscribe":
            topics = message.get("topics", [])
            self.active_subscriptions.setdefault(device.device_id, set()).update(topics)
            
        elif msg_type == "unsubscribe":
            topics = message.get("topics", [])
            if device.device_id in self.active_subscriptions:
                self.active_subscriptions[device.device_id].difference_update(topics)
                
        elif msg_type == "sync_request":
            # Handle real-time sync request
            sync_data = await self.handle_sync_request(
                SyncRequest(**message.get("sync_params", {})),
                HTTPAuthorizationCredentials(scheme="Bearer", credentials=message.get("token"))
            )
            await device.websocket.send_json({
                "type": "sync_response",
                "data": sync_data
            })
    
    def _cleanup_device(self, device_id: str):
        """Clean up disconnected device"""
        if device_id in self.connected_devices:
            del self.connected_devices[device_id]
        if device_id in self.active_subscriptions:
            del self.active_subscriptions[device_id]
            
    def _generate_token(self, device_id: str, device_type: str) -> str:
        """Generate JWT token for device authentication"""
        payload = {
            "device_id": device_id,
            "device_type": device_type,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
        
    def _verify_token(self, token: str) -> str:
        """Verify JWT token and return device_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["device_id"]
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    async def start_cleanup_task(self):
        """Start background task to clean up stale connections"""
        while True:
            try:
                current_time = datetime.now()
                stale_devices = [
                    device_id for device_id, device in self.connected_devices.items()
                    if (current_time - device.last_heartbeat).seconds > 60
                ]
                
                for device_id in stale_devices:
                    self._cleanup_device(device_id)
                    
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(30)
                
    def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the real-time server"""
        import uvicorn
        
        # Start cleanup task
        asyncio.create_task(self.start_cleanup_task())
        
        # Start server
        uvicorn.run(self.app, host=host, port=port)
