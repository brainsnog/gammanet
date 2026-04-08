import torch
import torch.nn as nn
import torch.nn.functional as F

class GammaNet1D(nn.Module):
    def __init__(self, num_classes=5, num_channels=1024):
        super(GammaNet1D, self).__init__()
        
        # Convolutional Layer 1: Detecting sharp edges/peaks
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=32, kernel_size=11, stride=1, padding=5)
        self.bn1 = nn.BatchNorm1d(32)
        
        # Convolutional Layer 2: Detecting peak clusters
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=11, stride=1, padding=5)
        self.bn2 = nn.BatchNorm1d(64)
        
        # Pooling to reduce dimensionality and handle slight energy shifts
        self.pool = nn.MaxPool1d(kernel_size=2)
        
        # Fully Connected Layers
        # After two MaxPools (2x2), 1024 channels become 256
        self.fc1 = nn.Linear(64 * 256, 128)
        self.dropout = nn.Dropout(0.3) # Prevent overfitting
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        # Only unsqueeze if the data is 2D [Batch, 1024]
        # If it's already 3D [Batch, 1, 1024], skip this!
        if x.dim() == 2:
            x = x.unsqueeze(1)
        elif x.dim() == 4:
            # Emergency fix if SHAP sends [10, 1, 1, 1024]
            x = x.squeeze(2)
        
        # Line 30: Now x will be exactly [Batch, 1, 1024]
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        
        # Flatten for the dense layers
        x = x.view(x.size(0), -1)
        
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x) 
        
        return x