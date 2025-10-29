import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "NewPassword123!",
    "database": "bike_service_db"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_all_mechanics():
    """Fetch all mechanic IDs"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM mechanics")
    mechanics = cursor.fetchall()
    cursor.close()
    conn.close()
    return mechanics

def fetch_mechanic_availability(mechanic_id):
    """Fetch all availability slots for a given mechanic"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, day, start_time, end_time, date, place FROM mechanic_availability WHERE mechanic_id = %s",
        (mechanic_id,)
    )
    availability = cursor.fetchall()
    cursor.close()
    conn.close()
    return availability
