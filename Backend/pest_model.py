import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import io
from typing import Dict, Union, List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLASS_NAMES = [
    'aphids', 'armyworm', 'beetle', 'bollworm', 'grasshopper',
    'mites', 'mosquito', 'sawfly', 'stem_borer'
]

class PestModel:
    """Pest classification model wrapper"""
    
    def __init__(self, model_path: str = "Backend/models/pest_classification.keras"):
        self.model_path = model_path
        self.model = None
        self.target_size = (224, 224)
        self.class_names = CLASS_NAMES
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            logger.info(f"Pest model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading pest model: {e}")
            raise
    
    def preprocess_image(self, img_input: Union[str, bytes]) -> np.ndarray:
        """
        Preprocess image for prediction
        
        Args:
            img_input: Either file path (str) or image bytes
            
        Returns:
            Preprocessed image array
        """
        try:
            if isinstance(img_input, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(img_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = cv2.imread(img_input)
            
            if img is None:
                raise ValueError("Failed to load image")
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize
            img = cv2.resize(img, self.target_size)
            
            # Expand dimensions and preprocess
            img_array = np.expand_dims(img, axis=0)
            img_array = tf.keras.applications.mobilenet.preprocess_input(img_array)
            
            return img_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, img_input: Union[str, bytes]) -> Dict:
        """
        Predict pest from image
        
        Args:
            img_input: Either file path or image bytes
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if self.model is None:
                raise RuntimeError("Model not loaded")
            
            # Preprocess
            img_array = self.preprocess_image(img_input)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            pred_index = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][pred_index]) * 100
            
            # Get top 3 predictions
            top_3_indices = np.argsort(predictions[0])[-3:][::-1]
            top_3_predictions = [
                {
                    "pest": self.class_names[i],
                    "confidence": round(float(predictions[0][i]) * 100, 2)
                }
                for i in top_3_indices
            ]
            
            return {
                "success": True,
                "predicted_pest": self.class_names[pred_index],
                "confidence": round(confidence, 2),
                "top_3_predictions": top_3_predictions
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
