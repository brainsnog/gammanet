import torch
import numpy as np
import matplotlib.pyplot as plt
import shap
import pandas as pd
from models.cnn import GammaNet1D
import os

# Ensure results directory exists
os.makedirs("results/figures", exist_ok=True)

# 1. Setup and Load
ISOTOPES = ["Cs137", "Co60", "Am241", "Eu152", "K40"]
device = torch.device("cpu")
model = GammaNet1D(num_classes=5)
model.load_state_dict(torch.load("models/gammanet_v1.pt", map_location=device))
model.eval()

# 2. Prepare Data
data = pd.read_hdf("data/raw/train.h5", key="spectra")
all_spectra = torch.tensor(data.values).float()

# 3. Define Wrapper
def predict(x):
    x_tensor = torch.from_numpy(np.array(x)).float()
    with torch.no_grad():
        outputs = model(x_tensor)
    return outputs.numpy()

# 4. Explain the model
# Background should be representative of the "average" input
background = all_spectra[:10].numpy().reshape(10, 1024)
# Selecting sample 11 for the test
test_sample = all_spectra[11:12].numpy().reshape(1, 1024)

print("Calculating SHAP values (this may take a minute)...")
explainer = shap.KernelExplainer(predict, background)
shap_values = explainer.shap_values(test_sample)

# 5. Prediction Check
preds = predict(test_sample)
pred_class = np.argmax(preds[0])
print(f"Model predicts this sample is: {ISOTOPES[pred_class]}")

# We want to see WHY it made that specific prediction
isotope_idx = pred_class 

# 6. Visualization (Dual-Axis Plot)
# We use one plot with two Y-axes to handle the scale difference
fig, ax1 = plt.subplots(figsize=(12, 6))

# Process SHAP attribution
if isinstance(shap_values, list):
    attr = shap_values[isotope_idx].flatten()
else:
    attr = shap_values[0, :, isotope_idx]

# --- LEFT Y-AXIS: The Spectrum ---
ax1.plot(test_sample.flatten(), label="Input Spectrum (Counts)", color='black', alpha=0.3)
ax1.set_xlabel("Channel (Energy)")
ax1.set_ylabel("Counts (Intensity)", color='black')
ax1.tick_params(axis='y', labelcolor='black')

# --- RIGHT Y-AXIS: The SHAP Values ---
ax2 = ax1.twinx() 
ax2.fill_between(range(1024), 0, attr, 
                 where=attr > 0, color='red', alpha=0.6, label="Positive Attribution")
ax2.fill_between(range(1024), 0, attr, 
                 where=attr < 0, color='blue', alpha=0.6, label="Negative Attribution")
ax2.set_ylabel("SHAP Importance Value", color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Combined Legend
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='upper right')

plt.title(f"XAI Analysis: Feature Attribution for {ISOTOPES[isotope_idx]}")
plt.grid(alpha=0.1)
plt.tight_layout()
plt.savefig("results/figures/shap_analysis_dual_axis.png")
plt.show()