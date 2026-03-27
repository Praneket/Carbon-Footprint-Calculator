# Emission factors (kg CO2 per unit)
FACTORS = {
    "car_km":        0.21,   # per km
    "bike_km":       0.0,
    "bus_km":        0.089,  # per km
    "flights_short": 255,    # per short-haul flight (< 3h)
    "flights_long":  1620,   # per long-haul flight (> 6h)
    "electricity":   0.82,   # per kWh/month → annualised below
    "lpg_kg":        2.98,   # per kg LPG/month
    "diet_vegan":    600,    # kg CO2/year
    "diet_veg":      1000,
    "diet_omnivore": 2000,
    "diet_meat":     3300,
    "waste_kg":      0.5,    # per kg/month
}

NATIONAL_AVG = 7500   # kg CO2/year (India average)
GLOBAL_AVG   = 4800   # kg CO2/year


def calculate(data: dict) -> dict:
    car_km        = float(data.get("car_km", 0))
    bus_km        = float(data.get("bus_km", 0))
    flights_short = float(data.get("flights_short", 0))
    flights_long  = float(data.get("flights_long", 0))
    electricity   = float(data.get("electricity_kwh", 0))
    lpg_kg        = float(data.get("lpg_kg", 0))
    diet          = data.get("diet", "omnivore")
    waste_kg      = float(data.get("waste_kg", 0))

    transport = (
        car_km * FACTORS["car_km"] * 12
        + bus_km * FACTORS["bus_km"] * 12
        + flights_short * FACTORS["flights_short"]
        + flights_long  * FACTORS["flights_long"]
    )
    energy = (electricity * FACTORS["electricity"] + lpg_kg * FACTORS["lpg_kg"]) * 12
    food   = FACTORS.get(f"diet_{diet}", FACTORS["diet_omnivore"])
    waste  = waste_kg * FACTORS["waste_kg"] * 12

    total = transport + energy + food + waste

    if total < 2000:
        score = "Low"
    elif total < 5000:
        score = "Medium"
    else:
        score = "High"

    return {
        "transport": round(transport, 2),
        "energy":    round(energy, 2),
        "food":      round(food, 2),
        "waste":     round(waste, 2),
        "total":     round(total, 2),
        "score":     score,
        "national_avg": NATIONAL_AVG,
        "global_avg":   GLOBAL_AVG,
    }
