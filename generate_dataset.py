import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

BLOCKS = list(range(1, 51))

FLOORS = list(range(1, 8))

USER_TYPES = [
    "Student",
    "Faculty"
]

FACILITIES = [
    "Washroom",
    "Water Cooler",
    "Lighting",
    "Garbage",
    "Classroom",
    "Lift",
    "AC",
    "WiFi",
    "Furniture",
    "Electrical",
    "Projector"
]

ISSUES = {

    "Washroom": [
        "Cleanliness",
        "Water Leakage",
        "No Water",
        "Fixture Damage"
    ],

    "Water Cooler": [
        "Not Working",
        "No Water",
        "Water Leakage",
        "Water Quality"
    ],

    "Lighting": [
        "Light Not Working",
        "Flickering",
        "Electrical Fault"
    ],

    "Garbage": [
        "Bin Overflow",
        "Bad Odour",
        "Waste Not Collected"
    ],

    "Classroom": [
        "Fan Not Working",
        "Damaged Board",
        "General Maintenance"
    ],

    "Lift": [
        "Not Working",
        "Door Problem",
        "Stuck",
        "Unusual Noise"
    ],

    "AC": [
        "Not Cooling",
        "Not Working",
        "Water Leakage",
        "Unusual Noise"
    ],

    "WiFi": [
        "No Connection",
        "Slow Speed",
        "Authentication Problem",
        "Frequent Disconnection"
    ],

    "Furniture": [
        "Broken Chair",
        "Broken Desk",
        "Damaged Furniture"
    ],

    "Electrical": [
        "Power Failure",
        "Socket Problem",
        "Switch Problem",
        "Electrical Hazard"
    ],

    "Projector": [
        "No Display",
        "HDMI Problem",
        "Power Issue",
        "Blurry Display"
    ]
}

HIGH_RISK_LOCATIONS = [
    (12, 3, 305, "Washroom"),
    (34, 5, 507, "Projector"),
    (21, 2, 203, "Water Cooler"),
    (8, 4, 404, "WiFi"),
    (45, 1, 102, "Garbage"),
    (17, 6, 605, "AC"),
    (29, 3, 307, "Electrical"),
    (40, 2, 204, "Lift")
]

HIGH_RISK_ISSUES = {
    (12, 3, 305, "Washroom"): "Cleanliness",
    (34, 5, 507, "Projector"): "No Display",
    (21, 2, 203, "Water Cooler"): "No Water",
    (8, 4, 404, "WiFi"): "Frequent Disconnection",
    (45, 1, 102, "Garbage"): "Bin Overflow",
    (17, 6, 605, "AC"): "Not Cooling",
    (29, 3, 307, "Electrical"): "Power Failure",
    (40, 2, 204, "Lift"): "Not Working"
}



facility = "Projector"

issue = random.choice(ISSUES[facility])

# print(issue)


def generate_room(floor):
    room_last_number = random.randint(1, 9)
    room = floor * 100 + room_last_number
    return room


# print(generate_room(5))


def generate_user_id(user_type):

    if user_type == "Student":
        return random.randint(12400000, 12499999)

    elif user_type == "Faculty":
        return random.randint(3000, 9999)

def generate_footfall(facility):

    if facility in ["Washroom", "Water Cooler", "Garbage"]:
        return random.randint(200, 700)

    elif facility in ["Lift", "WiFi", "Lighting", "Electrical"]:
        return random.randint(150, 600)

    else:
        return random.randint(30, 150)

# def generate_previous_complaints():
#     return random.randint(0, 15)



def generate_severity(issue, footfall, previous_complaints):

    critical_issues = [
        "Electrical Hazard",
        "Stuck",
        "Power Failure"
    ]

    if issue in critical_issues:
        return random.choice(["High", "Critical"])

    elif footfall > 500 and previous_complaints >= 8:
        return "High"

    elif previous_complaints >= 5:
        return random.choice(["Medium", "High"])

    else:
        return random.choice(["Low", "Medium"])


def generate_resolution_time(severity):

    if severity == "Critical":
        return round(random.uniform(0.5, 2), 1)

    elif severity == "High":
        return round(random.uniform(1, 6), 1)

    elif severity == "Medium":
        return round(random.uniform(4, 12), 1)

    else:
        return round(random.uniform(8, 24), 1)


def generate_photo():
    return random.choice(["Yes", "Yes", "Yes", "No"])

def generate_datetime():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 9, 1)

    days = (end_date - start_date).days
    random_days = random.randint(0, days)

    complaint_date = start_date + timedelta(days=random_days)

    # Campus active hours: 8 AM to 8 PM
    hour = random.randint(8, 19)
    minute = random.randint(0, 59)

    complaint_datetime = complaint_date.replace(
        hour=hour,
        minute=minute
    )

    return complaint_datetime

def generate_location():

    # 30% chance of selecting a recurring high-risk location
    if random.random() < 0.30:

        block, floor, room, facility = random.choice(
            HIGH_RISK_LOCATIONS
        )

    else:

        block = random.choice(BLOCKS)
        floor = random.choice(FLOORS)
        room = generate_room(floor)
        facility = random.choice(FACILITIES)

    return block, floor, room, facility

