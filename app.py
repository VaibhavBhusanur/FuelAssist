from flask import Flask, request, jsonify
from flask_cors import CORS
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
CORS(app)

# In-memory storage
rides = {}
ride_id_counter = 1

# Vehicle database (simplified example)
vehicle_data = {
    "2018 Splendor": {"tank_capacity": 8, "mileage": 60},  # mileage in km/l
    "2020 Activa": {"tank_capacity": 5, "mileage": 50},
}

# Haversine formula to calculate distance between two GPS points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    distance = R * c
    return distance  # in km

@app.route("/")
def home():
    return "FuelMate Backend Running 🚀"

@app.route("/start_ride", methods=["POST"])
def start_ride():
    global ride_id_counter
    
    data = request.get_json(force=True)
    vehicle = data.get("vehicle")
    fuel_filled = data.get("fuel_filled")
    
    if vehicle not in vehicle_data:
        return jsonify({"error": "Vehicle not found"}), 400

    ride_id = ride_id_counter
    rides[ride_id] = {
        "vehicle": vehicle,
        "fuel_filled": fuel_filled,
        "fuel_remaining": fuel_filled,
        "locations": [],  # to store GPS points
        "distance": 0,    # total distance traveled
        "avg_speed": 0,   # average speed
        "speed_samples": []  # store speeds for calculation
    }
    ride_id_counter += 1

    return jsonify({
        "message": "Ride started successfully",
        "ride_id": ride_id,
        "vehicle": vehicle,
        "fuel_filled": fuel_filled
    })

@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.get_json(force=True)
    ride_id = data.get("ride_id")
    lat = data.get("latitude")
    lon = data.get("longitude")
    speed = data.get("speed")  # km/h

    if ride_id not in rides:
        return jsonify({"error": "Ride not found"}), 404

    ride = rides[ride_id]

    # Update distance if there is a previous location
    if ride["locations"]:
        prev_lat, prev_lon = ride["locations"][-1]
        distance_increment = haversine(prev_lat, prev_lon, lat, lon)
        ride["distance"] += distance_increment

        # Estimate fuel used
        vehicle = ride["vehicle"]
        mileage = vehicle_data[vehicle]["mileage"]
        fuel_used = distance_increment / mileage
        ride["fuel_remaining"] -= fuel_used
        if ride["fuel_remaining"] < 0:
            ride["fuel_remaining"] = 0

    # Store new location and speed
    ride["locations"].append((lat, lon))
    ride["speed_samples"].append(speed)
    ride["avg_speed"] = sum(ride["speed_samples"]) / len(ride["speed_samples"])

    return jsonify({
        "message": "Location updated",
        "ride_id": ride_id,
        "total_distance": round(ride["distance"], 2),
        "fuel_remaining": round(ride["fuel_remaining"], 2),
        "avg_speed": round(ride["avg_speed"], 2)
    })

@app.route("/end_ride", methods=["POST"])
def end_ride():
    data = request.get_json(force=True)
    ride_id = data.get("ride_id")

    if not ride_id or ride_id not in rides:
        return jsonify({"error": "Ride not found"}), 404

    ride = rides.pop(ride_id)
    return jsonify({
        "message": "Ride ended successfully",
        "ride_id": ride_id,
        "vehicle": ride["vehicle"],
        "fuel_filled": ride["fuel_filled"],
        "fuel_remaining": round(ride["fuel_remaining"], 2),
        "distance_traveled": round(ride["distance"], 2),
        "avg_speed": round(ride["avg_speed"], 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
