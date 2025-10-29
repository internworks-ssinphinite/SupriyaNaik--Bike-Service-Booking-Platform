from flask import Blueprint, jsonify
import mysql.connector
from routes.mecha_aval import DB_CONFIG  # reuse DB_CONFIG

mech_req_bp = Blueprint("mech_req_bp", __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Fetch all service requests for a mechanic
@mech_req_bp.route("/<int:mechanic_id>/requests", methods=["GET"])
def get_service_requests(mechanic_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.id, c.full_name AS customer_name, c.phone, b.package,
                   b.date, b.start_time, b.end_time, b.place, b.status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            WHERE b.mechanic_id = %s
            ORDER BY b.date, b.start_time
        """, (mechanic_id,))
        requests = cursor.fetchall()
        conn.close()
        return jsonify({"requests": requests}), 200
    except Exception as e:
        print("❌ Error fetching service requests:", e)
        return jsonify({"requests": [], "error": str(e)}), 500
