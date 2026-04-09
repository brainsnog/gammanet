#!/bin/bash
# Start the API (the brain) in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the Dashboard (the face)
streamlit run ui.py --server.port 8501 --server.address 0.0.0.0