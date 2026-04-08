import os
import numpy as np
import pandas as pd

# Match the ISOTOPES order from your training script exactly
ISOTOPES = ["Cs137", "Co60", "Am241", "Eu152", "K40"]

def create_gaussian_peak(channels, center_ch, fwhm=10):
    """Generates a Gaussian peak to simulate a gamma photopeak."""
    sigma = fwhm / 2.355
    # Ensure center_ch doesn't go out of bounds
    return np.exp(-0.5 * ((channels - center_ch) / sigma)**2)

def generate_stress_test(output_path: str, drift_max=15, signal_strength=50):
    n_channels = 1024
    channels = np.arange(n_channels)
    
    # EXACT peak map from your training script
    peak_map = {
        "Cs137": [662/3],
        "Co60":  [1173/3, 1332/3],
        "Am241": [60/3],
        "Eu152": [121/3, 344/3, 1408/3],
        "K40":   [1460/3]
    }

    all_spectra = []
    all_labels = []

    print(f"Generating Stress Test: Drift ±{drift_max} channels, Signal {signal_strength}")

    for i, iso in enumerate(ISOTOPES):
        for _ in range(200):
            # CHAOS 1: Random Gain Drift
            drift = np.random.randint(-drift_max, drift_max)
            
            spec = np.zeros(n_channels)
            for peak_ch in peak_map[iso]:
                spec += create_gaussian_peak(channels, peak_ch + drift)
            
            # Base background
            spec += 0.05 
            
            # CHAOS 2: Poisson Noise (lower signal_strength = noisier)
            spec = np.random.poisson(spec * signal_strength).astype(float)
            
            # NORMALIZE to match Training Magnitude (Max ~45)
            # Dividing by sum and multiplying by 2500 based on our X-Ray debug
            spec = (spec / spec.sum()) * 2500 
            
            # Store once per loop
            all_spectra.append(spec)
            
            label = np.zeros(len(ISOTOPES))
            label[i] = 1
            all_labels.append(label)

    # Convert and Save
    spectra_df = pd.DataFrame(all_spectra)
    labels_df = pd.DataFrame(all_labels, columns=ISOTOPES)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.HDFStore(output_path) as store:
        store.put('spectra', spectra_df)
        store.put('sources', labels_df)

if __name__ == "__main__":
    generate_stress_test("data/raw/test.h5")
    print("✅ Stress test data generated at data/raw/test.h5")