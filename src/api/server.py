from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import json
import asyncio
from datetime import datetime

from ..database.database import DatabaseManager
from ..scrapers.advanced_scraper import AdvancedScraper

app = FastAPI(title="AI OS API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
scraper = AdvancedScraper()

# Models
class ScrapeRequest(BaseModel):
    url: str
    wait_time: Optional[int] = 10

class MLPredictionRequest(BaseModel):
    model_name: str
    data: Dict[str, Any]

class AnalysisRequest(BaseModel):
    urls: List[str]

# Routes
@app.get("/")
async def root():
    return {"message": "AI OS API is running"}

@app.post("/scrape")
async def scrape_url(request: ScrapeRequest):
    try:
        result = scraper.scrape_url(request.url, request.wait_time)
        if result:
            return {"status": "success", "data": result}
        raise HTTPException(status_code=400, detail="Failed to scrape URL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(limit: int = 100):
    try:
        history = db.get_browser_history(limit)
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_urls(request: AnalysisRequest):
    try:
        results = []
        for url in request.urls:
            structure = scraper.analyze_page_structure(url)
            if structure:
                results.append({
                    "url": url,
                    "structure": structure
                })
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/models")
async def list_models():
    try:
        models = db.get_ml_model()
        return {"status": "success", "data": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/predict")
async def predict(request: MLPredictionRequest):
    try:
        model = db.get_ml_model(request.model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # Here you would load and use the model
        # This is a placeholder
        prediction = {"result": "Prediction placeholder"}
        
        return {"status": "success", "data": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send system updates every 5 seconds
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "system_update",
                "data": {
                    "browser_activity": "Active",
                    "scraping_status": "Idle",
                    "ml_status": "Ready"
                }
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

def start_server():
    """Start the FastAPI server"""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start_server()
