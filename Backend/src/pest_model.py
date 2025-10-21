import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import io
from typing import Dict, Union, List
import logging
import os
from keras.models import load_model as keras_load_model
from keras.applications.mobilenet import preprocess_input

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [utils.py] - %(message)s'
)
logger = logging.getLogger(__name__)


CLASS_NAMES = [
    'aphids', 'armyworm', 'beetle', 'bollworm', 'grasshopper',
    'mites', 'mosquito', 'sawfly', 'stem_borer'
]

class PestModel:
    """
    Pest classification model wrapper.
    """
    
    def __init__(self, model_path: str = "Backend/models/pest_classifier.keras"):
        """
        Initializes the PestModel.
        
        Args: model_path (str): Path to the saved .keras model file.
        """
        self.model_path = model_path
        self.model = None
        self.target_size = (224, 224)
        self.class_names = CLASS_NAMES
        self.load_model()
    
    def load_model(self):
        """
        Loads the trained Keras model from the specified path.
        """
        logger.info(f"Attempting to load model from: {self.model_path}")
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found at: {self.model_path}")
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model = keras_load_model(self.model_path)
            
            logger.info(f"Pest model loaded successfully from {self.model_path}")
            
        except (IOError, ImportError) as e:
            logger.error(f"Error loading model from {self.model_path}. File not found or corrupted.", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading model: {e}", exc_info=True)
            raise
    
    def preprocess_image(self, img_input: Union[str, bytes]) -> np.ndarray:
        """
        Preprocesses an image for prediction.
        
        Args: img_input: Either file path (str) or image bytes.
        Returns: Preprocessed image as a numpy array.
        """
        try:
            img = None
            if isinstance(img_input, bytes):
                # If input is bytes, decode it with OpenCV
                nparr = np.frombuffer(img_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif isinstance(img_input, str):
                # If input is a path, read it with OpenCV
                img = cv2.imread(img_input)
            else:
                raise TypeError(f"Invalid input type: {type(img_input)}. Expected 'str' or 'bytes'.")
            
            if img is None:
                raise ValueError(f"Failed to load or decode image: {img_input}")
            
            # preprocessing
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, self.target_size)
            img_array = np.expand_dims(img_resized, axis=0)
            img_preprocessed = preprocess_input(img_array)
            
            return img_preprocessed
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}", exc_info=True)
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, img_input: Union[str, bytes]) -> Dict:
        """
        Predicts the pest type from a given image (path or bytes).
        Args: img_input: Either file path (str) or image bytes.
        Returns: A dictionary containing the prediction results.
        """
        try:
            if self.model is None:
                logger.error("Prediction failed: Model is not loaded.")
                raise RuntimeError("Model not loaded")
            
            img_array = self.preprocess_image(img_input)

            predictions = self.model.predict(img_array, verbose=0) 
            pred_index = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][pred_index]) * 100
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
            logger.error(f"Prediction error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }