from flask import Blueprint, request, jsonify, make_response
import mysql.connector
from datetime import datetime, timedelta
from dateutil import parser  # pip install python-dateutil

# ---------------- Blueprint ----------------
mecha_aval_bp = Blueprint("mecha_aval_bp", __name__)

# ---------------- DB Config ----------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def format_time(time_str):
    """Ensure time string is in HH:MM:SS format"""
    if not time_str:
        return None
    if len(time_str.split(":")) == 2:
        return time_str + ":00"
    return time_str

# ---------------- Routes ----------------

# GET all mechanics
@mecha_aval_bp.route("/available-mechanics", methods=["GET"])
def fetch_all_mechanics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name AS name, specialization FROM mechanics ORDER BY full_name")
        mechanics = cursor.fetchall()
        conn.close()
        response = make_response(jsonify(mechanics), 200)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response
    except Exception as e:
        print("❌ Error fetching mechanics:", e)
        return jsonify([]), 500

# GET availability for a mechanic
@mecha_aval_bp.route("/<int:mechanic_id>/availability", methods=["GET"])
def fetch_mechanic_availability(mechanic_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, day, start_time, end_time, date, place
            FROM mechanic_availability
            WHERE mechanic_id = %s
            ORDER BY FIELD(day, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'), start_time
        """, (mechanic_id,))
        slots = cursor.fetchall()
        conn.close()

        # Convert time objects to HH:MM:SS string
        for slot in slots:
            for key in ["start_time", "end_time"]:
                t = slot.get(key)
                if t is not None:
                    if isinstance(t, timedelta):
                        total_seconds = t.total_seconds()
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        slot[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        slot[key] = t.strftime("%H:%M:%S")

        return jsonify({"availability": slots}), 200
    except Exception as e:
        print("❌ Error fetching availability:", e)
        return jsonify({"availability": []}), 500

# POST to add/update availability
@mecha_aval_bp.route("/<int:mechanic_id>/availability", methods=["POST"])
def save_mechanic_availability(mechanic_id):
    try:
        data = request.get_json()
        availability = data.get("availability", [])

        conn = get_db_connection()
        cursor = conn.cursor()

        # Remove existing slots for this mechanic
        cursor.execute("DELETE FROM mechanic_availability WHERE mechanic_id = %s", (mechanic_id,))

        for slot in availability:
            start_time = format_time(slot.get("start_time"))
            end_time = format_time(slot.get("end_time"))
            date_str = slot.get("date")
            place = slot.get("place")
            day = slot.get("day")

            # ---------------- Convert date ----------------
            date = None
            if date_str:
                try:
                    dt = parser.parse(date_str)        # Parse incoming string
                    date = dt.strftime("%Y-%m-%d")    # Convert to MySQL DATE
                    if not day:
                        day = dt.strftime("%A")
                except Exception as e:
                    print("⚠️ Skipping invalid date:", date_str, e)
                    continue  # skip this slot if date invalid

            # Skip slot if essential info missing
            if not (start_time and end_time and date):
                print("⚠️ Skipping slot due to missing date/time:", slot)
                continue

            cursor.execute("""
                INSERT INTO mechanic_availability (mechanic_id, day, start_time, end_time, date, place)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (mechanic_id, day, start_time, end_time, date, place))
            print(f"✅ Inserted slot: mechanic_id={mechanic_id}, date={date}, start={start_time}, end={end_time}, place={place}")

        conn.commit()
        conn.close()
        return jsonify({"message": "Availability saved successfully!"}), 200

    except Exception as e:
        print("❌ Error saving availability:", e)
        return jsonify({"error": str(e)}), 500

# ------------------- DEBUG Route -------------------
@mecha_aval_bp.route("/debug-mechanics", methods=["GET"])
def debug_mechanics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mechanics")
        mechanics = cursor.fetchall()
        conn.close()

        print("DEBUG: Mechanics fetched from DB:", mechanics)
        return jsonify({"mechanics": mechanics, "count": len(mechanics)}), 200
    except Exception as e:
        print("❌ Error fetching mechanics for debug:", e)
        return jsonify({"mechanics": [], "error": str(e)}), 500
