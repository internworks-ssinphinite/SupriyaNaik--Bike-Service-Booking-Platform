from flask import Blueprint, request, jsonify
import mysql.connector

mechanic_bookings_bp = Blueprint("mechanic_bookings_bp", __name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db",
}

# ---------------- Get Bookings for a Mechanic ----------------
@mechanic_bookings_bp.route("/get", methods=["GET"])
def get_bookings():
    mechanic_id = request.args.get("mechanic_id")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM mechanic_bookings WHERE mechanic_id = %s"
        cursor.execute(query, (mechanic_id,))
        bookings = cursor.fetchall()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ---------------- Mark Booking as Completed ----------------
@mechanic_bookings_bp.route("/complete/<int:booking_id>", methods=["PUT"])
def complete_booking(booking_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        update_query = """
            UPDATE mechanic_bookings
            SET status = 'Completed'
            WHERE id = %s
        """
        cursor.execute(update_query, (booking_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Booking not found"}), 404

        return jsonify({"message": "Booking marked as completed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
