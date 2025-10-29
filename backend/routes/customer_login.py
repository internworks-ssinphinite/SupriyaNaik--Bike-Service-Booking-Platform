from flask import Blueprint, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash

customer_bp = Blueprint("customer_bp", __name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ✅ Customer Login
@customer_bp.route("/login", methods=["POST"])
def login_customer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    mobile = data.get("mobile")

    if not name or not mobile:
        return jsonify({"error": "Missing name or mobile"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, full_name, email, phone, password, address1, address2, city, pincode,
                   bike_brand, model_name, registration_number, purchase_year, service_type, notes
            FROM customers 
            WHERE full_name=%s AND phone=%s
        """, (name, mobile))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()

        if customer:
            customer.pop("password", None)  # Remove password from response
            return jsonify({"message": "Login successful!", "customer": customer}), 200
        else:
            return jsonify({"error": "Invalid name or mobile"}), 401

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


# ✅ Customer Profile
@customer_bp.route("/profile/<int:customer_id>", methods=["GET"])
def get_customer_profile(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, full_name, email, phone, password, address1, address2, city, pincode,
                   bike_brand, model_name, registration_number, purchase_year, service_type, notes
            FROM customers 
            WHERE id=%s
        """, (customer_id,))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()

        if customer:
            customer.pop("password", None)  # Remove password from response
            return jsonify({"customer": customer}), 200
        else:
            return jsonify({"error": "Customer not found"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


# ✅ Update Customer Profile
@customer_bp.route("/update/<int:customer_id>", methods=["PUT"])
def update_customer_profile(customer_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE customers
            SET full_name=%s, phone=%s, address1=%s, address2=%s, city=%s, pincode=%s,
                bike_brand=%s, model_name=%s, registration_number=%s
            WHERE id=%s
        """, (
            data.get("full_name"),
            data.get("phone"),
            data.get("address1"),
            data.get("address2"),
            data.get("city"),
            data.get("pincode"),
            data.get("bike_brand"),
            data.get("model_name"),
            data.get("registration_number"),
            customer_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Profile updated successfully"}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
