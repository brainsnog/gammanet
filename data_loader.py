import torch
from torch.utils.data import Dataset, DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from riid.data.sampleset import SampleSet
import numpy as np

def get_dataloaders(file_path, batch_size=32):
    # 1. Load SampleSet 
    ss = SampleSet()
    
    # Try this specific naming convention
    try:
        ss.load_hdf(file_path)
    except AttributeError:
        # If that fails, we use the "last resort" 
        # which is the direct to_sample_set conversion 
        # (Assuming you saved it via a pandas-compatible way)
        import pandas as pd
        ss.spectra = pd.read_hdf(file_path, key="spectra")
        ss.sources = pd.read_hdf(file_path, key="sources")
        ss.info = pd.read_hdf(file_path, key="info")

    # 2. Extract spectra (X) and one-hot labels (y)
    X = ss.spectra.values.astype(np.float32)
    y = ss.sources.values.astype(np.float32)
    
    # 3. Train/Val Split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 4. Convert to Tensors
    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    val_ds = TensorDataset(torch.from_numpy(X_val), torch.from_numpy(y_val))
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    
    return train_loader, val_loader