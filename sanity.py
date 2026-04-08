import pandas as pd
import numpy as np

train_data = pd.read_hdf("data/raw/train.h5", key="spectra")
test_data = pd.read_hdf("data/raw/test.h5", key="spectra")

print(f"Train Max: {train_data.iloc[0].max():.6f} | Train Mean: {train_data.iloc[0].mean():.6f}")
print(f"Test Max:  {test_data.iloc[0].max():.6f} | Test Mean:  {test_data.iloc[0].mean():.6f}")