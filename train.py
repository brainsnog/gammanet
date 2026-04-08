import torch
import torch.nn as nn
import torch.optim as optim
from models.cnn import GammaNet1D
from data_loader import get_dataloaders
import os

# Hyperparameters
EPOCHS = 20
BATCH_SIZE = 32
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train():
    # 1. Load Data
    train_loader, val_loader = get_dataloaders("data/raw/train.h5", BATCH_SIZE)
    
    # 2. Initialize Model
    model = GammaNet1D(num_classes=5).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    print(f"Starting training on {DEVICE}...")
    
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0
        for spectra, labels in train_loader:
            spectra, labels = spectra.to(DEVICE), labels.to(DEVICE)
            
            # Forward pass
            outputs = model(spectra)
            loss = criterion(outputs, torch.max(labels, 1)[1])
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        # Validation phase
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for spectra, labels in val_loader:
                spectra, labels = spectra.to(DEVICE), labels.to(DEVICE)
                outputs = model(spectra)
                loss = criterion(outputs, torch.max(labels, 1)[1])
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == torch.max(labels, 1)[1]).sum().item()
        
        print(f"Epoch [{epoch+1}/{EPOCHS}] - Loss: {train_loss/len(train_loader):.4f} - Val Acc: {100 * correct / total:.2f}%")

    # Save the weights
    os.makedirs("gammanet/models", exist_ok=True)
    torch.save(model.state_dict(), "gammanet/models/gammanet_v1.pt")
    print("Model saved to gammanet/models/gammanet_v1.pt")

if __name__ == "__main__":
    train()