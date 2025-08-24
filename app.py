from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

# Use environment variables (Render will provide DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def calculate_footprint(electricity_kwh, fuel_liters, waste_kg):
    elec_factor = 0.82
    fuel_factor = 2.31
    waste_factor = 1.8
    return (electricity_kwh * elec_factor) + (fuel_liters * fuel_factor) + (waste_kg * waste_factor)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_form():
    electricity = float(request.form["electricity_kwh"])
    fuel = float(request.form["fuel_liters"])
    waste = float(request.form["waste_kg"])

    footprint = calculate_footprint(electricity, fuel, waste)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO carbon_data (electricity_kwh, fuel_liters, waste_kg, footprint_kgco2)
        VALUES (%s, %s, %s, %s)
    """, (electricity, fuel, waste, footprint))
    conn.commit()
    cur.close()
    conn.close()

    return f"Carbon Footprint: {footprint} kg CO2"

@app.route("/add_data", methods=["POST"])
def add_data():
    data = request.json
    electricity = data["electricity_kwh"]
    fuel = data["fuel_liters"]
    waste = data["waste_kg"]

    footprint = calculate_footprint(electricity, fuel, waste)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO carbon_data (electricity_kwh, fuel_liters, waste_kg, footprint_kgco2)
        VALUES (%s, %s, %s, %s)
    """, (electricity, fuel, waste, footprint))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data added successfully", "carbon_footprint": footprint})

@app.route("/get_data", methods=["GET"])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM carbon_data")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    # Render expects the port to come from $PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
