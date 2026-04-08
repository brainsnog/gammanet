import torch
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from models.cnn import GammaNet1D

# 1. Setup
ISOTOPES = ["Cs137", "Co60", "Am241", "Eu152", "K40"]
device = torch.device("cpu")
model = GammaNet1D(num_classes=5)
model.load_state_dict(torch.load("models/gammanet_v1.pt", map_location=device))
model.eval()

data = pd.read_hdf("data/raw/test.h5", key="spectra")
labels = pd.read_hdf("data/raw/test.h5", key="sources")

# 2. Individual Inference
y_true = np.argmax(labels.values, axis=1)
y_pred = []

print("Running robust evaluation...")
for i in range(len(data)):
    # Keep it as a 2D tensor [1, 1024] so the Dimension Guard works
    sample = torch.tensor(data.iloc[i:i+1].values).float()
    with torch.no_grad():
        output = model(sample)
        pred = torch.argmax(output, dim=1).item()
        y_pred.append(pred)

# 3. Final Report
print("\n--- Corrected Classification Report ---")
print(classification_report(y_true, y_pred, target_names=ISOTOPES))

# 4. Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=ISOTOPES, yticklabels=ISOTOPES, cmap='Greens')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Final Validation: Confusion Matrix')
plt.show()