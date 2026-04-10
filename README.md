# GammaNet: Deep Learning for Real-Time Radioisotope Identification

[![Deployment Status](https://img.shields.io/badge/Live-Railway-brightgreen)](https://gammanet-production.up.railway.app/)
![PyTorch](https://img.shields.io/badge/PyTorch-1D--CNN-orange)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED)

> Bridging the Sim-to-Real gap in nuclear security: a production-deployed 1D-CNN for automated radioisotope identification from raw NaI(Tl) gamma-ray spectral data.

---

# GammaNet: Deep Learning for Real-Time Radioisotope Identification

[![Deployment Status](https://img.shields.io/badge/Live-Railway-brightgreen)](https://gammanet-production.up.railway.app/)

**Objective:** To bridge the "Sim-to-Real" gap in nuclear security by deploying a 1D-CNN capable of identifying radioisotopes from raw NaI(Tl) spectral data in a production environment.

---

## 01 // Executive Summary

GammaNet is a physics-informed machine learning platform designed to automate the identification of isotopic signatures. By treating gamma-ray spectra as 1D signals rather than static data, the system utilises a 1D Convolutional Neural Network (CNN) to perform automated feature extraction on 1024-channel inputs.

The project demonstrates a full-stack engineering lifecycle: from Physics-Informed Synthetic Data Generation (modeling Gaussian photopeaks and exponential backgrounds) to a Containerized Microservice Deployment.

---

## 02 // Engineering Architecture

### The "Sidecar" Container Strategy

To optimize for cloud deployment, I engineered a Sidecar Process Architecture. Within a single Linux container, the system orchestrates two distinct layers:

- **The Inference Engine (Back-end):** A FastAPI service that manages the PyTorch model lifecycle and handles tensor transformations.
- **The Analysis Terminal (Front-end):** A Streamlit-based "Industrial HUD" that provides operators with real-time interactive visualizations using Plotly.

### Key Technical Challenges Overcome

**Memory-Constrained Inference**
Successfully optimized the 1D-CNN to operate under a 512MB RAM ceiling by utilizing a cpu-only PyTorch build and efficient HDF5 streaming via PyTables, preventing OOM (Out-of-Memory) crashes during model initialization.

**Process Orchestration**
Developed a custom `start.sh` entrypoint to manage asynchronous process start-ups, implementing a health-check handshake to ensure the API is "Warm" before the UI accepts user data.

**Cross-Origin Networking**
Resolved complex internal networking blocks (Error 111/403) by standardizing on a Linux gateway binding (`0.0.0.0`) and implementing a robust CORS policy for internal loopback communication.

---

## 03 // The Physics-ML Pipeline

**1. Synthetic Twin Generation**
Data was generated using the PyRIID framework (Sandia National Laboratories). I implemented a custom "Manual Seed Factory" to simulate realistic NaI detector responses, including Gaussian peak broadening ($FWHM$) and Compton continuum slopes.

**2. 1D-CNN Architecture**
Unlike traditional MLPs, the 1D-CNN uses convolutional kernels as "automated peak finders," identifying local energy correlations regardless of slight gain shifts.

**3. Spectral Calibration**
The UI performs real-time calibration from Channel Index to Energy (keV) using a calculated slope of $3.3135 \text{ keV/ch}$, allowing for scientific validation of the results.

---

## 04 // Tech Stack

| Domain | Tools |
|---|---|
| Deep Learning | PyTorch (1D-CNN), SHAP (XAI Validation) |
| Data Science | NumPy, Pandas, H5Py (HDF5 Serialization) |
| API / Backend | FastAPI, Uvicorn, Pydantic (Data Validation) |
| Frontend | Streamlit, Plotly (Interactive Spectral HUD) |
| DevOps | Docker, Bash Scripting, Railway Cloud |

---

## 05 // Project Structure

```
├── api/
│   └── main.py          # FastAPI: Model loading & REST endpoints
├── models/
│   ├── cnn.py           # PyTorch: 1D-CNN Class with Dimension Guards
│   └── gammanet_v1.pt   # Serialized weights (Trained on 50k spectra)
├── data/
│   └── generate.py      # Physics-informed data generation script
├── notebooks/
│   └── 01_eda.ipynb     # Exploratory Data Analysis & XAI (SHAP)
├── ui.py                # Streamlit: Operator Dashboard
├── start.sh             # Docker Entrypoint: Process Orchestrator
├── Dockerfile           # Multi-layer container definition
└── requirements.txt     # Dependency manifest
```

---

## Acknowledgements

Synthetic data generation powered by [PyRIID](https://github.com/sandialabs/pyriid) — an open-source radiological intelligence framework developed by Sandia National Laboratories.
