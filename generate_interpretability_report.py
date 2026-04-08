import torch
import numpy as np
import matplotlib.pyplot as plt
import shap
import pandas as pd
from models.cnn import GammaNet1D
import os

# 1. Setup
ISOTOPES = ["Cs137", "Co60", "Am241", "Eu152", "K40"]
os.makedirs("results/interpretability_report", exist_ok=True)

device = torch.device("cpu")
model = GammaNet1D(num_classes=5)
model.load_state_dict(torch.load("models/gammanet_v1.pt", map_location=device))
model.eval()

# 2. Load Data
print("Loading dataset...")
spectra_df = pd.read_hdf("data/raw/train.h5", key="spectra")
labels_df = pd.read_hdf("data/raw/train.h5", key="sources")

# 3. Prediction Wrapper
def predict(x):
    x_tensor = torch.from_numpy(np.array(x)).float()
    with torch.no_grad():
        outputs = model(x_tensor)
    return outputs.numpy()

# 4. Initialize SHAP Explainer
# Use the first 20 samples as a general background reference
background = spectra_df.iloc[:20].values.reshape(20, 1024)
explainer = shap.KernelExplainer(predict, background)

# 5. Loop through each Isotope
for idx, isotope_name in enumerate(ISOTOPES):
    print(f"\n--- Processing {isotope_name} ---")
    
    # Create the mask
    # We use .values to get a clean numpy array of booleans
    sample_mask = (labels_df[isotope_name] == 1).values
    
    # Check if we found ANY samples for this isotope
    if not np.any(sample_mask):
        print(f"No samples found for {isotope_name}, skipping.")
        continue
        
    # Get the index of the first matching sample
    # np.where returns a tuple of arrays, we take the first element of the first array
    matching_indices = np.where(sample_mask)[0]
    target_row_idx = matching_indices[0]
    
    # Get the spectrum and reshape for SHAP
    # Use .iloc with the integer index we just found
    test_sample = spectra_df.iloc[target_row_idx].values.reshape(1, 1024)

    # Calculate SHAP values for this specific sample
    print(f"Calculating attribution for {isotope_name}...")
    shap_results = explainer.shap_values(test_sample, nsamples=100)
    
    # Extract attribution for the CORRECT class (the one we are looking for)
    if isinstance(shap_results, list):
        attr = shap_results[idx].flatten()
    else:
        attr = shap_results[0, :, idx]
        
    # 6. Create the Dual-Axis Visualization
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Spectrum Axis
    ax1.plot(test_sample.flatten(), label="Input Spectrum", color='black', alpha=0.3, lw=1.5)
    ax1.set_xlabel("Channel (Energy Bin)")
    ax1.set_ylabel("Counts (Normalized)", color='black')
    
    # SHAP Axis
    ax2 = ax1.twinx()
    ax2.fill_between(range(1024), 0, attr, where=attr > 0, color='red', alpha=0.6, label="Positive Attribution")
    ax2.fill_between(range(1024), 0, attr, where=attr < 0, color='blue', alpha=0.6, label="Negative Attribution")
    ax2.set_ylabel("SHAP Importance", color='red')
    
    # Aesthetics
    plt.title(f"Isotope Validation: {isotope_name} Feature Attribution")
    ax1.grid(alpha=0.1)
    
    # Unified Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    # Save output
    filename = f"results/interpretability_report/{isotope_name}_validation.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close() # Close to save memory
    print(f"Saved: {filename}")

print("\nReport Generation Complete! Check results/interpretability_report/")