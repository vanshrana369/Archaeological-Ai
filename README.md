# Archaeological-Ai

An AI system that discovers hidden archaeological sites worldwide using satellite imagery, computer vision, and machine learning. Buried civilizations leave invisible fingerprints on the surface - crop marks, soil anomalies, thermal signatures - this platform reads them at global scale.

---

## What It Does

- Fetches free satellite imagery (Sentinel-2, Landsat) for any region on Earth
- Uses a Computer Vision model to detect archaeological anomalies in satellite bands
- Cross-references terrain, elevation, river proximity, and historical trade routes
- 4 AI agents analyze and generate a full discovery report automatically
- Interactive World map showing probability heatmap of undiscovered sites
- Researchers can validate or reject findings, improving the model over time

---

## How Buried Sites Are Detected

| Signal | What It Means |
|--------|---------------|
| Crop marks | Plants grow differently above buried walls vs open soil |
| Soil marks | Different colored earth where structures once stood |
| Thermal anomalies | Stone retains heat differently than surrounding soil |
| Topographic patterns | Ancient civilizations built near water, on elevated ground |
| Vegetation anomalies | Certain plants grow only on disturbed or enriched soil |
| Multispectral bands | Infrared and SWIR bands reveal what visible light cannot |

---

## 4 AI Agents (LangGraph)

| Agent | Role |
|-------|------|
| Agent 1 - Satellite Scanner | Fetches and preprocesses satellite imagery for a target region |
| Agent 2 - Anomaly Detector | CV model flags suspicious patterns in multispectral bands |
| Agent 3 - Context Analyzer | Cross-references terrain, history, known civilizations nearby |
| Agent 4 - Report Generator | Produces discovery brief with coordinates, confidence score, and reasoning |

---

## Data Sources (All Free)

| Source | Data |
|--------|------|
| ESA Sentinel-2 | Multispectral imagery, updated every 5 days |
| Sentinel-1 SAR | Sees through cloud cover and dense vegetation |
| NASA Landsat | 40 years of historical imagery for change detection |
| NASA SRTM | Global elevation and terrain data |
| Pleiades / OpenContext | 35,000+ known ancient sites for model training |

---

## Tech Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, APScheduler
- **ML:** PyTorch, torchvision, scikit-learn, rasterio, geopandas
- **Agents:** LangGraph, Groq (Llama 3.1)
- **Frontend:** React, Leaflet.js
- **Deployment:** Render (backend), Vercel (frontend)

---

## Project Structure

```
archaeological-ai/
├── backend/          FastAPI server, API endpoints, scheduler
├── ml/               CV model, site detector, heatmap generator
├── agents/           4 LangGraph AI agents + pipeline
├── data_pipeline/    Satellite data fetching, known sites loader
├── data/             Raw satellite imagery, site databases
├── outputs/          Generated reports, heatmaps, PDFs
└── frontend/         React dashboard with interactive world map
```

---

## Task List

### Phase 1 - Data Pipeline
- [x] Fetch known archaeological sites from Pleiades/OpenContext API
- [ ] Store sites in PostgreSQL with coordinates, civilization, period
- [ ] Connect to Google Earth Engine and fetch Sentinel-2 imagery
- [ ] Download NASA SRTM elevation data for terrain features
- [ ] Build preprocessing pipeline (band extraction, normalization, tiling)

### Phase 2 - ML Model
- [ ] Prepare training dataset from known site coordinates + satellite imagery
- [ ] Build negative examples (non-site areas with similar terrain)
- [ ] Train CNN / Vision Transformer to detect site anomalies
- [ ] Add confidence scoring (0-100%) per prediction
- [ ] Backtest model against known sites to measure accuracy
- [ ] Generate probability heatmap for any input region

### Phase 3 - AI Agents
- [ ] Agent 1: Satellite scanner (fetch + preprocess imagery for target region)
- [ ] Agent 2: Anomaly detector (run CV model, extract flagged coordinates)
- [ ] Agent 3: Context analyzer (terrain, river proximity, historical cross-reference)
- [ ] Agent 4: Report generator (discovery brief with coordinates + reasoning)
- [ ] Wire all 4 agents into LangGraph pipeline
- [ ] Automated weekly scan of high-probability regions

### Phase 4 - Backend API
- [ ] FastAPI server with PostgreSQL
- [ ] /scan endpoint (trigger scan for a region)
- [ ] /discoveries endpoint (return all flagged sites)
- [ ] /heatmap endpoint (return probability heatmap for a region)
- [ ] /report endpoint (latest AI-generated discovery report)
- [ ] /validate endpoint (researchers confirm or reject a finding)
- [ ] PDF export of discovery reports

### Phase 5 - Frontend Dashboard
- [ ] Interactive world map (Leaflet.js)
- [ ] Probability heatmap overlay on map
- [ ] Click any flagged site to see satellite image + AI reasoning
- [ ] Researcher validation panel (confirm / reject findings)
- [ ] Discovery report viewer with PDF download
- [ ] Region search - enter any location to trigger a scan

### Phase 6 - Deployment
- [ ] Deploy backend on Render
- [ ] Deploy frontend on Vercel
- [ ] Connect PostgreSQL (Render managed DB)
- [ ] Set up weekly automated scan scheduler
- [ ] Write project documentation

---

## Inspiration

In 2018, LiDAR revealed an entire Mayan civilization hidden under jungle in Guatemala - 60,000 structures invisible for 1,000 years, found in weeks. That was expensive, limited-coverage technology used by only 50 research teams globally.

Sentinel-2 covers the entire Earth every 5 days for free. Nobody has built a serious ML system on top of it for global archaeological discovery. Until now.

---

## Status

In Development

---

## Author

Vansh Rana - https://github.com/vanshrana369
