from flask import Blueprint, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash

customer_bp = Blueprint("customer_bp", __name__)

# MySQL database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",                 # Update if needed
    "password": "NewPassword123!",  # Update with your password
    "database": "bike_service_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@customer_bp.route("/register", methods=["POST"])
def register_customer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract fields matching your React form and MySQL table
    full_name = data.get("fullName")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    address1 = data.get("address1")
    address2 = data.get("address2")
    city = data.get("city")
    pincode = data.get("pincode")
    bike_brand = data.get("bikeBrand")
    model_name = data.get("modelName")
    registration_number = data.get("registrationNumber")
    purchase_year = data.get("purchaseYear")
    service_type = data.get("serviceType")
    notes = data.get("notes")

    if not all([full_name, email, phone, password, address1, city, pincode, bike_brand, model_name, registration_number]):
        return jsonify({"error": "Missing required fields"}), 400

    # Hash password before storing
    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO customers (
            full_name, email, phone, password, address1, address2, city, pincode,
            bike_brand, model_name, registration_number, purchase_year, service_type, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            full_name, email, phone, hashed_password, address1, address2, city, pincode,
            bike_brand, model_name, registration_number, purchase_year, service_type, notes
        )

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Customer registered successfully!"}), 201

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return jsonify({"error": "Database error", "details": str(err)}), 500