def generate_issue(block, floor, room, facility):

    location_key = (
        block,
        floor,
        room,
        facility
    )

    # High-risk location
    if location_key in HIGH_RISK_ISSUES:

        # 70% chance recurring issue repeats
        if random.random() < 0.70:
            return HIGH_RISK_ISSUES[location_key]

    # Otherwise choose normal facility-specific issue
    return random.choice(ISSUES[facility])

# block = random.choice(BLOCKS)
# floor = random.choice(FLOORS)
# room = generate_room(floor)

# user_type = random.choice(USER_TYPES)
# user_type = random.choices(
#     USER_TYPES,
#     weights=[90, 10],
#     k=1
# )[0]

# facility = random.choice(FACILITIES)

block, floor, room, facility = generate_location()



issue = random.choice(ISSUES[facility])

# print("User Type:", user_type)
# print("Block:", block)
# print("Floor:", floor)
# print("Room:", room)
# print("Facility:", facility)
# print("Issue:", issue)


complaint_history = {}



data = []

for i in range(10000):

    # 1. User
    user_type = random.choices(
        USER_TYPES,
        weights=[90, 10],
        k=1
    )[0]

    user_id = generate_user_id(user_type)

    # 2. Location
    # block = random.choice(BLOCKS)
    # floor = random.choice(FLOORS)
    # room = generate_room(floor)

    # 3. Facility and Issue
    # facility = random.choice(FACILITIES)

    # 2. Location + Facility
    block, floor, room, facility = generate_location()

# 3. Issue

    # issue = random.choice(ISSUES[facility])

    issue = generate_issue(
    block,
    floor,
    room,
    facility
)

    location_key = (
    block,
    floor,
    room,
    facility
)


    # 4. Campus usage
    footfall = generate_footfall(facility)

    # 5. Complaint history
    # previous_complaints = generate_previous_complaints()

    previous_complaints = complaint_history.get(
    location_key,
    0
)

    # 6. Severity
    severity = generate_severity(
        issue,
        footfall,
        previous_complaints
    )

    # 7. Resolution time
    resolution_time = generate_resolution_time(severity)

    # 8. Photo
    photo = generate_photo()

    # 9. Date
    complaint_datetime = generate_datetime()

    # 10. Store complaint
    data.append({
        "Complaint_ID": f"CMP{i+1:05d}",
        "User_Type": user_type,
        "User_ID": user_id,
        "Block_No": block,
        "Floor": floor,
        "Room_No": room,
        "Facility_Type": facility,
        "Issue_Type": issue,
        "Complaint_Date": complaint_datetime.date(),
        "Day_of_Week": complaint_datetime.strftime("%A"),
        "Complaint_Time": complaint_datetime.strftime("%H:%M"),
        "Footfall": footfall,
        "Previous_Complaints": previous_complaints,
        "Severity": severity,
        "Resolution_Time_Hours": resolution_time,
        "Photo_Available": photo
    })

    complaint_history[location_key] = previous_complaints + 1

df = pd.DataFrame(data)



# Create complete datetime
df["Complaint_DateTime"] = pd.to_datetime(
    df["Complaint_Date"].astype(str)
    + " "
    + df["Complaint_Time"]
)

# Sort oldest to newest
df = df.sort_values(
    "Complaint_DateTime"
).reset_index(drop=True)

# Recalculate previous complaints chronologically
df["Previous_Complaints"] = (
    df.groupby(
        ["Block_No", "Floor", "Room_No", "Facility_Type"]
    )
    .cumcount()
)

# Recalculate severity
df["Severity"] = df.apply(
    lambda row: generate_severity(
        row["Issue_Type"],
        row["Footfall"],
        row["Previous_Complaints"]
    ),
    axis=1
)

# Recalculate resolution time
df["Resolution_Time_Hours"] = df["Severity"].apply(
    generate_resolution_time
)

# Recreate complaint IDs
df["Complaint_ID"] = [
    f"CMP{i+1:05d}"
    for i in range(len(df))
]

# print(df.to_string(index=False))

# print("\n--- Recurring Issues at High-Risk Locations ---")

# for location in HIGH_RISK_LOCATIONS:

#     block, floor, room, facility = location

#     result = df[
#         (df["Block_No"] == block) &
#         (df["Floor"] == floor) &
#         (df["Room_No"] == room) &
#         (df["Facility_Type"] == facility)
#     ]

#     if len(result) > 0:

#         print(
#             f"\nBlock {block}, Floor {floor}, "
#             f"Room {room}, {facility}"
#         )

#         print(result["Issue_Type"].value_counts())

#convert data into csv file

df.to_csv(
    "smart_campus_facility_dataset.csv",
    index=False
)

print("\nDataset created successfully!")
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

print("\nSeverity Distribution:")
print(df["Severity"].value_counts())

print("\nFacility Distribution:")
print(df["Facility_Type"].value_counts())
