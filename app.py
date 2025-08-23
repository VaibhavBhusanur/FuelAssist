from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

vehicles = {
    "splendor2018": {"tank_capacity": 11},
    "activa2020": {"tank_capacity": 5.3}
}

PETROL_PRICE = 100  # Rs per liter

@app.route("/start_ride", methods=["POST"])
def start_ride():
    data = request.json
    vehicle = data.get("vehicle")
    fuel_rs = data.get("fuel")

    if not vehicle or not fuel_rs:
        return jsonify({"error": "Vehicle and fuel required"}), 400

    fuel_liters = fuel_rs / PETROL_PRICE
    tank_capacity = vehicles.get(vehicle, {}).get("tank_capacity", 10)

    distance = 50  # dummy
    mileage = distance / fuel_liters
    fuel_used = distance / mileage
    fuel_left = tank_capacity - fuel_used
    fuel_percent = (fuel_left / tank_capacity) * 100

    return jsonify({
        "vehicle": vehicle,
        "fuel_filled_rs": fuel_rs,
        "fuel_in_liters": round(fuel_liters, 2),
        "distance": distance,
        "mileage": round(mileage, 2),
        "fuel_used": round(fuel_used, 2),
        "fuel_left": round(fuel_left, 2),
        "fuel_percent": round(fuel_percent, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
