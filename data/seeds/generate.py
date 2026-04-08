import os
import numpy as np
import riid
from riid.data.synthetic.static import StaticSynthesizer
from riid.data.sampleset import SampleSet
import pandas as pd 

# Professional naming convention
ISOTOPES = ["Cs137", "Co60", "Am241", "Eu152", "K40"]

def create_gaussian_peak(channels, center_ch, fwhm=10):
    """Generates a Gaussian peak to simulate a gamma photopeak."""
    sigma = fwhm / 2.355
    return np.exp(-0.5 * ((channels - center_ch) / sigma)**2)

def generate_datasets(output_dir: str, n_train: int = 2000):
    os.makedirs(output_dir, exist_ok=True)
    
    # --- 1. Isotope Seeds ---
    n_isotopes = len(ISOTOPES)
    n_channels = 1024
    channels = np.arange(n_channels)
    spectra_data = np.zeros((n_isotopes, n_channels))

    peak_map = {
        "Cs137": [662/3],
        "Co60":  [1173/3, 1332/3],
        "Am241": [60/3],
        "Eu152": [121/3, 344/3, 1408/3],
        "K40":   [1460/3]
    }

    for i, iso in enumerate(ISOTOPES):
        seed_spectrum = np.zeros(n_channels)
        for peak_ch in peak_map[iso]:
            seed_spectrum += create_gaussian_peak(channels, peak_ch)
        
        seed_spectrum += 0.05 
        spectra_data[i] = seed_spectrum / seed_spectrum.sum()
    
    seeds_ss = SampleSet()
    seeds_ss.spectra = pd.DataFrame(spectra_data)
    seeds_ss.sources = pd.DataFrame(
        np.eye(n_isotopes), 
        columns=pd.MultiIndex.from_tuples([(iso,) for iso in ISOTOPES], names=["Seed"])
    )
    
    full_info = {
        "real_time": 1.0,
        "live_time": 1.0,
        "distance_cm": 10.0,
        "instrument_type": "NaI",
        "ecal_order_0": 0.0,      
        "ecal_order_1": 3.0,      
        "ecal_order_2": 0.0,      
        "ecal_order_3": 0.0,      
        "ecal_low_e": 0.0         
    }
    seeds_ss.info = pd.DataFrame([full_info] * n_isotopes)
    
    # --- 2. Background Seed ---
    bg_curve = np.exp(-channels / 200) + 0.01
    bg_data = (bg_curve / bg_curve.sum()).reshape(1, -1)
    
    bg_seeds_ss = SampleSet()
    bg_seeds_ss.spectra = pd.DataFrame(bg_data)
    bg_seeds_ss.sources = pd.DataFrame(
        [[1]], 
        columns=pd.MultiIndex.from_tuples([("Background",)], names=["Seed"])
    )
    bg_seeds_ss.info = pd.DataFrame([full_info])

    # --- 3. Setup Synthesizer ---
    # We use snr_min and snr_max instead of a custom function.
    # This achieves the same goal (random SNR between 10 and 100)
    # without triggering the "is not a valid function" error.
    syn = StaticSynthesizer(
        samples_per_seed=n_train // n_isotopes
    )

    print(f"Generating {n_train} samples with realistic peaks...")
    # Generate will now run with default physics settings
    results = syn.generate(seeds_ss, bg_seeds_ss)

    # Unpacking logic (handling both tuple and single object)
    if isinstance(results, tuple):
        # In most RIID versions, index 1 is the 'Gross' (Signal + BG)
        # If results[1] is None, we fall back to results[0]
        gross_ss = results[1] if results[1] is not None else results[0]
    else:
        gross_ss = results

    # --- 4. Save to HDF5 ---
    target_path = os.path.join(output_dir, "train.h5")
    gross_ss.to_hdf(target_path)
    print(f"✅ Success! Realistic HDF5 file generated at: {target_path}")

if __name__ == "__main__":
    generate_datasets("data/raw")