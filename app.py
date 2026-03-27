from flask import Flask, request, render_template, jsonify, send_file
import sqlite3, os, io, json
from datetime import datetime
from utils.calculator import calculate
from utils.tips import generate_tips

app = Flask(__name__)
DB = os.path.join("data", "carbon_data.db")

# Ensure data dir + DB table exist at import time (works with gunicorn)
os.makedirs("data", exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


REQUIRED_COLS = {
    "id", "date", "name", "car_km", "bus_km", "flights_short", "flights_long",
    "electricity_kwh", "lpg_kg", "diet", "waste_kg",
    "transport", "energy", "food", "waste", "total", "score"
}

CREATE_SQL = """
    CREATE TABLE emissions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        date            TEXT,
        name            TEXT,
        car_km          REAL, bus_km REAL,
        flights_short   INTEGER, flights_long INTEGER,
        electricity_kwh REAL, lpg_kg REAL,
        diet            TEXT, waste_kg REAL,
        transport       REAL, energy REAL,
        food            REAL, waste  REAL,
        total           REAL, score  TEXT
    )
"""

def init_db():
    with get_db() as conn:
        existing = {row[1] for row in conn.execute("PRAGMA table_info(emissions)")}
        if not REQUIRED_COLS.issubset(existing):
            conn.execute("DROP TABLE IF EXISTS emissions")
            conn.execute(CREATE_SQL)

# Called at module load so gunicorn workers initialise the DB too
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate_route():
    try:
        data = request.form.to_dict()
        result = calculate(data)
        tips   = generate_tips(data, result)

        with get_db() as conn:
            conn.execute("""
                INSERT INTO emissions
                (date,name,car_km,bus_km,flights_short,flights_long,
                 electricity_kwh,lpg_kg,diet,waste_kg,
                 transport,energy,food,waste,total,score)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                data.get("name", "Anonymous"),
                data.get("car_km", 0), data.get("bus_km", 0),
                data.get("flights_short", 0), data.get("flights_long", 0),
                data.get("electricity_kwh", 0), data.get("lpg_kg", 0),
                data.get("diet", "omnivore"), data.get("waste_kg", 0),
                result["transport"], result["energy"],
                result["food"], result["waste"],
                result["total"], result["score"]
            ))

        return render_template("results.html", result=result, tips=tips,
                               name=data.get("name", "Anonymous"),
                               data=json.dumps(result))
    except Exception as e:
        app.logger.error(f"calculate error: {e}")
        return render_template("index.html", error=f"Something went wrong: {e}")


@app.route("/history")
def history():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,date,name,total,score FROM emissions ORDER BY id DESC LIMIT 20"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/history/analytics")
def history_analytics():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,date,name,transport,energy,food,waste,total,score,diet FROM emissions ORDER BY id ASC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/history/page")
def history_page():
    return render_template("history.html")


@app.route("/export_csv")
def export_csv():
    try:
        import pandas as pd
        with get_db() as conn:
            df = pd.read_sql_query("SELECT * FROM emissions", conn)
        df.to_csv(os.path.join("data", "carbon_emissions.csv"), index=False)
        return jsonify({"message": "Exported to data/carbon_emissions.csv"})
    except ImportError:
        return jsonify({"error": "pandas not installed"}), 500


@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib import colors

        result = request.json.get("result", {})
        tips   = request.json.get("tips", [])
        name   = request.json.get("name", "Anonymous")

        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=A4)
        w, h = A4

        c.setFillColor(colors.HexColor("#16a34a"))
        c.rect(0, h - 80, w, 80, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(40, h - 50, "🌿 Carbon Footprint Report")
        c.setFont("Helvetica", 12)
        c.drawString(40, h - 68, f"Generated for: {name}")

        c.setFillColor(colors.black)
        y = h - 120
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Emission Breakdown (kg CO₂/year)")
        y -= 25
        c.setFont("Helvetica", 12)
        for key in ("transport", "energy", "food", "waste", "total"):
            label = key.capitalize()
            val   = result.get(key, 0)
            c.drawString(60, y, f"{label}: {val} kg CO₂")
            y -= 20

        y -= 10
        score = result.get("score", "N/A")
        score_colors = {"Low": "#16a34a", "Medium": "#d97706", "High": "#dc2626"}
        c.setFillColor(colors.HexColor(score_colors.get(score, "#000000")))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(40, y, f"Carbon Score: {score}")
        y -= 30

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Personalized Eco-Tips")
        y -= 20
        c.setFont("Helvetica", 11)
        for tip in tips:
            words = tip
            if len(words) > 90:
                words = words[:90] + "..."
            c.drawString(50, y, f"• {words}")
            y -= 18
            if y < 60:
                c.showPage()
                y = h - 60

        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.grey)
        c.drawString(40, 30, "Carbon Footprint Calculator | Sustainability Analytics")
        c.save()
        buf.seek(0)
        return send_file(buf, mimetype="application/pdf",
                         as_attachment=True, download_name="carbon_report.pdf")
    except ImportError:
        return jsonify({"error": "reportlab not installed"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
