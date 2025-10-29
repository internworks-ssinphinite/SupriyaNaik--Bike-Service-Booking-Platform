from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import timedelta

bookings_bp = Blueprint("bookings_bp", __name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db",
}

# ---------------- Create Booking ----------------
@bookings_bp.route("/create", methods=["POST"])
def create_booking():
    try:
        data = request.get_json()
        required_fields = ["customer_id", "mechanic_id", "package", "date", "start_time", "end_time", "place"]

        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"success": False, "error": "Missing booking fields"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 🔹 Step 1: Check if slot already booked for same mechanic and overlapping time
        check_query = """
            SELECT * FROM bookings
            WHERE mechanic_id = %s
              AND date = %s
              AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (start_time >= %s AND end_time <= %s)
                  )
              AND status IN ('pending', 'completed')
        """
        cursor.execute(check_query, (
            data["mechanic_id"],
            data["date"],
            data["start_time"], data["start_time"],
            data["end_time"], data["end_time"],
            data["start_time"], data["end_time"],
        ))

        existing = cursor.fetchone()
        if existing:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "error": "This slot is already booked for the selected mechanic. Please choose another time."
            }), 400

        # 🔹 Step 2: Insert new booking
        insert_query = """
            INSERT INTO bookings (customer_id, mechanic_id, package, date, start_time, end_time, place, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
        """
        values = (
            data["customer_id"],
            data["mechanic_id"],
            data["package"],
            data["date"],
            data["start_time"],
            data["end_time"],
            data["place"],
        )

        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        print("Error in /bookings/create:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- Get Bookings for Mechanic ----------------
@bookings_bp.route("/get", methods=["GET"])
def get_bookings():
    try:
        mechanic_id = request.args.get("mechanic_id")
        if not mechanic_id:
            return jsonify({"success": False, "error": "Mechanic ID required"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM bookings
            WHERE mechanic_id=%s
            ORDER BY date DESC, start_time ASC
        """, (mechanic_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # 🔹 Format date/time properly
        for r in rows:
            if r.get("date") and not isinstance(r["date"], str):
                r["date"] = r["date"].strftime("%Y-%m-%d")
            for time_field in ["start_time", "end_time"]:
                if r.get(time_field) and not isinstance(r[time_field], str):
                    if isinstance(r[time_field], timedelta):
                        total_seconds = r[time_field].total_seconds()
                        h, rem = divmod(total_seconds, 3600)
                        m, s = divmod(rem, 60)
                        r[time_field] = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

        pending = [r for r in rows if r["status"] == "pending"]
        completed = [r for r in rows if r["status"] == "completed"]
        cancelled = [r for r in rows if r["status"] == "cancelled"]

        return jsonify({"success": True, "pending": pending, "completed": completed, "cancelled": cancelled})

    except Exception as e:
        print("Error in /bookings/get:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- Get Bookings for Customer ----------------
@bookings_bp.route("/customer/get", methods=["GET"])
def get_customer_bookings():
    try:
        customer_id = request.args.get("customer_id")
        if not customer_id:
            return jsonify({"success": False, "error": "Customer ID required"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM bookings
            WHERE customer_id=%s
            ORDER BY date DESC, start_time ASC
        """, (customer_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # 🔹 Format date/time properly
        for r in rows:
            if r.get("date") and not isinstance(r["date"], str):
                r["date"] = r["date"].strftime("%Y-%m-%d")
            for time_field in ["start_time", "end_time"]:
                if r.get(time_field) and not isinstance(r[time_field], str):
                    if isinstance(r[time_field], timedelta):
                        total_seconds = r[time_field].total_seconds()
                        h, rem = divmod(total_seconds, 3600)
                        m, s = divmod(rem, 60)
                        r[time_field] = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

        pending = [r for r in rows if r["status"] == "pending"]
        completed = [r for r in rows if r["status"] == "completed"]
        cancelled = [r for r in rows if r["status"] == "cancelled"]

        return jsonify({"success": True, "pending": pending, "completed": completed, "cancelled": cancelled})

    except Exception as e:
        print("Error in /bookings/customer/get:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- Accept Booking ----------------
@bookings_bp.route("/accept", methods=["POST"])
def accept_booking():
    try:
        data = request.get_json()
        booking_id = data.get("booking_id")
        if not booking_id:
            return jsonify({"success": False, "error": "Booking ID required"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status='completed' WHERE id=%s", (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        print("Error in /bookings/accept:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- Cancel Booking for Customer ----------------
@bookings_bp.route("/customer/cancel", methods=["POST"])
def cancel_customer_booking():
    try:
        data = request.get_json()
        booking_id = data.get("booking_id")
        if not booking_id:
            return jsonify({"success": False, "error": "Booking ID required"}), 400

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 🔹 Mark booking as cancelled (don’t delete)
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Booking cancelled successfully."})
    except Exception as e:
        print("Error in /bookings/customer/cancel:", e)
        return jsonify({"success": False, "error": str(e)}), 500
# ---------------- Mark Booking as Completed ----------------
@bookings_bp.route("/complete/<int:booking_id>", methods=["PUT"])
def complete_booking(booking_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE bookings SET status='completed' WHERE id=%s", 
            (booking_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Booking marked as completed."})
    except Exception as e:
        print("Error in /bookings/complete:", e)
        return jsonify({"success": False, "error": str(e)}), 500
