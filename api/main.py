import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.cnn import GammaNet1D
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize API and Model
app = FastAPI(title="GammaNet: Radioisotope Identification API")

# Allow requests from your specific Railway dashboard
origins = [
    "https://gammanet-production.up.railway.app/", 
    "http://localhost:8501", # For local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For debugging, you can use ["*"] to allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ISOTOPES = ["Cs137", "Co60", "Am241", "Eu152", "K40"]
device = torch.device("cpu")

model = GammaNet1D(num_classes=5)
model.load_state_dict(torch.load("models/gammanet_v1.pt", map_location=device))
model.eval()

# 2. Define Data Schema
class SpectrumRequest(BaseModel):
    # Expecting a list of 1024 floats (the counts per channel)
    data: list[float]

# 3. Define the Prediction Endpoint
@app.post("/predict")
async def predict_isotope(request: SpectrumRequest):
    if len(request.data) != 1024:
        raise HTTPException(status_code=400, detail="Spectrum must have 1024 channels.")
    
    # Convert to tensor and add batch dimension
    input_tensor = torch.tensor([request.data]).float()
    
    with torch.no_grad():
        logits = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)
        conf, pred_idx = torch.max(probabilities, 1)
    
    # Extract logits as a list
    logits_list = logits[0].tolist()
    
    return {
        "isotope": ISOTOPES[pred_idx.item()],
        "confidence": conf.item(), # Remove rounding here to keep precision
        "all_probabilities": {
            iso: prob for iso, prob in zip(ISOTOPES, probabilities[0].tolist())
        },
        "logits": {
            iso: logit for iso, logit in zip(ISOTOPES, logits_list)
        }
    }

@app.get("/health")
def health_check():
    return {"status": "online", "model_version": "v1.0.0"}