from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from routes.customer_login import customer_bp
from routes.mechanic_register import mechanic_bp
from routes.mechanic_login import mechanic_login_bp
from routes.mecha_aval import mecha_aval_bp
from routes.bookings import bookings_bp
from routes.mechanic_bookings import mechanic_bookings_bp  # ✅ new
import os

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "../frontend/build"),
    static_url_path="/"
)

CORS(app)

# ---------------- Blueprints ----------------
app.register_blueprint(customer_bp, url_prefix="/customer")
app.register_blueprint(mechanic_bp, url_prefix="/mechanic")          # Registration
app.register_blueprint(mechanic_login_bp, url_prefix="/mechanic")    # Login
app.register_blueprint(mecha_aval_bp, url_prefix="/mechanic")        # Availability
app.register_blueprint(bookings_bp, url_prefix="/bookings")          # Bookings
app.register_blueprint(mechanic_bookings_bp, url_prefix="/mechanic/bookings")  # Mechanic bookings

# ---------------- Serve React ----------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

# ---------------- Run Flask ----------------
if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=False)
