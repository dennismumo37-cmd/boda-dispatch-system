from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Boda Boda Station & Dispatch System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect("boda_system.db", check_same_thread=False)
cursor = conn.cursor()

# 1. Stations Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    landmark TEXT NOT NULL
)
""")

# 2. Riders Table (Includes bike_type, rating, and review_summary)
cursor.execute("""
CREATE TABLE IF NOT EXISTS riders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    national_id TEXT NOT NULL,
    number_plate TEXT NOT NULL,
    bike_type TEXT DEFAULT 'Petrol',
    rating REAL DEFAULT 4.8,
    reviews TEXT DEFAULT 'Safe and punctual rider',
    station_id INTEGER,
    is_available INTEGER DEFAULT 1,
    FOREIGN KEY(station_id) REFERENCES stations(id)
)
""")

# 3. Ride Requests Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ride_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    client_phone TEXT NOT NULL,
    destination TEXT NOT NULL,
    station_id INTEGER,
    rider_id INTEGER,
    status TEXT DEFAULT 'PENDING',
    FOREIGN KEY(station_id) REFERENCES stations(id),
    FOREIGN KEY(rider_id) REFERENCES riders(id)
)
""")
conn.commit()

# --- Data Models ---
class Station(BaseModel):
    name: str
    landmark: str

class Rider(BaseModel):
    full_name: str
    phone: str
    national_id: str
    number_plate: str
    bike_type: str
    rating: float
    reviews: str
    station_id: int

class RideRequestCreate(BaseModel):
    client_name: str
    client_phone: str
    destination: str
    station_id: int
    rider_id: int

class RequestDecision(BaseModel):
    status: str  # "APPROVED" or "DENIED"

# --- Station Endpoints ---
@app.post("/stations")
def add_station(station: Station):
    cursor.execute("INSERT INTO stations (name, landmark) VALUES (?, ?)", (station.name, station.landmark))
    conn.commit()
    return {"status": "Station added"}

@app.get("/stations")
def get_stations():
    cursor.execute("SELECT id, name, landmark FROM stations")
    return [{"id": r[0], "name": r[1], "landmark": r[2]} for r in cursor.fetchall()]

# --- Rider Endpoints ---
@app.post("/riders")
def onboard_rider(rider: Rider):
    cursor.execute(
        """INSERT INTO riders (full_name, phone, national_id, number_plate, bike_type, rating, reviews, station_id) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (rider.full_name, rider.phone, rider.national_id, rider.number_plate, rider.bike_type, rider.rating, rider.reviews, rider.station_id)
    )
    conn.commit()
    return {"status": "Rider onboarded"}

@app.get("/riders")
def get_all_riders():
    cursor.execute("SELECT id, full_name, number_plate, station_id FROM riders")
    return [{"id": r[0], "name": r[1], "plate": r[2], "station_id": r[3]} for r in cursor.fetchall()]

@app.get("/stations/{station_id}/riders")
def get_riders_at_station(station_id: int):
    cursor.execute(
        """SELECT id, full_name, phone, number_plate, bike_type, rating, reviews 
           FROM riders WHERE station_id = ? AND is_available = 1""",
        (station_id,)
    )
    return [
        {
            "id": r[0], "name": r[1], "phone": r[2], "plate": r[3],
            "bike_type": r[4], "rating": r[5], "reviews": r[6]
        }
        for r in cursor.fetchall()
    ]

# --- Ride Request Endpoints ---
@app.post("/requests")
def create_ride_request(req: RideRequestCreate):
    cursor.execute(
        """INSERT INTO ride_requests (client_name, client_phone, destination, station_id, rider_id, status)
           VALUES (?, ?, ?, ?, ?, 'PENDING')""",
        (req.client_name, req.client_phone, req.destination, req.station_id, req.rider_id)
    )
    conn.commit()
    request_id = cursor.lastrowid
    return {"request_id": request_id, "status": "PENDING"}

@app.get("/requests/{request_id}")
def check_request_status(request_id: int):
    cursor.execute("SELECT id, status, rider_id FROM ride_requests WHERE id = ?", (request_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"id": row[0], "status": row[1], "rider_id": row[2]}

@app.get("/riders/{rider_id}/requests")
def get_rider_requests(rider_id: int):
    cursor.execute(
        """SELECT id, client_name, client_phone, destination, status 
           FROM ride_requests WHERE rider_id = ? ORDER BY id DESC""",
        (rider_id,)
    )
    return [
        {"id": r[0], "client_name": r[1], "client_phone": r[2], "destination": r[3], "status": r[4]}
        for r in cursor.fetchall()
    ]

@app.put("/requests/{request_id}/decision")
def decide_request(request_id: int, decision: RequestDecision):
    cursor.execute("UPDATE ride_requests SET status = ? WHERE id = ?", (decision.status, request_id))
    conn.commit()
    return {"request_id": request_id, "new_status": decision.status}