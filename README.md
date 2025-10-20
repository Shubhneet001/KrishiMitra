# Krishi Mitra: AI-Powered Agricultural Assistant

<div align="center">

**A smart farming companion designed to empower farmers with advanced AI technology for crop diagnostics and management.**

</div>

---

## Overview

**Krishi Mitra** is a web-based application that provides real-time assistance for detecting plant diseases, identifying pests, and receiving personalized agricultural advice.  
By leveraging **computer vision** and **natural language processing**, it aims to enhance crop yield, reduce losses, and promote sustainable farming practices.

---

## Key Features

### 1. Disease Detection
Upload an image of a plant leaf to get an instant diagnosis.  
The system can identify over **38 common plant diseases** with high accuracy.

---

### 2. Pest Identification
Identify harmful pests affecting your crops by uploading a photo.  
The pest classifier uses deep learning to detect and classify major pest species.

---

### 3. AI Chatbot Assistant
An intelligent conversational AI assistant powered by **Llama 3** and **LangChain**, offering:
- Crop care and treatment recommendations  
- Personalized responses based on user queries  
- Contextual memory and real-time adaptability

---

### 4. Real-Time Weather Insights
Access current weather conditions and agriculturally relevant data such as:
- Temperature, humidity, and rainfall  
- UV index and cloud coverage  
- Data localized to the user’s geographical location

---

### 5. Mobile-Responsive Design
A modern and lightweight interface built with **vanilla HTML, CSS, and JavaScript**, ensuring accessibility and performance across devices.

---

<p align="center">
  <img src="https://github.com/user-attachments/assets/d162fd51-8c69-4cd4-a8f4-3c688ecd3185" width="33%"/>
  <img src="https://github.com/user-attachments/assets/7fa221f1-fe85-4681-aa38-5a63872d6167" width="33%"/>
  <img src="https://github.com/user-attachments/assets/6678391e-7941-4848-a53b-1d39683f5439" width="33%"/>
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/e6b13f3c-6b72-46f1-b2db-826a93b2d350" width="45%"/>
  <img src="https://github.com/user-attachments/assets/02e61213-334a-44cc-8b74-16edc3f05579" width="45%"/>
</p>

---

## Technology Stack

| Category | Technologies |
|-----------|--------------|
| **Frontend** | HTML, CSS, JavaScript |
| **Backend** | Python, FastAPI |
| **Machine Learning** | TensorFlow, Keras |
| **AI Chatbot** | LangChain, Hugging Face (Llama 3), FAISS |
| **Server / Deployment** | Uvicorn (ASGI) |
| **APIs** | WeatherAPI.com (for live weather data) |

---

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites
- Python 3.8 or higher  
- Git  
- A modern web browser

---

### 1. Clone the Repository

```bash
git clone https://github.com/Shubhneet001/KrishiMitra.git
cd KrishiMitra
````

---

### 2. Backend Setup

Navigate to the backend directory and create a virtual environment:

```bash
cd Backend
python -m venv venv
```

Activate the virtual environment:

* **Windows:**

  ```bash
  venv\Scripts\activate
  ```
* **macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r Backend/requirements.txt
```

---

### 3. Configure Environment Variables

Create a `.env` file inside the `Backend` directory and add the following variables:

```env
# Backend/.env file

# Hugging Face API Token
HUGGINGFACE_API_TOKEN="your_hugging_face_api_token"

# WeatherAPI Key
WEATHER_API_KEY="your_weather_api_key"
```

> Note: The application requires valid API keys for functionality.
> You can obtain these keys for free from:
>
> * Hugging Face: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
> * WeatherAPI: [https://www.weatherapi.com/](https://www.weatherapi.com/)

---

### 4. Run the Backend Server

Ensure your virtual environment is activated, then start the FastAPI server:

```bash
uvicorn Backend.main:app --reload
```

The backend will be available at:
**[http://localhost:8000](http://localhost:8000)**

---

### 5. Launch the Frontend

Navigate to the `Frontend` folder and open the `index.html` file directly in your web browser.

---

## Project Structure

```
krishi-mitra/
├── Backend/
│   ├── models/
│   │   ├── crop_disease_detection.h5
│   │   └── pest_classification.keras
│   ├── .env
│   ├── chatbot.py
│   ├── disease_model.py
│   ├── main.py
│   ├── pest_model.py
│   └── requirements.txt
├── Frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── .gitignore
└── README.md
```
