def generate_tips(data: dict, result: dict) -> list:
    tips = []
    car_km   = float(data.get("car_km", 0))
    elec     = float(data.get("electricity_kwh", 0))
    diet     = data.get("diet", "omnivore")
    waste_kg = float(data.get("waste_kg", 0))
    flights_short = float(data.get("flights_short", 0))
    flights_long  = float(data.get("flights_long", 0))

    if car_km > 500:
        saving = round(car_km * 0.21 * 12 * 0.3, 1)
        tips.append(f"Reduce car usage by 30% → saves ~{saving} kg CO₂/year. Try carpooling or public transport.")
    if elec > 300:
        saving = round(elec * 0.82 * 12 * 0.2, 1)
        tips.append(f"Switch to LED bulbs & energy-efficient appliances → saves ~{saving} kg CO₂/year.")
    if diet in ("meat", "omnivore"):
        tips.append("Shifting to a plant-rich diet 3 days/week can cut food emissions by up to 40%.")
    if waste_kg > 20:
        saving = round(waste_kg * 0.5 * 12 * 0.5, 1)
        tips.append(f"Composting & recycling half your waste → saves ~{saving} kg CO₂/year.")
    if flights_short > 2:
        tips.append("Consider train travel for short trips — trains emit ~80% less CO₂ than flights.")
    if flights_long > 1:
        tips.append("Offset long-haul flights through certified carbon offset programs.")
    if result["energy"] > 3000:
        tips.append("Consider rooftop solar panels to drastically cut your energy emissions.")
    if not tips:
        tips.append("Great job! Your footprint is already low. Keep up the sustainable habits.")
    return tips
