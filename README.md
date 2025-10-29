# 🏍️ Bike Service Booking Platform (BikeServe+)

## 📌 Overview
**BikeServe+** is an online bike service booking platform that simplifies how customers and mechanics manage service appointments.  
It was created to address issues with manual booking, delays, and lack of real-time updates.  

The platform allows customers to easily book services, choose packages, select available time slots, and track their service progress online.  
Mechanics can view assigned bookings, manage slot timings, update service status, and mark them as completed efficiently.  

The backend, developed using **Flask**, handles all API operations and connects to a **MySQL** database for secure and organized data storage.  
The **React.js** frontend provides a smooth, responsive, and user-friendly interface for both customers and mechanics.  

I designed a structured database to manage users, bookings, packages, and slot details effectively.  
During development, I resolved challenges such as booking updates, slot conflicts, and API routing errors through backend refinements.  
Overall, **BikeServe+** ensures a fast, transparent, and efficient system for managing bike service bookings with proper slot arrangements.

---

## 🚀 Features

### 🧑‍💻 Customer Features
- Register and log in securely  
- Browse service packages  
- Book bike service appointments online  
- Track service status and view booking history  

### 🔧 Mechanic Features
- Login to mechanic dashboard  
- View assigned bookings  
- Update and mark bookings as completed  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React.js |
| **Backend** | Python Flask |
| **Database** | MySQL |
| **Version Control** | Git & GitHub |

---

## ⚙️ Installation and Setup (Windows)

Follow these steps carefully to set up and run the **entire project** on your Windows system 👇  

```bash
# 1️⃣ Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# 2️⃣ Setup the Frontend, Backend, and Database (all in one flow)

# --- FRONTEND SETUP ---
cd frontend
npm install

# --- BACKEND SETUP ---
cd ../backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# --- DATABASE SETUP ---
# Open MySQL Command Prompt or Workbench and create the database
CREATE DATABASE bike_service_db;

# Update the following configuration in backend/app.py
# Replace root and password with your MySQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/bike_service_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database tables
python
>>> from app import db
>>> db.create_all()
>>> exit()

# --- RUN THE PROJECT ---
# Start Flask backend
python app.py

# Open new terminal for frontend
cd ../frontend
npm start
