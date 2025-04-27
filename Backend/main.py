import os
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import uvicorn

from disease_model import predict_disease, download_plant_disease_model
from pest_model import predict_pest, download_pest_classification_model
from chatbot import KrishiMitra

# Download models before app starts
download_plant_disease_model()
download_pest_classification_model()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = KrishiMitra()

@app.post("/disease-prediction/")
async def disease_prediction(file: UploadFile = File(...)):
    contents = await file.read()
    result = predict_disease(contents)
    return JSONResponse(content=result)

@app.post("/pest-prediction/")
async def pest_prediction(file: UploadFile = File(...)):
    contents = await file.read()
    result = predict_pest(contents)
    return JSONResponse(content=result)

@app.get("/chatbot/")
async def chatbot_response(query: str = Query(..., title="User query")):
    response = chatbot.generate_ai_response(query)
    return JSONResponse(content={"response": response})

@app.get("/weather/")
async def get_weather_data():
    location = chatbot.location
    weather_data = chatbot.get_weather_data(location)
    if weather_data:
        return JSONResponse(content=weather_data)
    else:
        return JSONResponse(content={"error": "Failed to fetch weather data"}, status_code=500)

@app.get("/crop-advice/")
async def crop_advice(crop_name: str = Query(..., title="Crop name")):
    advice = chatbot.get_crop_specific_advice(crop_name)
    return JSONResponse(content={"advice": advice})

@app.put("/set-location/")
async def set_location(location: str = Query(..., description="Location to set for chatbot")):
    chatbot.location = location
    return JSONResponse(content={"message": f"Location set to {location}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

