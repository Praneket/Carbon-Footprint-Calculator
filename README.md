# 🌿 EcoTrack — Carbon Footprint Calculator

A production-ready Flask web app for calculating, visualising, and reducing your carbon footprint.

## Folder Structure
```
Carbon Footprint Calculator/
├── app.py                  # Flask routes + DB init
├── utils/
│   ├── calculator.py       # Emission calculation engine
│   └── tips.py             # Personalised eco-tips engine
├── templates/
│   ├── index.html          # Input form (dark mode, responsive)
│   └── results.html        # Dashboard with Chart.js + PDF download
├── static/
│   └── style.css           # Custom styles + dark mode
├── pipeline/
│   └── export_to_powerbi.py  # SQLite → CSV export for Power BI
├── data/
│   ├── carbon_data.db      # SQLite database (auto-created)
│   └── carbon_emissions.csv
├── requirements.txt
├── Procfile
└── .env
```

## Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app
python app.py

# 3. Open in browser
http://localhost:5000
```

## Power BI Dashboard Setup

1. Run the export script:
   ```bash
   python pipeline/export_to_powerbi.py
   ```
2. Open Power BI Desktop → **Get Data → Text/CSV** → select `data/carbon_emissions.csv`
3. Build visuals:
   - **Card**: Total emissions (sum of `total`)
   - **Donut chart**: `transport`, `energy`, `food`, `waste` columns
   - **Bar chart**: Average `total` by `score` category
   - **Line chart**: `total` over `date` for trend tracking

## Deploy to Render

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `gunicorn app:app`
5. Add env var: `PORT=10000`

## Features
- ✅ Transport, energy, food, waste inputs
- ✅ Annual CO₂ calculation with realistic emission factors
- ✅ Carbon score: Low / Medium / High
- ✅ Comparison vs India national avg & global avg
- ✅ Personalised eco-tips (rule-based engine)
- ✅ Chart.js doughnut + bar charts
- ✅ PDF report download (reportlab)
- ✅ SQLite data persistence + history view
- ✅ CSV export for Power BI
- ✅ Dark mode toggle
- ✅ Mobile responsive (Bootstrap 5)
