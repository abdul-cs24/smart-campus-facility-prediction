
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

import joblib
import pandas as pd

from fastapi.staticfiles import StaticFiles

from database import (
    create_table,
    get_previous_complaints,
    get_recurring_issues,
    save_complaint,
    get_all_complaints,
    get_dashboard_summary,
    get_high_risk_locations,
    update_complaint_status
)


app = FastAPI(
    title="Smart Campus Facility System"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database table when server starts
@app.on_event("startup")
def startup():
    create_table()


# Load trained ML model
model = joblib.load(
    "smart_campus_severity_model.pkl"
)


# Complaint input validation
class Complaint(BaseModel):

    user_type: str
    user_id: str = Field(min_length=1)

    block_no: int = Field(ge=1, le=50)
    floor: int = Field(ge=1, le=7)
    room_no: int = Field(ge=101, le=709)

    facility_type: str = Field(min_length=1)
    issue_type: str = Field(min_length=1)

    complaint_date: str
    complaint_time: str

    photo_available: str = "No"


# Estimate footfall based on facility type
def estimate_footfall(facility_type):

    footfall_data = {
        "Washroom": 400,
        "Water Cooler": 350,
        "Garbage": 300,
        "Lighting": 250,
        "Lift": 500,
        "AC": 200,
        "WiFi": 450,
        "Furniture": 150,
        "Electrical": 250,
        "Projector": 100,
        "Classroom": 350
    }

    return footfall_data.get(
        facility_type,
        200
    )


# Submit complaint
@app.post("/submit-complaint")
def submit_complaint(complaint: Complaint):

    # 1. Validate User Type
    if complaint.user_type not in ["Student", "Faculty"]:
        raise HTTPException(
            status_code=400,
            detail="User Type must be Student or Faculty"
        )

    # 2. Validate User ID
    if not complaint.user_id.strip():
        raise HTTPException(
            status_code=400,
            detail="User ID cannot be empty"
        )

    # 3. Validate Room Number according to Floor
    minimum_room = complaint.floor * 100 + 1
    maximum_room = complaint.floor * 100 + 9

    if not minimum_room <= complaint.room_no <= maximum_room:
        raise HTTPException(
            status_code=400,
            detail=f"For Floor {complaint.floor}, room number must be between {minimum_room} and {maximum_room}"
        )

    # 4. Validate Complaint Date
    try:
        complaint_date = datetime.strptime(
            complaint.complaint_date,
            "%Y-%m-%d"
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date. Use YYYY-MM-DD format"
        )

    # 5. Validate Complaint Time
    try:
        datetime.strptime(
            complaint.complaint_time,
            "%H:%M"
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid time. Use 24-hour HH:MM format"
        )

    # 6. Validate Photo Availability
    if complaint.photo_available not in ["Yes", "No"]:
        raise HTTPException(
            status_code=400,
            detail="Photo Available must be Yes or No"
        )

    # 7. Automatically find previous complaints
    previous_complaints = get_previous_complaints(
        complaint.block_no,
        complaint.floor,
        complaint.room_no,
        complaint.facility_type
    )

    # 8. Automatically estimate footfall
    footfall = estimate_footfall(
        complaint.facility_type
    )

    # 9. Extract complaint hour
    complaint_hour = int(
        complaint.complaint_time.split(":")[0]
    )

    # 10. Find day of week
    day_of_week = complaint_date.strftime("%A")

    # 11. Prepare ML input
    input_data = pd.DataFrame([{

        "User_Type": complaint.user_type,
        "Block_No": complaint.block_no,
        "Floor": complaint.floor,
        "Room_No": complaint.room_no,
        "Facility_Type": complaint.facility_type,
        "Issue_Type": complaint.issue_type,
        "Day_of_Week": day_of_week,
        "Complaint_Hour": complaint_hour,
        "Footfall": footfall,
        "Previous_Complaints": previous_complaints,
        "Photo_Available": complaint.photo_available

    }])

    # 12. Predict severity
    prediction = model.predict(
        input_data
    )[0]

    # 13. Prepare database record
    complaint_data = {

        "user_type": complaint.user_type,
        "user_id": complaint.user_id,

        "block_no": complaint.block_no,
        "floor": complaint.floor,
        "room_no": complaint.room_no,

        "facility_type": complaint.facility_type,
        "issue_type": complaint.issue_type,

        "complaint_date": complaint.complaint_date,
        "complaint_time": complaint.complaint_time,

        "footfall": footfall,
        "previous_complaints": previous_complaints,

        "photo_available": complaint.photo_available,
        "predicted_severity": prediction

    }

    # 14. Save complaint in database
    complaint_id = save_complaint(
        complaint_data
    )

    # 15. Return result
    return {

        "message": "Complaint submitted successfully",
        "complaint_id": complaint_id,
        "predicted_severity": prediction,
        "previous_complaints": previous_complaints,
        "status": "Pending"

    }


# Get all complaints
@app.get("/complaints")
def complaints():
    return get_all_complaints()


# Dashboard summary
@app.get("/dashboard-summary")
def dashboard_summary():
    return get_dashboard_summary()


# High-risk locations
@app.get("/high-risk-locations")
def high_risk_locations():
    return get_high_risk_locations()


# Recurring issues
@app.get("/recurring-issues")
def recurring_issues():
    return get_recurring_issues()


# Frontend
app.mount(
    "/ui",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)

class StatusUpdate(BaseModel):
    status: str


@app.patch("/complaints/{complaint_id}/status")
def change_complaint_status(
    complaint_id: int,
    update: StatusUpdate
):

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    updated = update_complaint_status(
        complaint_id,
        update.status
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return {
        "message": "Complaint status updated successfully",
        "complaint_id": complaint_id,
        "status": update.status
    }