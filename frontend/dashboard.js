
const API_URL = "http://127.0.0.1:8000";

let allComplaints = [];


// ========================================
// 1. Helper: Convert Time to AM/PM
// ========================================

function formatTime(time) {

    if (!time) return "N/A";

    const [hours, minutes] = time.split(":");

    let hour = parseInt(hours);

    const ampm = hour >= 12 ? "PM" : "AM";

    hour = hour % 12;
    hour = hour === 0 ? 12 : hour;

    return `${hour}:${minutes} ${ampm}`;
}


// ========================================
// 2. Helper: Fetch API Data
// ========================================

async function fetchData(url, options = {}) {

    const response = await fetch(url, options);

    if (!response.ok) {

        const error = await response.json().catch(() => ({}));

        throw new Error(
            error.detail || `API Error: ${response.status}`
        );
    }

    return await response.json();
}


// ========================================
// 3. Load Dashboard Summary
// ========================================

async function loadSummary() {

    const data = await fetchData(
        `${API_URL}/dashboard-summary`
    );

    document.getElementById(
        "totalComplaints"
    ).textContent = data.total_complaints;

    document.getElementById(
        "pendingComplaints"
    ).textContent = data.pending_complaints;

    document.getElementById(
        "highPriority"
    ).textContent = data.high_priority;
}


// ========================================
// 4. Load High-Risk Locations
// ========================================

async function loadHighRiskLocations() {

    const locations = await fetchData(
        `${API_URL}/high-risk-locations`
    );

    const container = document.getElementById(
        "riskLocations"
    );

    container.innerHTML = "";

    if (locations.length === 0) {

        container.innerHTML =
            "<p>No complaints available yet.</p>";

        return;
    }

    locations.forEach(location => {

        const alertClass = location.alert_level
            .toLowerCase()
            .replace(" ", "-");

        container.innerHTML += `

            <div class="risk-location">

                <div>

                    <strong>
                        Block ${location.block_no}
                        → Floor ${location.floor}
                        → Room ${location.room_no}
                    </strong>

                    <p>
                        ${location.facility_type}
                    </p>

                </div>

                <div class="risk-details">

                    <span class="alert-badge ${alertClass}">
                        ${location.alert_level}
                    </span>

                    <p>
                        Priority Score:
                        ${location.priority_score}
                    </p>

                    <p>
                        ${location.complaint_count}
                        complaints
                    </p>

                </div>

            </div>

        `;
    });
}


// ========================================
// 5. Load All Complaints from Database
// ========================================

async function loadComplaints() {

    const complaints = await fetchData(
        `${API_URL}/complaints`
    );

    allComplaints = complaints;

    displayComplaints(allComplaints);
}


// ========================================
// 6. Display Complaints in Table
// ========================================

