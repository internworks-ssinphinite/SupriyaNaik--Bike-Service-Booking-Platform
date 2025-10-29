import traceback
from flask import Blueprint, request, jsonify
import mysql.connector
from werkzeug.security import check_password_hash

# 1️⃣ Create the blueprint first
mechanic_login_bp = Blueprint("mechanic_login_bp", __name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# 2️⃣ Then define the route
@mechanic_login_bp.route("/login_mechanic", methods=["POST"])
def login_mechanic():
    data = request.get_json()
    username_or_email = data.get("username")
    password = data.get("password")

    print("Received login data:", username_or_email, password)

    if not username_or_email or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM mechanics WHERE username=%s OR email=%s LIMIT 1"
        cursor.execute(query, (username_or_email, username_or_email))
        user = cursor.fetchone()

        print("Fetched user:", user)

        if not user:
            return jsonify({"error": "User not found"}), 404

        print("Stored hash:", user["password"])
        check = check_password_hash(user["password"], password)
        print("Password check result:", check)

        if check:
            user.pop("password", None)
            return jsonify({"message": "Login successful", "mechanic": user}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
