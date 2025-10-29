from flask import Blueprint, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import datetime

mechanic_bp = Blueprint("mechanic_bp", __name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# -------------------------
# Registration Endpoint
# -------------------------
@mechanic_bp.route("/register_mechanic", methods=["POST"])
def register_mechanic():
    data = request.get_json()
    full_name = data.get("full_name")
    contact_number = data.get("contact_number")
    email = data.get("email")
    username = data.get("username")
    raw_password = data.get("password")
    password = generate_password_hash(raw_password) if raw_password else None

    # Convert DOB to YYYY-MM-DD
    dob = data.get("dob")
    if dob:
        try:
            dob = datetime.strptime(dob[:10], "%Y-%m-%d").date()
        except:
            dob = None

    if not all([full_name, contact_number, email, username, password]):
        return jsonify({"error": "Required fields missing"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mechanics (
                full_name, gender, dob, contact_number, alt_contact_number, email, address,
                experience, qualification, specialization, known_brands,
                workshop_name, workshop_address, workshop_contact, opening_hours, weekly_off,
                available_days, available_time,
                account_holder, bank_name, account_number, ifsc, upi,
                username, password
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            full_name, data.get("gender"), dob, contact_number, data.get("alt_contact_number"),
            email, data.get("address"), data.get("experience"), data.get("qualification"),
            ",".join(data.get("specialization", [])) if data.get("specialization") else "",
            data.get("known_brands"), data.get("workshop_name"), data.get("workshop_address"),
            data.get("workshop_contact"), data.get("opening_hours"), data.get("weekly_off"),
            data.get("available_days"), data.get("available_time"), data.get("account_holder"),
            data.get("bank_name"), data.get("account_number"), data.get("ifsc"), data.get("upi"),
            username, password
        ))
        conn.commit()
        return jsonify({"message": "Mechanic registered successfully!"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email or username already exists!"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -------------------------
# Fetch Mechanic Profile
# -------------------------
@mechanic_bp.route("/get_mechanic/<int:id>", methods=["GET"])
def get_mechanic(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mechanics WHERE id=%s", (id,))
        mechanic = cursor.fetchone()
        return jsonify({"mechanic": mechanic})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -------------------------
# Update Mechanic Profile
# -------------------------
@mechanic_bp.route("/update_mechanic/<int:id>", methods=["PUT"])
def update_mechanic(id):
    data = request.get_json()

    # Convert DOB to YYYY-MM-DD
    dob = data.get("dob")
    if dob:
        try:
            dob = datetime.strptime(dob[:10], "%Y-%m-%d").date()
        except:
            dob = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            UPDATE mechanics SET 
                full_name=%s, gender=%s, dob=%s, contact_number=%s,
                alt_contact_number=%s, email=%s, address=%s, experience=%s,
                qualification=%s, specialization=%s, known_brands=%s,
                workshop_name=%s, workshop_address=%s, workshop_contact=%s,
                opening_hours=%s, weekly_off=%s, available_days=%s, available_time=%s,
                account_holder=%s, bank_name=%s, account_number=%s, ifsc=%s,
                upi=%s, username=%s
            WHERE id=%s
        """, (
            data.get("full_name"), data.get("gender"), dob,
            data.get("contact_number"), data.get("alt_contact_number"), data.get("email"),
            data.get("address"), data.get("experience"), data.get("qualification"),
            data.get("specialization"), data.get("known_brands"), data.get("workshop_name"),
            data.get("workshop_address"), data.get("workshop_contact"), data.get("opening_hours"),
            data.get("weekly_off"), data.get("available_days"), data.get("available_time"),
            data.get("account_holder"), data.get("bank_name"), data.get("account_number"),
            data.get("ifsc"), data.get("upi"), data.get("username"),
            id
        ))
        conn.commit()
        cursor.execute("SELECT * FROM mechanics WHERE id=%s", (id,))
        updated = cursor.fetchone()
        return jsonify({"mechanic": updated})
    except Exception as e:
        print("Update error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
