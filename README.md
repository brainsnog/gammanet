# GammaNet: Deep Learning for Real-Time Radioisotope Identification

[![Deployment Status](https://img.shields.io/badge/Live-Railway-brightgreen)](https://gammanet-production.up.railway.app/)
![PyTorch](https://img.shields.io/badge/PyTorch-1D--CNN-orange)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED)

> Bridging the Sim-to-Real gap in nuclear security: a production-deployed 1D-CNN for automated radioisotope identification from raw NaI(Tl) gamma-ray spectral data.

---

## Executive Summary

GammaNet is a physics-informed machine learning platform that automates the identification of isotopic signatures. By treating gamma-ray spectra as 1D signals rather than static feature vectors, it employs a 1D Convolutional Neural Network operating on 1024-channel inputs — allowing convolutional kernels to act as learned, automated peak finders.

The project demonstrates a full-stack ML engineering lifecycle: from **Physics-Informed Synthetic Data Generation** (modelling Gaussian photopeaks and exponential Compton backgrounds) through to **Containerised Microservice Deployment** on Railway Cloud.

---

## Engineering Architecture

### The Sidecar Container Strategy

To optimise for cloud deployment under tight resource constraints, GammaNet uses a **Sidecar Process Architecture** — two distinct service layers orchestrated within a single Linux container:

| Layer | Component | Role |
|---|---|---|
| Back-end | FastAPI + Uvicorn | Model lifecycle management, tensor transformation, REST endpoints |
| Front-end | Streamlit + Plotly | Real-time interactive spectral visualisation ("Industrial HUD") |

### Key Technical Challenges

**Memory-Constrained Inference**
Optimised the 1D-CNN to operate under a 512 MB RAM ceiling by using a `cpu-only` PyTorch build and efficient HDF5 streaming via PyTables, preventing OOM crashes during model initialisation.

**Process Orchestration**
Developed a custom `start.sh` entrypoint to manage asynchronous process start-up, implementing a health-check handshake that gates the UI until the API is confirmed warm.

**Cross-Origin Networking**
Resolved internal networking blocks (Error 111/403) by standardising on Linux gateway binding (`0.0.0.0`) and implementing a robust CORS policy for internal loopback communication.

---

## The Physics-ML Pipeline

### 1. Synthetic Twin Generation
Data was generated using the [PyRIID](https://github.com/sandialabs/pyriid) framework (Sandia National Laboratories). A custom **Manual Seed Factory** simulates realistic NaI(Tl) detector responses, including Gaussian peak broadening (FWHM) and Compton continuum slopes across a training corpus of 50,000 spectra.

### 2. 1D-CNN Architecture
Unlike traditional MLPs operating on flat feature vectors, the 1D-CNN uses convolutional kernels as automated peak finders — identifying local energy correlations that remain robust against slight detector gain shifts.

### 3. Spectral Calibration
The operator UI performs real-time calibration from channel index to energy (keV) using a calculated slope of **3.3135 keV/ch**, enabling scientific validation of classification results against known isotope libraries.

---

## Tech Stack

| Domain | Tools |
|---|---|
| Deep Learning | PyTorch (1D-CNN), SHAP (XAI validation) |
| Data Science | NumPy, Pandas, H5Py (HDF5 serialisation) |
| API / Back-end | FastAPI, Uvicorn, Pydantic |
| Front-end | Streamlit, Plotly |
| DevOps | Docker, Bash scripting, Railway Cloud |

---

## Project Structure

```
gammanet/
├── api/
│   └── main.py              # FastAPI: model loading & REST endpoints
├── models/
│   ├── cnn.py               # PyTorch: 1D-CNN class with dimension guards
│   └── gammanet_v1.pt       # Serialised weights (trained on 50k spectra)
├── data/
│   └── generate.py          # Physics-informed data generation script
├── notebooks/
│   └── 01_eda.ipynb         # Exploratory data analysis & XAI (SHAP)
├── ui.py                    # Streamlit: operator dashboard
├── start.sh                 # Docker entrypoint: process orchestrator
├── Dockerfile               # Multi-layer container definition
└── requirements.txt         # Dependency manifest
```

---

## Deployment

The live deployment is hosted on Railway. The container entrypoint (`start.sh`) handles service orchestration: the FastAPI inference engine starts first, and the Streamlit UI is held until the health-check confirms the API is ready to serve requests.

**Live:** [gammanet-production.up.railway.app](https://gammanet-production.up.railway.app/)

To run locally:

```bash
docker build -t gammanet .
docker run -p 8501:8501 -p 8000:8000 gammanet
```

---

## Acknowledgements

Synthetic data generation powered by [PyRIID](https://github.com/sandialabs/pyriid) — an open-source radiological intelligence framework developed by Sandia National Laboratories.
