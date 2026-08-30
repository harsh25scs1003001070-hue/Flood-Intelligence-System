# 🌊 Cascading Disaster Intelligence & Resource Allocation Platform

> **Predict the Cascade → Optimize the Response → Act Before Failure Spreads**

An **AI + GIS prototype** built for **Smart India Hackathon 2026** to support flood and extreme-rainfall disaster response.

The idea is simple: a flood is rarely an isolated problem. Heavy rainfall can lead to flooding, road blockage, village isolation, hospital-access problems, and emergency resource shortages. Instead of only detecting the hazard, our platform connects **risk prediction → cascading impact analysis → priority assessment → resource allocation** in one command center.

---

## 🚀 What the Prototype Does

```text
Rainfall Data
     ↓
1h / 3h / 6h / 12h / 24h Features
     ↓
XGBoost Flood-Risk Model
     ↓
Flood Risk Score
     ↓
Cascading Impact Analysis
     ↓
Priority Assessment
     ↓
Emergency Resource Allocation
     ↓
Disaster Command Center
```

The current prototype focuses on **flood / extreme-rainfall scenarios** and uses **simulation inputs** for the demo. Live-data integration is planned as a future phase.

---

## 🧠 AI / ML

The current flood-risk baseline uses **XGBoost** with five rainfall features:

- `rainfall_1h_mm`
- `rainfall_3h_mm`
- `rainfall_6h_mm`
- `rainfall_12h_mm`
- `rainfall_24h_mm`

### Training data

For the current prototype, we used two historical Bihar flood events:

- **02 September 2022**
- **27 September 2024**

Rainfall features were derived from **NASA GPM IMERG** data. Flood labels were created from **NRSC/ISRO satellite-derived flood inundation maps**, georeferenced and processed using QGIS and geospatial tooling.

The resulting model is saved as:

```text
backend/models/flood_risk_model.joblib
```

> ⚠️ **Prototype note:** the current model is a baseline trained on a limited number of historical events. It is not presented as a production-validated flood forecasting model.

---

## 🏗️ System Architecture

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- Leaflet / React-Leaflet

### Backend
- FastAPI
- Python
- REST API

### ML & Geospatial
- XGBoost
- scikit-learn
- GeoPandas
- Shapely
- QGIS
- OpenStreetMap

### Response Intelligence
- Cascading impact analysis
- Priority assessment
- Ambulance allocation
- Rescue-team allocation

---

## 📁 Project Structure

```text
SIH-Flood-Intelligence/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── main.py
│   ├── disaster_pipeline.py
│   ├── hazard_engine.py
│   ├── cascade_engine.py
│   ├── priority_engine.py
│   ├── resource_optimizer.py
│   ├── ml_predictor.py
│   ├── requirements.txt
│   └── models/
│       └── flood_risk_model.joblib
│
├── aiml/
│   ├── src/
│   └── data/
│       └── processed/
│
└── README.md
```

---

## ▶️ Run the Prototype Locally

### 1. Start the backend

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 2. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

## 🔌 Main API

### `POST /api/disaster/analyze`

Example request:

```json
{
  "mode": "simulation",
  "rainfall_mm": 180,
  "duration_hours": 4,
  "water_level_m": 8,
  "rainfall_1h_mm": 60,
  "rainfall_3h_mm": 120,
  "rainfall_6h_mm": 180,
  "rainfall_12h_mm": 240,
  "rainfall_24h_mm": 310
}
```

The response contains:

- flood risk score
- hazard level
- impact on roads, villages and hospitals
- priority assessment
- resource optimization
- resource gaps

---

## 🗺️ Why This Approach?

Traditional disaster workflows often follow:

**Detect → Alert → Respond**

Our approach is:

**Detect → Predict Cascade → Optimize Resources → Recommend Action**

The main goal is not only to answer **“Where is the disaster?”**, but also:

> **“What may fail next, and where should limited emergency resources move now?”**

---

## ⚠️ Current Limitations

This is an **MVP / prototype**. The current version has:

- a limited historical training set
- strong class imbalance in flood labels
- simulation-based input for the main demo
- prototype infrastructure/resource data
- no full live rainfall or river-level ingestion yet

These limitations are intentional parts of the next development stage rather than hidden assumptions.

---

## 🛣️ Roadmap

### Phase 1 ✅
Flood intelligence + cascading-impact prototype

### Phase 2 🚧
More advanced resource optimization and evacuation routing

### Phase 3 🔜
Near-real-time rainfall / river data integration

### Phase 4 🔜
Expansion to multiple disaster types

---

## 🎯 Target Users

The platform is designed as decision support for:

- District Disaster Management Authorities
- Emergency Operations Centers
- NDRF / SDRF
- Fire & Rescue Services
- Police
- Hospitals
- Municipal authorities

The system is intended to **support human decision-making**, not replace emergency responders.

---

## 🏆 Smart India Hackathon 2026

**Team:** Innovatrix  
**Project:** Cascading Disaster Intelligence & Resource Allocation Platform  
**Theme:** Disaster Management  
**Category:** Software

---

## 🤝 Team Note

This repository contains our working prototype and the experimentation behind it. The current goal is to demonstrate an end-to-end flow from **real-world rainfall data to ML risk estimation and actionable disaster-response intelligence**.

Built with a focus on **early detection, cascading-risk awareness, and better use of limited emergency resources.**
