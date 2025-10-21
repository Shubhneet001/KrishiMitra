import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import io
import os
from typing import Dict, Union, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLASS_DICT = {
    0: "Apple___Apple_scab",
    1: "Apple___Black_rot",
    2: "Apple___Cedar_apple_rust",
    3: "Apple___healthy",
    4: "Blueberry___healthy",
    5: "Cherry_(including_sour)___Powdery_mildew",
    6: "Cherry_(including_sour)___healthy",
    7: "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot",
    8: "Corn_(maize)___Common_rust_",
    9: "Corn_(maize)___Northern_Leaf_Blight",
    10: "Corn_(maize)___healthy",
    11: "Grape___Black_rot",
    12: "Grape___Esca_(Black_Measles)",
    13: "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    14: "Grape___healthy",
    15: "Orange___Haunglongbing_(Citrus_greening)",
    16: "Peach___Bacterial_spot",
    17: "Peach___healthy",
    18: "Pepper,_bell___Bacterial_spot",
    19: "Pepper,_bell___healthy",
    20: "Potato___Early_blight",
    21: "Potato___Late_blight",
    22: "Potato___healthy",
    23: "Raspberry___healthy",
    24: "Soybean___healthy",
    25: "Squash___Powdery_mildew",
    26: "Strawberry___Leaf_scorch",
    27: "Strawberry___healthy",
    28: "Tomato___Bacterial_spot",
    29: "Tomato___Early_blight",
    30: "Tomato___Late_blight",
    31: "Tomato___Leaf_Mold",
    32: "Tomato___Septoria_leaf_spot",
    33: "Tomato___Spider_mites_(Two-spotted_spider_mite)",
    34: "Tomato___Target_Spot",
    35: "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    36: "Tomato___Tomato_mosaic_virus",
    37: "Tomato___healthy"
}

class DiseaseModel:
    """Disease detection model wrapper"""
    
    def __init__(self, model_path: str = "Backend/models/disease_classifier.h5"):
        self.model_path = model_path
        self.model = None
        self.target_size = (256, 256)
        self.load_model()
        self.class_names = CLASS_DICT
    
    def load_model(self):
        """Load the trained model"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            self.model = load_model(self.model_path)
            logger.info(f"Disease model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading disease model: {e}")
            raise
    
    def preprocess_image(self, img_input: Union[str, bytes]) -> np.ndarray:
        """
        Preprocess image for prediction

        Args: img_input: Either file path (str) or image bytes
        Returns: Preprocessed image array
        """
        try:
            if isinstance(img_input, bytes):
                img = Image.open(io.BytesIO(img_input))
            else:
                img = Image.open(img_input)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize
            img = img.resize(self.target_size)
            
            # Convert to array and normalize
            img_array = np.array(img, dtype=np.float32)
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, img_input: Union[str, bytes]) -> Dict:
        """
        Predict disease from image

        Args: img_input: Either file path or image bytes
        Returns: Dictionary with prediction results
        """
        try:
            if self.model is None:
                raise RuntimeError("Model not loaded")
            
            # Preprocess
            img_array = self.preprocess_image(img_input)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            pred_index = int(np.argmax(predictions[0]))
            confidence = float(np.max(predictions[0])) * 100
            top_3_indices = np.argsort(predictions[0])[-3:][::-1]
            top_3_predictions = [
                {
                    "pest": self.class_names[i],
                    "confidence": round(float(predictions[0][i]) * 100, 2)
                }
                for i in top_3_indices
            ]
            
            # Get class label
            class_name = CLASS_DICT.get(pred_index, "Unknown")
            
            # Extract plant and disease information
            parts = class_name.split("___")
            plant = parts[0] if len(parts) > 0 else "Unknown"
            disease = parts[1] if len(parts) > 1 else "Unknown"
            
            return {
                "success": True,
                "predicted_class": class_name,
                "plant": plant,
                "disease": disease,
                "confidence": round(confidence, 2),
                "is_healthy": "healthy" in disease.lower(),
                "top_3_predictions": top_3_predictions
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }