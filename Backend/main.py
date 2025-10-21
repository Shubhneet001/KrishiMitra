import warnings
warnings.filterwarnings("ignore")
import os
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging

from src.disease_model import DiseaseModel
from src.pest_model import PestModel
from src.chatbot import KrishiMitra
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Krishi Mitra API",
    description="Agricultural Assistant API for disease detection, pest identification, and farming advice",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LocationUpdate(BaseModel):
    location: str

class ChatQuery(BaseModel):
    query: str

# Initialize models and chatbot
disease_model = None
pest_model = None
chatbot = None

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global disease_model, pest_model, chatbot
    try:
        disease_model = DiseaseModel()
        logger.info("Disease model initialized")
    except Exception as e:
        logger.error(f"Failed to initialize disease model: {e}")
    
    try:
        pest_model = PestModel()
        logger.info("Pest model initialized")
    except Exception as e:
        logger.error(f"Failed to initialize pest model: {e}")
    
    try:
        chatbot = KrishiMitra()
        logger.info("Chatbot initialized")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Krishi Mitra API",
        "version": "1.0.0",
        "endpoints": {
            "disease_prediction": "/disease-prediction/",
            "pest_prediction": "/pest-prediction/",
            "chatbot": "/chatbot/",
            "weather": "/weather/",
            "set_location": "/set-location/",
            "health": "/health/"
        }
    }

@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "disease_model": disease_model is not None,
        "pest_model": pest_model is not None,
        "chatbot": chatbot is not None
    }

@app.post("/disease-prediction/")
async def disease_prediction(file: UploadFile = File(...)):
    """Predict plant disease from uploaded image"""
    if disease_model is None:
        raise HTTPException(status_code=503, detail="Disease model not initialized")
    
    try:
        contents = await file.read()
        result = disease_model.predict(contents)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Disease prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pest-prediction/")
async def pest_prediction(file: UploadFile = File(...)):
    """Predict pest type from uploaded image"""
    if pest_model is None:
        raise HTTPException(status_code=503, detail="Pest model not initialized")
    
    try:
        contents = await file.read()
        result = pest_model.predict(contents)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Pest prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chatbot/")
async def chatbot_endpoint(chat_query: ChatQuery):
    """Chat with Krishi Mitra assistant"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        response = chatbot.ask(chat_query.query)
        return JSONResponse(content={"response": response})
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chatbot/")
async def chatbot_get(query: str = Query(..., description="User query")):
    """Chat with Krishi Mitra assistant (GET method)"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        response = chatbot.ask(query)
        return JSONResponse(content={"response": response})
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/")
async def get_weather():
    """Get current weather data for the set location"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        weather_data = chatbot.get_weather_data()
        if weather_data:
            return JSONResponse(content=weather_data)
        else:
            raise HTTPException(status_code=404, detail="Weather data not available")
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/{location}")
async def get_weather_by_location(location: str):
    """Get weather data for a specific location"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        weather_data = chatbot.get_weather_data(location)
        if weather_data:
            return JSONResponse(content=weather_data)
        else:
            raise HTTPException(status_code=404, detail=f"Weather data not available for {location}")
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/set-location/")
async def set_location(location_data: LocationUpdate):
    """Set location for weather and chatbot context"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        chatbot.update_location(location_data.location)
        return JSONResponse(content={
            "message": f"Location updated to {location_data.location}",
            "location": location_data.location
        })
    except Exception as e:
        logger.error(f"Location update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-memory/")
async def clear_chatbot_memory():
    """Clear chatbot conversation memory"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        chatbot.clear_memory()
        return JSONResponse(content={"message": "Memory cleared successfully"})
    except Exception as e:
        logger.error(f"Memory clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/info/")
async def get_models_info():
    """Get information about loaded models"""
    return {
        "disease_model": {
            "loaded": disease_model is not None,
            "classes": len(disease_model.class_names) if disease_model else 0,
            "target_size": disease_model.target_size if disease_model else None
        },
        "pest_model": {
            "loaded": pest_model is not None,
            "classes": len(pest_model.class_names) if pest_model else 0,
            "class_names": pest_model.class_names if pest_model else [],
            "target_size": pest_model.target_size if pest_model else None
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)     # for using across multiple devices
    uvicorn.run("main:app", host="localhost", port=port, reload=True)       # for local use only