import os
import re
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class KrishiMitra:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.location = "Pune"
        self.agricultural_database = self.load_agricultural_database()

    def load_agricultural_database(self):
        return {
            "crops": {
                "wheat": {
                    "scientific_name": "Triticum aestivum",
                    "growing_season": "Rabi",
                    "ideal_temperature": "10-25°C",
                    "water_requirements": "Moderate",
                    "soil_type": "Loamy, well-drained",
                    "fertilizer_recommendations": [
                        "NPK 20:20:0",
                        "Urea top dressing"
                    ],
                    "common_diseases": [
                        "Rust",
                        "Powdery Mildew"
                    ]
                },
                "rice": {
                    "scientific_name": "Oryza sativa",
                    "growing_season": "Kharif",
                    "ideal_temperature": "20-35°C",
                    "water_requirements": "High",
                    "soil_type": "Clay, waterlogged",
                    "fertilizer_recommendations": [
                        "NPK 14:14:14",
                        "Organic compost"
                    ],
                    "common_diseases": [
                        "Blast",
                        "Bacterial Leaf Blight"
                    ]
                }
            },
            "government_schemes": [
                {
                    "name": "PM-KISAN",
                    "description": "Income support scheme for farmers",
                    "benefits": [
                        "₹6,000 annual financial support",
                        "Direct bank transfer"
                    ]
                },
                {
                    "name": "Pradhan Mantri Fasal Bima Yojana",
                    "description": "Crop insurance scheme",
                    "benefits": [
                        "Low premium rates",
                        "Full crop loss coverage"
                    ]
                }
            ]
        }

    def get_weather_data(self, location: str):
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return None

        try:
            current_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
            forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=7&aqi=no&alerts=no"

            current_response = requests.get(current_url)
            forecast_response = requests.get(forecast_url)

            if current_response.status_code == 200 and forecast_response.status_code == 200:
                current_data = current_response.json()
                forecast_data = forecast_response.json()

                weather_info = {
                    "location": current_data["location"]["name"],
                    "temperature": current_data["current"]["temp_c"],
                    "conditions": current_data["current"]["condition"]["text"],
                    "humidity": current_data["current"]["humidity"],
                    "wind_speed": current_data["current"]["wind_kph"],
                    "rainfall": current_data["current"].get("precip_mm", 0),
                    "forecast": forecast_data["forecast"]["forecastday"]
                }

                return weather_info
            else:
                return None

        except Exception as e:
            return None

    def generate_ai_response(self, query: str) -> str:
        try:
            full_prompt = f"""
            You are Krishi Mitra, an advanced AI agricultural assistant. 
            Provide a helpful HTML-formatted response to the user's query below:

            Context:
            - Current location: {self.location}
            - Agricultural knowledge base loaded
            - Focus on practical, actionable advice

            Query: {query}

            Please return the response in clean, structured HTML with:
            - <strong> for highlights
            - <ul>/<li> for lists
            - <p> for paragraphs
            """

            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            return f"<p>Sorry, I couldn't process your request. Error: {str(e)}</p>"

    def get_crop_specific_advice(self, crop_name: str):
        crop_info = self.agricultural_database["crops"].get(crop_name.lower())
        if crop_info:
            advice = f"""
            <h3>🌾 Crop Details for {crop_name.capitalize()}</h3>
            <p><strong>Scientific Name:</strong> {crop_info['scientific_name']}</p>
            <p><strong>Growing Season:</strong> {crop_info['growing_season']}</p>
            <p><strong>Ideal Temperature:</strong> {crop_info['ideal_temperature']}</p>
            <p><strong>Water Requirements:</strong> {crop_info['water_requirements']}</p>
            <p><strong>Soil Type:</strong> {crop_info['soil_type']}</p>
            <p><strong>Fertilizer Recommendations:</strong></p>
            <ul>{''.join(f'<li>{rec}</li>' for rec in crop_info['fertilizer_recommendations'])}</ul>
            <p><strong>Common Diseases:</strong></p>
            <ul>{''.join(f'<li>{disease}</li>' for disease in crop_info['common_diseases'])}</ul>
            """
            return advice
        return "<p>Crop information not found in database.</p>"

    def find_government_schemes(self):
        schemes = self.agricultural_database["government_schemes"]
        scheme_details = "".join([
            f"<h4>🏣 {scheme['name']}</h4><p>{scheme['description']}</p><ul>{''.join(f'<li>{benefit}</li>' for benefit in scheme['benefits'])}</ul>"
            for scheme in schemes
        ])
        return scheme_details
