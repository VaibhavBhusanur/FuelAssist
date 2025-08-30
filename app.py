from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Vehicle data with tank capacity (liters) and mileage (km/liter)
vehicles = {
    "splendor2018": {"tank_capacity": 11, "mileage": 60},   # ~60 km/l
    "activa2020": {"tank_capacity": 5.3, "mileage": 45}     # ~45 km/l
}

PETROL_PRICE = 100  # Rs per liter

@app.route("/start_ride", methods=["POST"])
def start_ride():
    data = request.json
    vehicle = data.get("vehicle")
    fuel_rs = data.get("fuel")        # money spent in Rs
    distance = data.get("distance", 50)  # requested distance (default 50 km)

    # Basic validation
    if not vehicle or fuel_rs is None:
        return jsonify({"error": "Vehicle and fuel required"}), 400
    if vehicle not in vehicles:
        return jsonify({"error": "Vehicle not found"}), 404

    # Vehicle info
    tank_capacity = vehicles[vehicle]["tank_capacity"]
    mileage = vehicles[vehicle]["mileage"]

    # Fuel calculations
    fuel_liters = fuel_rs / PETROL_PRICE
    max_distance = fuel_liters * mileage

    if distance > max_distance:
        # Not enough fuel for requested distance
        distance_travelled = max_distance
        fuel_used = fuel_liters
        fuel_left = 0
    else:
        distance_travelled = distance
        fuel_used = distance_travelled / mileage
        fuel_left = fuel_liters - fuel_used

    fuel_percent = (fuel_left / tank_capacity) * 100

    return jsonify({
        "vehicle": vehicle,
        "fuel_filled_rs": fuel_rs,
        "fuel_in_liters": round(fuel_liters, 2),
        "distance_requested": distance,
        "distance_travelled": round(distance_travelled, 2),
        "mileage": mileage,
        "fuel_used": round(fuel_used, 2),
        "fuel_left": round(fuel_left, 2),
        "fuel_percent": round(fuel_percent, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