function displayComplaints(complaints) {

    const table = document.getElementById(
        "complaintsTableBody"
    );

    if (!table) {

        console.error(
            "complaintsTableBody not found in dashboard.html"
        );

        return;
    }

    table.innerHTML = "";

    if (complaints.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="9">
                    No complaints found.
                </td>
            </tr>
        `;

        return;
    }

    complaints.forEach(complaint => {

        const severity =
            complaint.predicted_severity ||
            complaint.severity ||
            "N/A";

        const status =
            complaint.status || "Pending";

        table.innerHTML += `

            <tr>

                <!-- Complaint ID -->
                <td>
                    #${complaint.id}
                </td>

                <!-- User Registration ID -->
                <td>
                    ${complaint.user_id || "N/A"}
                </td>

                <!-- Location -->
                <td>
                    Block ${complaint.block_no}
                    <br>
                    Floor ${complaint.floor}
                    <br>
                    Room ${complaint.room_no}
                </td>

                <!-- Facility -->
                <td>
                    ${complaint.facility_type}
                </td>

                <!-- Issue -->
                <td>
                    ${complaint.issue_type}
                </td>

                <!-- Predicted Severity -->
                <td>
                    ${severity}
                </td>

                <!-- Complaint Date -->
                <td>
                    ${complaint.complaint_date || "N/A"}
                </td>

                <!-- Complaint Time -->
                <td>
                    ${formatTime(complaint.complaint_time)}
                </td>

                <!-- Maintenance Status -->
                <td>

                    <select
                        class="status-select"
                        onchange="updateComplaintStatus(
                            ${complaint.id},
                            this.value
                        )"
                    >

                        <option value="Pending"
                            ${status === "Pending" ? "selected" : ""}>
                            Pending
                        </option>

                        <option value="In Progress"
                            ${status === "In Progress" ? "selected" : ""}>
                            In Progress
                        </option>

                        <option value="Resolved"
                            ${status === "Resolved" ? "selected" : ""}>
                            Resolved
                        </option>

                    </select>

                </td>

            </tr>

        `;

    });
}


// ========================================
// 7. Search and Filter Complaints
// ========================================

function filterComplaints() {

    const searchInput = document.getElementById(
        "complaintSearch"
    );

    const statusInput = document.getElementById(
        "statusFilter"
    );

    const severityInput = document.getElementById(
        "severityFilter"
    );

    const searchText = searchInput
        ? searchInput.value.toLowerCase().trim()
        : "";

    const selectedStatus = statusInput
        ? statusInput.value
        : "All";

    const selectedSeverity = severityInput
        ? severityInput.value
        : "All";


    const filteredComplaints = allComplaints.filter(
        complaint => {

            const searchableText = [

                complaint.id,
                complaint.user_id,
                complaint.block_no,
                complaint.floor,
                complaint.room_no,
                complaint.facility_type,
                complaint.issue_type

            ].join(" ").toLowerCase();


            const severity =
                complaint.predicted_severity ||
                complaint.severity ||
                "N/A";

            const status =
                complaint.status || "Pending";


            const matchesSearch =
                searchableText.includes(searchText);

            const matchesStatus =
                selectedStatus === "All" ||
                status === selectedStatus;

            const matchesSeverity =
                selectedSeverity === "All" ||
                severity === selectedSeverity;


            return (
                matchesSearch &&
                matchesStatus &&
                matchesSeverity
            );

        }
    );


    displayComplaints(filteredComplaints);
}


// ========================================
// 8. Connect Search and Filter Events
// ========================================

function setupComplaintFilters() {

    const searchInput = document.getElementById(
        "complaintSearch"
    );

    const statusInput = document.getElementById(
        "statusFilter"
    );

    const severityInput = document.getElementById(
        "severityFilter"
    );

    if (searchInput) {
        searchInput.addEventListener(
            "input",
            filterComplaints
        );
    }

    if (statusInput) {
        statusInput.addEventListener(
            "change",
            filterComplaints
        );
    }

    if (severityInput) {
        severityInput.addEventListener(
            "change",
            filterComplaints
        );
    }
}


// ========================================
// 9. Update Complaint Status
// ========================================

async function updateComplaintStatus(
    complaintId,
    newStatus
) {

    try {

        await fetchData(
            `${API_URL}/complaints/${complaintId}/status`,
            {

                method: "PATCH",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    status: newStatus
                })

            }
        );


        alert(
            `Complaint #${complaintId} updated to ${newStatus}`
        );


        // Reload summary and complaints
        await loadSummary();

        await loadComplaints();

    }

    catch (error) {

        console.error(
            "Status Update Error:",
            error
        );

        alert(
            "Unable to update complaint status."
        );

        await loadComplaints();

    }
}


// ========================================
// 10. Load Recurring Facility Issues
// ========================================

async function loadRecurringIssues() {

    const issues = await fetchData(
        `${API_URL}/recurring-issues`
    );

    const container = document.getElementById(
        "recurringIssues"
    );

    container.innerHTML = "";

    if (issues.length === 0) {

        container.innerHTML =
            "<p>No recurring issues found yet.</p>";

        return;
    }

    issues.forEach(issue => {

        container.innerHTML += `

            <div class="risk-location">

                <div>

                    <strong>
                        Block ${issue.block_no}
                        → Floor ${issue.floor}
                        → Room ${issue.room_no}
                    </strong>

                    <p>
                        ${issue.facility_type}
                    </p>

                </div>

                <div class="risk-details">

                    <strong>
                        ${issue.issue_type}
                    </strong>

                    <p>
                        Reported ${issue.issue_count} times
                    </p>

                    <span class="alert-badge medium-alert">
                        Recurring Issue
                    </span>

                </div>

            </div>

        `;
    });
}


// ========================================
// 11. Load Complete Dashboard
// ========================================

async function loadDashboard() {

    try {

        setupComplaintFilters();

        await loadSummary();

        await loadHighRiskLocations();

        await loadComplaints();

        await loadRecurringIssues();

        console.log(
            "Dashboard loaded successfully!"
        );

    }

    catch (error) {

        console.error(
            "Dashboard Error:",
            error
        );

        const table = document.getElementById(
            "complaintsTableBody"
        );

        if (table) {

            table.innerHTML = `
                <tr>
                    <td colspan="9">
                        Unable to load complaints.
                        Check backend API and browser console.
                    </td>
                </tr>
            `;
        }

    }
}


// ========================================
// 12. Start Dashboard
// ========================================

loadDashboard();
