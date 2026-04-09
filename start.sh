#!/bin/bash

# 1. Start the API from the 'api' subfolder
# Use api.main:app to tell uvicorn to look in api/main.py
uvicorn api.main:app --host 127.0.0.1 --port 8000 &

# 2. Give the model time to load into RAM
echo "INITIALIZING_BRAIN_FROM_SUBDIRECTORY..."
sleep 15

# 3. Start the Dashboard from the root
streamlit run ui.py --server.port 8501 --server.address 0.0.0.0