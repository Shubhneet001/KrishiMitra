import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import gdown
import json
import os
import io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / 'disease_model' / 'disease_model.pth'
CLASS_INDICES_PATH = BASE_DIR / 'disease_model' / 'disease_classes.json'
PLANT_DISEASE_FILE_ID = "1As5gawGTPeHM5mTACXMEEKHs0DS8qK7T"

def download_plant_disease_model():
    if not MODEL_PATH.exists():
        print(f"Downloading plant disease model...")
        url = f"https://drive.google.com/uc?id={PLANT_DISEASE_FILE_ID}"
        gdown.download(url, str(MODEL_PATH), quiet=False)
        print("Plant disease model downloaded!")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(model_path, class_indices_path, device):
    model = models.resnet50(pretrained=False)
    num_classes = 38
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512, num_classes)
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    with open(class_indices_path, 'r') as f:
        class_indices = json.load(f)

    return model, class_indices

def preprocess_image(image, device):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0).to(device)
    return image

def predict_disease(image_bytes):
    model, class_indices = load_model(MODEL_PATH, CLASS_INDICES_PATH, device)
    
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = preprocess_image(image, device)

    with torch.no_grad():
        outputs = model(image)
        _, predicted_idx = torch.max(outputs, 1)
        
        predicted_class = str(predicted_idx.item())
        class_name = class_indices.get(predicted_class, "Unknown")
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        confidence = probabilities[predicted_idx].item() * 100

    return {
        "disease": class_name,
        "confidence": f"{confidence:.2f}%"
    }
