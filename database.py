import sqlite3

DATABASE_NAME = "smart_campus.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    return connection


def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_type TEXT,
            user_id TEXT,

            block_no INTEGER,
            floor INTEGER,
            room_no INTEGER,

            facility_type TEXT,
            issue_type TEXT,

            complaint_date TEXT,
            complaint_time TEXT,

            footfall INTEGER,
            previous_complaints INTEGER,

            photo_available TEXT,

            predicted_severity TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# Count previous complaints from the same location
def get_previous_complaints(
    block_no,
    floor,
    room_no,
    facility_type
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE block_no = ?
        AND floor = ?
        AND room_no = ?
        AND facility_type = ?
    """, (
        block_no,
        floor,
        room_no,
        facility_type
    ))

    count = cursor.fetchone()[0]

    connection.close()

    return count


# Save a new complaint
def save_complaint(data):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO complaints (

            user_type,
            user_id,

            block_no,
            floor,
            room_no,

            facility_type,
            issue_type,

            complaint_date,
            complaint_time,

            footfall,
            previous_complaints,

            photo_available,

            predicted_severity

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        data["user_type"],
        data["user_id"],

        data["block_no"],
        data["floor"],
        data["room_no"],

        data["facility_type"],
        data["issue_type"],

        data["complaint_date"],
        data["complaint_time"],

        data["footfall"],
        data["previous_complaints"],

        data["photo_available"],

        data["predicted_severity"]
    ))

    connection.commit()

    complaint_id = cursor.lastrowid

    connection.close()

    return complaint_id

# Get all complaints
def get_all_complaints():

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM complaints
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# Get dashboard summary
def get_dashboard_summary():

    connection = get_connection()

    cursor = connection.cursor()

    # Total complaints
    total = cursor.execute("""
        SELECT COUNT(*) FROM complaints
    """).fetchone()[0]

    # Pending complaints
    pending = cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Pending'
    """).fetchone()[0]

    # High and Critical complaints
    high_priority = cursor.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE predicted_severity IN ('High', 'Critical')
    """).fetchone()[0]

    connection.close()

    return {
        "total_complaints": total,
        "pending_complaints": pending,
        "high_priority": high_priority
    }


# Find recurring / high-risk locations
def get_high_risk_locations():

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            block_no,
            floor,
            room_no,
            facility_type,

            COUNT(*) AS complaint_count,

            AVG(
                CASE predicted_severity
                    WHEN 'Low' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'High' THEN 3
                    WHEN 'Critical' THEN 4
                END
            ) AS average_severity

        FROM complaints

        GROUP BY
            block_no,
            floor,
            room_no,
            facility_type

        ORDER BY
            complaint_count DESC,
            average_severity DESC

        LIMIT 10
    """)

    rows = cursor.fetchall()

    connection.close()

    locations = []

    for row in rows:

        location = dict(row)

        # Normalize complaint frequency
        frequency_score = min(
            location["complaint_count"] / 5,
            1
        )

        # Normalize severity (maximum severity value is 4)
        severity_score = (
            location["average_severity"] / 4
        )

        # Final priority score
        priority_score = (
            0.5 * frequency_score
            +
            0.5 * severity_score
        )

        # Decide alert level
        if priority_score >= 0.70:
            alert_level = "High Alert"

        elif priority_score >= 0.40:
            alert_level = "Medium Alert"

        else:
            alert_level = "Low Alert"

        location["priority_score"] = round(
            priority_score,
            2
        )

        location["alert_level"] = alert_level

        locations.append(location)

    # Sort locations by priority score
    locations.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    return locations


def get_recurring_issues():

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            block_no,
            floor,
            room_no,
            facility_type,
            issue_type,
            COUNT(*) AS issue_count

        FROM complaints

        GROUP BY
            block_no,
            floor,
            room_no,
            facility_type,
            issue_type

        HAVING COUNT(*) >= 2

        ORDER BY issue_count DESC

        LIMIT 10
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# Update complaint status
def update_complaint_status(complaint_id, new_status):

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if new_status not in allowed_statuses:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """, (new_status, complaint_id))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated