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
