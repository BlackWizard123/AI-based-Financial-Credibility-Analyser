// Global state
let fileStorage = {};
let isValidating = false;
let validationComplete = false;

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

// Form functions
function convertToUppercase(input) {
    input.value = input.value.toUpperCase();
}

function formatAadharNumber(input) {
    let value = input.value.replace(/\D/g, '');
    value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
    input.value = value;
}

// File upload functions
function triggerFileUpload(fileInputId) {
    document.getElementById(fileInputId).click();
}

function handleFileUpload(input, type) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        fileStorage[type] = {
            file: file,
            preview: e.target.result
        };
        updateFilePreview(type, file.name, e.target.result);
    };
    reader.readAsDataURL(file);
}

function updateFilePreview(type, fileName, preview) {
    const previewDiv = document.getElementById(type + 'Preview');
    const placeholderDiv = document.getElementById(type + 'Placeholder');
    const fileNameSpan = document.getElementById(type + 'FileName');
    const uploadDiv = document.getElementById(type + 'Upload') || document.querySelector(`[onclick="triggerFileUpload('${type}File')"]`);

    if (previewDiv && placeholderDiv && fileNameSpan) {
        fileNameSpan.textContent = fileName;
        previewDiv.style.display = 'block';
        placeholderDiv.style.display = 'none';
        
        // Update upload div styling
        if (uploadDiv) {
            uploadDiv.classList.add('has-file');
        }

        // Update image preview for image files
        const imageElement = document.getElementById(type + 'Image');
        if (imageElement && preview.startsWith('data:image')) {
            imageElement.src = preview;
            imageElement.style.display = 'block';
        }
    }
}

function removeFile(type) {
    delete fileStorage[type];
    
    const previewDiv = document.getElementById(type + 'Preview');
    const placeholderDiv = document.getElementById(type + 'Placeholder');
    const fileInput = document.getElementById(type + 'File');
    const uploadDiv = document.getElementById(type + 'Upload') || document.querySelector(`[onclick="triggerFileUpload('${type}File')"]`);

    if (previewDiv && placeholderDiv) {
        previewDiv.style.display = 'none';
        placeholderDiv.style.display = 'block';
    }

    if (fileInput) {
        fileInput.value = '';
    }

    if (uploadDiv) {
        uploadDiv.classList.remove('has-file');
    }
}

function viewFile(type) {
    const file = fileStorage[type.replace('Preview', '')];
    if (file && file.preview) {
        window.open(file.preview, '_blank');
    }
}

// Initialize payslip labels with previous months
function initializePayslipLabels() {
    const now = new Date();
    const months = [];
    
    for (let i = 1; i <= 3; i++) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const monthYear = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        months.push(monthYear);
    }

    document.getElementById('payslip1Label').textContent = `Payslip - ${months[0]}`;
    document.getElementById('payslip2Label').textContent = `Payslip - ${months[1]}`;
    document.getElementById('payslip3Label').textContent = `Payslip - ${months[2]}`;
}

// Consent functions
function updateConsentStatus() {
    const checkboxes = ['dataProcessing', 'creditCheck', 'termsAndConditions', 'privacyPolicy'];
    const allChecked = checkboxes.every(id => document.getElementById(id).checked);
    
    const validateBtn = document.getElementById('validateBtn');
    const consentWarning = document.getElementById('consentWarning');
    
    validateBtn.disabled = !allChecked;
    
    if (allChecked) {
        consentWarning.style.display = 'none';
    } else {
        consentWarning.style.display = 'flex';
    }
}

function validateCredibility() {
    if (isValidating || validationComplete) return;

    const checkboxes = ['dataProcessing', 'creditCheck', 'termsAndConditions', 'privacyPolicy'];
    const allChecked = checkboxes.every(id => document.getElementById(id).checked);
    
    if (!allChecked) {
        alert('Please provide all required consents before proceeding.');
        return;
    }

    isValidating = true;
    const validateBtn = document.getElementById('validateBtn');
    const validateBtnText = document.getElementById('validateBtnText');
    const validateSpinner = document.getElementById('validateSpinner');
    
    validateBtn.disabled = true;
    validateBtnText.textContent = 'Validating Credibility...';
    validateSpinner.style.display = 'inline-block';

    // Simulate validation process
    setTimeout(() => {
        isValidating = false;
        validationComplete = true;
        
        document.getElementById('validationSection').style.display = 'none';
        document.getElementById('validationComplete').style.display = 'block';

        // ✅ Submit the form after validation completes
        document.getElementById('kycForm').submit();
        
    }, 5000);
}
