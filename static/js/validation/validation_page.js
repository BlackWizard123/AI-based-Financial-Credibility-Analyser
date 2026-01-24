
// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializePayslipLabels();
    updateConsentStatus();
});

// Navigation functions
function toggleDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('show');
}

function toggleNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    const sidebar = document.getElementById('notificationSidebar');
    overlay.classList.add('show');
    sidebar.classList.add('show');
}

function closeNotifications() {
    const overlay = document.getElementById('notificationOverlay');
    const sidebar = document.getElementById('notificationSidebar');
    overlay.classList.remove('show');
    sidebar.classList.remove('show');
}

function toggleNotificationContent(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('svg');
    
    content.classList.toggle('show');
    
    if (content.classList.contains('show')) {
        icon.style.transform = 'rotate(90deg)';
    } else {
        icon.style.transform = 'rotate(0deg)';
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('profileDropdown');
    const profileBtn = document.querySelector('.profile-btn');
    
    if (!profileBtn.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

const steps = [
    'Validating file integrity...',
    'Validating Aadhar card...',
    'Validating PAN card...',
    'KYC Verified',
    'Reading uploaded documents...',
    'Analyzing documents...',
    'Final evaluation...',
    'Generating report...',
    'Process completed!'
];

let current = 0;

function startEvaluation() {
    if (current >= steps.length) return;
    const stepId = `step${current + 1}`;
    const processDiv = document.getElementById(stepId);
    const textSpan = processDiv.querySelector('.process-title');
    const tick = processDiv.querySelector('.tick');

    textSpan.textContent = steps[current];

    if (current === 0) {
    // simulate tamper check dynamic change
    const changes = ["Checking metadata for tampering...", "Analyzing signature fields...", "Verifying document integrity..."];
    let i = 0;
    const interval = setInterval(() => {
        if (i < changes.length) {
        textSpan.textContent = changes[i];
        i++;
        } else {
        clearInterval(interval);
        completeStep();
        }
    }, 2000);
    return;
    }

    if (current === 1) {
    completeStep(() => {
        document.getElementById('otpAadhar').style.display = 'block';
    });
    return;
    }

    if (current === 2) {
    completeStep(() => {
        document.getElementById('otpPan').style.display = 'block';
    });
    return;
    }

    completeStep();
}

function completeStep(callback) {
    const stepId = `step${current + 1}`;
    const processDiv = document.getElementById(stepId);
    processDiv.classList.add('complete');
    processDiv.querySelector('.tick').classList.add('show');

    setTimeout(() => {
    current++;
    if (current < steps.length) {
        startEvaluation();
    } else {
        document.getElementById('showReportBtn').style.display = 'inline-block';
    }
    if (callback) callback();
    }, 1000);
}

async function loadNotifications() {
    const notificationsList = document.querySelector(".notifications-list");
    notificationsList.innerHTML = "";

    try {
        const response = await fetch("/get_notifications");
        const data = await response.json();

        data.notifications.reverse().forEach(note => {
            const item = document.createElement("div");
            item.className = "notification-item";

            item.innerHTML = `
                <div class="notification-header-item" onclick="toggleNotificationContent(this)">
                    <div>
                        <div class="notification-title">
                            <h3>${note.message}</h3>
                            <span class="new-badge">New</span>
                        </div>
                        <div class="notification-time">${formatTime(note.timestamp)}</div>
                    </div>
                    <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <polyline points="9,18 15,12 9,6"></polyline>
                    </svg>
                </div>
                <div class="notification-content">
                    ${note.details || ""}
                </div>
            `;
            notificationsList.appendChild(item);
        });

    } catch (err) {
        console.error("Failed to load notifications:", err);
    }
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();  // Format to readable date/time
}

document.addEventListener("DOMContentLoaded", loadNotifications);

// validation checklist process

async function validateStep(stepNumber, endpoint) {
  const stepId = `step${stepNumber}`;
  const stepDiv = document.getElementById(stepId);
  const tick = stepDiv.querySelector('.tick');
  const title = stepDiv.querySelector('.process-title');

  title.textContent += " (processing...)";

  try {
    const response = await fetch(endpoint, { method: 'POST' });
    const data = await response.json();

    if (data.success) {
      stepDiv.classList.add('complete');
      tick.classList.add('show');
      title.textContent = data.message;
    } else {
      stepDiv.classList.add('failed');
      tick.classList.add('failed');
      title.textContent = data.message || "Validation failed";

      // Wait 10s then redirect
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 10000);
    }

    return data;  // ✅ RETURN result object
  } catch (err) {
    console.error("Server error:", err);
    title.textContent = "Server error occurred";
    stepDiv.classList.add('failed');
    tick.classList.add('failed');
    setTimeout(() => {
      window.location.href = "/dashboard";
    }, 5000);
  }
}

async function startEvaluation() {
    let success = true; // Flag to track overall success

    // Define your steps in an array for cleaner iteration
    const steps = [1, 2, 3, 4, 5, 6, 7, 8, 9];

    for (const stepNumber of steps) {
        try {
            const result = await validateStep(stepNumber, `/validate_step/${stepNumber}`);

            if (!result.success) { // <--- THIS IS THE KEY CHECK!
                console.warn(`Step ${stepNumber} failed. Stopping further validation.`);
                success = false; // Mark overall process as failed
                // Optionally display a user    -friendly message for the specific failure
                alert(`Validation failed at Step ${stepNumber}: ${result.message}`);
                break; // Exit the loop on the first failure
            }
            // If result.success is true, loop continues to the next step
        } catch (error) {
            console.error(`An unexpected error occurred during step ${stepNumber}:`, error);
            success = false; // Mark overall process as failed due to an exception
            alert(`An unexpected error occurred during validation: ${error.message}`);
            break; // Exit the loop on an unexpected error
        }
    }

    if (success) {
        console.log("All validation steps completed successfully!");
        document.getElementById("showReportBtn").style.display = "inline-block";
    } else {
        console.log("Validation process completed with failures.");
    }



    // await validateStep(1, "/validate_step/1");
    // await validateStep(2, "/validate_step/2");  // Show OTP after
    // await validateStep(3, "/validate_step/3");
    // await validateStep(4, "/validate_step/4");
    // await validateStep(5, "/validate_step/5");
    // await validateStep(6, "/validate_step/6");
    // await validateStep(7, "/validate_step/7");
    // await validateStep(8, "/validate_step/8");
    // await validateStep(9, "/validate_step/9");
    // document.getElementById("showReportBtn").style.display = "inline-block";
//   document.getElementById('otpAadhar').style.display = 'block';
//   return;  // wait for OTP manually
}

// async function verifyOTP(type) {
//   const input = document.getElementById(`otp${type}Input`);
//   const value = input.value;
//   console.log(value)
//   if (/^\d{6}$/.test(value)) {
//     document.getElementById(`otp${type}`).style.display = 'none';
    
//     if (type === 'Aadhar') {
//       await validateStep(3, "/validate_step/3");
//       document.getElementById('otpPan').style.display = 'block';
//     } else if (type === 'PAN') {
//       await validateStep(4, "/validate_step/4");
//       await validateStep(5, "/validate_step/5");
//       await validateStep(6, "/validate_step/6");
//       await validateStep(7, "/validate_step/7");
//       await validateStep(8, "/validate_step/8");
//       await validateStep(9, "/validate_step/9");
//       document.getElementById("showReportBtn").style.display = "inline-block";
//     }
//   } else {
//     alert("Please enter a valid 6-digit OTP.");
//   }
// }


window.onload = startEvaluation;