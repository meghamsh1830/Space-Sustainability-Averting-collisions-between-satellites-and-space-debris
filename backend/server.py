import requests
import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from sklearn.mixture import GaussianMixture
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Space-Track.org credentials
SPACE_TRACK_USERNAME = "vilok2006@gmail.com"
SPACE_TRACK_PASSWORD = "Vilok_123456789"
TLE_API_URL = "https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{}/orderby/ORDINAL%20asc/format/tle"

def fetch_tle_data(norad_ids):
    """Fetch TLE data for given NORAD IDs."""
    with requests.Session() as session:
        login_url = "https://www.space-track.org/ajaxauth/login"
        login_response = session.post(
            login_url, data={"identity": SPACE_TRACK_USERNAME, "password": SPACE_TRACK_PASSWORD}
        )
        if login_response.status_code != 200:
            raise Exception("Failed to log in to space-track.org")

        tle_data = {}
        for norad_id in norad_ids:
            response = session.get(TLE_API_URL.format(norad_id))
            if response.status_code == 200:
                tle_lines = response.text.strip().split("\n")
                if len(tle_lines) >= 2:
                    tle_data[norad_id] = tle_lines
        return tle_data

def tle_to_position_velocity(line1, line2, current_time):
    """Converts TLE lines to position and velocity in ECI frame."""
    satellite = Satrec.twoline2rv(line1, line2)
    jd, fr = jday(current_time.year, current_time.month, current_time.day,
                  current_time.hour, current_time.minute, current_time.second)
    e, position, velocity = satellite.sgp4(jd, fr)

    if e == 0:  # No error
        return np.array(position), np.array(velocity)
    else:
        return None, None

def calculate_relative_metrics(pos1, vel1, pos2, vel2):
    """Calculates relative position, velocity, and speed."""
    relative_position = np.array(pos1) - np.array(pos2)
    relative_velocity = np.array(vel1) - np.array(vel2)
    distance = np.linalg.norm(relative_position)
    relative_speed = np.linalg.norm(relative_velocity)
    return distance, relative_speed

def generate_uncertainty_samples(mean, cov, n_samples=1000):
    """Generate random uncertainty samples."""
    return np.random.multivariate_normal(mean, cov, n_samples)

def eci_to_lat_lon(position):
    """Converts ECI coordinates to latitude and longitude."""
    r = np.linalg.norm(position)
    lat = np.arcsin(position[2] / r) * (180 / np.pi)  # Latitude in degrees
    lon = np.arctan2(position[1], position[0]) * (180 / np.pi)  # Longitude in degrees
    lon = (lon + 360) % 360  # Normalize longitude to [0, 360)
    return lat, lon

@app.route('/satellite-collision-probability', methods=['POST'])
def satellite_collision_probability():
    """API endpoint for satellite collision probability calculation."""
    data = request.get_json()

    if not data or 'target_norad_id' not in data:
        return jsonify({"error": "Missing target NORAD ID", "status": "failed"}), 400

    try:
        dataset_file = "data/satellites_norad_ids.txt"
        with open(dataset_file, "r") as f:
            norad_ids = [line.strip() for line in f.readlines()]

        target_norad_id = str(data['target_norad_id'])
        if target_norad_id not in norad_ids:
            return jsonify({"error": f"NORAD ID {target_norad_id} is not in the dataset", "status": "failed"}), 404

        tle_data = fetch_tle_data(norad_ids)

        current_time = datetime.utcnow()
        satellites = {}
        for norad_id, tle in tle_data.items():
            satellites[norad_id] = Satrec.twoline2rv(tle[0], tle[1])

        target_sat = satellites[target_norad_id]
        highest_collision = None

        # Iterate through the next 7 days
        for day_offset in range(7):
            time_to_check = current_time + timedelta(days=day_offset)
            jd, fr = jday(time_to_check.year, time_to_check.month, time_to_check.day,
                          time_to_check.hour, time_to_check.minute, time_to_check.second)

            _, target_pos, target_vel = target_sat.sgp4(jd, fr)

            for norad_id, satellite in satellites.items():
                if norad_id == target_norad_id:
                    continue

                error, pos, vel = satellite.sgp4(jd, fr)
                if error != 0:
                    continue

                target_samples = generate_uncertainty_samples(target_pos, np.eye(3) * 0.1)
                satellite_samples = generate_uncertainty_samples(pos, np.eye(3) * 0.1)

                gmm = GaussianMixture(n_components=2, covariance_type="full")
                gmm.fit(np.vstack([target_samples, satellite_samples]))
                prob1 = gmm.score_samples(target_samples)
                prob2 = gmm.score_samples(satellite_samples)
                collision_prob = np.mean(np.exp(prob1) * np.exp(prob2))

                distance, relative_speed = calculate_relative_metrics(target_pos, target_vel, pos, vel)
                lat, lon = eci_to_lat_lon(pos)

                collision_data = {
                    "collision_probability": float(collision_prob),
                    "distance (km)": float(distance),
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "norad_id": norad_id,
                    "relative_speed (km/s)": float(relative_speed),
                }

                if highest_collision is None or collision_prob > highest_collision["collision_probability"]:
                    highest_collision = collision_data

        if not highest_collision:
            return jsonify({"status": "no_collisions_predicted", "target_norad_id": target_norad_id})

        return jsonify({
            "status": "success",
            "target_norad_id": target_norad_id,
            "timestamp": current_time.isoformat(),
            "collision_data": highest_collision
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
