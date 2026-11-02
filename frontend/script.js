const form = document.getElementById("complaintForm");

const severityValue = document.getElementById("severityValue");
const resultMessage = document.getElementById("resultMessage");
const errorMessage = document.getElementById("errorMessage");


form.addEventListener("submit", async function (event) {

    // Page refresh hone se rokta hai
    event.preventDefault();


    // User se form data lena
    const userType =
        document.getElementById("User_Type").value;

    const userId =
        document.getElementById("User_ID").value;

    const blockNo =
        document.getElementById("Block_No").value;

    const floor =
        document.getElementById("Floor").value;

    const roomNo =
        document.getElementById("Room_No").value;

    const facilityType =
        document.getElementById("Facility_Type").value;

    const issueType =
        document.getElementById("Issue_Type").value;

    const complaintDate =
        document.getElementById("Complaint_Date").value;

    const complaintTime =
        document.getElementById("Complaint_Time").value;


    // Check whether a photo was selected
    const photoInput =
        document.getElementById("Photo");

    let photoAvailable = "No";

    if (photoInput.files.length > 0) {
        photoAvailable = "Yes";
    }


    // Backend ko bhejne wala data
    const complaintData = {

        user_type: userType,
        user_id: userId,

        block_no: Number(blockNo),
        floor: Number(floor),
        room_no: Number(roomNo),

        facility_type: facilityType,
        issue_type: issueType,

        complaint_date: complaintDate,
        complaint_time: complaintTime,

        photo_available: photoAvailable
    };


    try {

        // User ko processing status dikhana
        severityValue.textContent =
            "Processing...";

        resultMessage.textContent =
            "Your complaint is being analyzed.";

        errorMessage.textContent = "";


        // FastAPI backend ko request
        const response = await fetch(
            "http://127.0.0.1:8000/submit-complaint",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    complaintData
                )
            }
        );


        // Backend error handle karna
        if (!response.ok) {

            throw new Error(
                "Unable to submit complaint."
            );
        }


        // Backend response
        const result =
            await response.json();


        // User ko result dikhana
        severityValue.textContent =
            result.predicted_severity;

        resultMessage.textContent =
            `Complaint ID: ${result.complaint_id} | Status: ${result.status}`;


        console.log(
            "Complaint Result:",
            result
        );

    }

    catch (error) {

        console.error(error);

        severityValue.textContent =
            "Submission Failed";

        resultMessage.textContent =
            "Please try again.";

        errorMessage.textContent =
            "Make sure the FastAPI server is running.";
    }

});