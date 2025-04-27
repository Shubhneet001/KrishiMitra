import torch
import json
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import torch.nn as nn
import gdown
import os
import io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / 'pest_model' / 'pest_model.pth'
CLASS_INDICES_PATH = BASE_DIR / 'pest_model' / 'pest_classes.json'
PEST_CLASSIFICATION_FILE_ID = "1s5VddwxRoKHrqSBpRkfnZsomadkKQnzp"

def download_pest_classification_model():
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading pest classification model...")
        url = f"https://drive.google.com/uc?id={PEST_CLASSIFICATION_FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Pest classification model downloaded!")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_class_names(class_indices_path):
    with open(class_indices_path, "r") as f:
        class_indices = json.load(f)
    return {v: k for k, v in class_indices.items()}

def load_model(model_path, class_indices_path, device):
    download_pest_classification_model()
    class_names = load_class_names(class_indices_path)

    model = models.efficientnet_b0(pretrained=False)
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Flatten(),
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, len(class_names)),
        nn.Softmax(dim=1)
    )

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    return model, class_names

def preprocess_image(image, device):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0).to(device)
    return image

def predict_pest(image_bytes):
    model, class_names = load_model(MODEL_PATH, CLASS_INDICES_PATH, device)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = preprocess_image(image, device)

    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)

    return {"pest": class_names[predicted.item()]}
