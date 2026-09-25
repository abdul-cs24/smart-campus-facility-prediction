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

def generate_previous_complaints():
    return random.randint(0, 15)

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

def generate_date():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 9, 1)

    days = (end_date - start_date).days

    random_days = random.randint(0, days)

    return start_date + timedelta(days=random_days)



block = random.choice(BLOCKS)
floor = random.choice(FLOORS)
room = generate_room(floor)

# user_type = random.choice(USER_TYPES)
user_type = random.choices(
    USER_TYPES,
    weights=[90, 10],
    k=1
)[0]

facility = random.choice(FACILITIES)
issue = random.choice(ISSUES[facility])

print("User Type:", user_type)
print("Block:", block)
print("Floor:", floor)
print("Room:", room)
print("Facility:", facility)
print("Issue:", issue)