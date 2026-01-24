import os
import json 
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
 
from models import db, User
from validation_logics import *

main_bp = Blueprint('main_bp', __name__)

# Load env vars and initialize blob connection
load_dotenv()
blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = "credimate-data"
container_client = blob_service.get_container_client(container_name)

@main_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not 'user_id':
        return redirect(url_for('login_page'))
    
    user = User.query.get(user_id)
    return render_template('home/main_page.html', user = user)


@main_bp.route('/submit_application', methods=['POST'])
def submit_application():
    user_id = session.get('user_id')
    if not user_id:
        return "User not logged in", 403

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    # Base folder: User_<id>_<firstname>/
    base_path = f"User_{user.id}_{user.first_name}/"

    # === 1. Upload Documents ===

    doc_fields = [
        "panCardFile", "aadharCardFile", "payslip1File", "payslip2File",
        "payslip3File", "bankStatementFile", "creditReportFile"
    ]
    docs_path = base_path + "docs/"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = f"{base_path}archive/docs_{timestamp}/"

    for field in doc_fields:
        file = request.files.get(field)
        if file and file.filename:
            # Get extension and clean it
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[-1].lower()

            # Use field name as file base to ensure overwriting
            safe_filename = f"{field}.{ext}"
            current_blob_path = docs_path + safe_filename
            archive_blob_path = archive_path + safe_filename

            blob_client = container_client.get_blob_client(current_blob_path)

            # === Archive existing file if it exists ===
            try:
                if blob_client.exists():
                    old_data = blob_client.download_blob().readall()
                    container_client.upload_blob(
                        name=archive_blob_path,
                        data=old_data,
                        overwrite=True
                    )
                    print(f"[ARCHIVED] {current_blob_path} → {archive_blob_path}")
            except Exception as e:
                print(f"[WARNING] Couldn't archive {current_blob_path}: {e}")

            # === Upload new file ===
            try:
                container_client.upload_blob(
                    name=current_blob_path,
                    data=file,
                    overwrite=True
                )
                print(f"[UPLOADED] {current_blob_path}")
            except Exception as e:
                print(f"[ERROR] Failed to upload {current_blob_path}: {e}")
    
    # === 2. Save Text Fields to user_inputs.json ===
    input_fields = [
        'fullName', 'fatherName', 'occupation', 'dob', 'employmentStatus','panNumber', 'aadharNumber'
    ]  
    user_inputs = {
        field: request.form.get(field) for field in input_fields
    }

    container_client.upload_blob(
        name=base_path + "metadata/user_inputs.json",
        data=json.dumps(user_inputs),
        overwrite=True
    )

    # === 3. Create/Append notification.json with "Submission received" ===
    notification_blob_path = base_path + "notification.json"
    new_entry = {
        "message": "Submission received and documents archived if replaced.",
        "timestamp": datetime.now().isoformat()
    }

    try:
        blob_client = container_client.get_blob_client(notification_blob_path)

        if blob_client.exists():
            # Download existing data
            existing_data = json.loads(blob_client.download_blob().readall())
            existing_data["notifications"].append(new_entry)
        else:
            # Create new if not found
            existing_data = {"notifications": [new_entry]}

        # Upload updated JSON
        container_client.upload_blob(
            name=notification_blob_path,
            data=json.dumps(existing_data),
            overwrite=True
        )

    except Exception as e:
        print(f"[ERROR] Could not update notification.json: {e}")

    return redirect(url_for('main_bp.validation_page'))


@main_bp.route("/validation")
def validation_page():  
    user_id = session.get('user_id')    
    user = User.query.get(user_id)
    return render_template('validation/validation_page.html', user = user)


@main_bp.route("/get_notifications")
def get_notifications():
    user_id = session.get("user_id")  # You must be logged in
    if not user_id:
        return jsonify({"notifications": []})

    user = User.query.get(user_id)
    if not user:
        return jsonify({"notifications": []})

    base_path = f"User_{user.id}_{user.first_name}/notification.json"
    try:
        blob_client = container_client.get_blob_client(base_path)
        blob_data = blob_client.download_blob().readall()
        notifications = json.loads(blob_data)
        return jsonify(notifications)
    except Exception as e:
        print(f"[ERROR] Notification fetch failed: {e}")
        return jsonify({"notifications": []})
    

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))



# Validation checklist process

# @main_bp.route('/validate_step/1', methods=['POST'])
# def validate_file_integrity_page():
#     success = True     #validate_file_integrity()

#     if success:
#         return jsonify(success=True, message="File integrity confirmed. No tampering found.")
#     else:
#         # Log to notification.json
#         user_id = session.get("user_id")
#         if user_id:
#             user = User.query.get(user_id)
#             notif_path = f"User_{user.id}_{user.first_name}/notification.json"
#             try:
#                 blob_client = container_client.get_blob_client(notif_path)
#                 existing = []
#                 if blob_client.exists():
#                     existing = json.loads(blob_client.download_blob().readall()).get("notifications", [])
#                 existing.append({
#                     "message": "Step 1 failed: Tampering detected in file integrity check.",
#                     "timestamp": datetime.now().isoformat()
#                 })
#                 container_client.upload_blob(name=notif_path, data=json.dumps({"notifications": existing}), overwrite=True)
#             except Exception as e:
#                 print("Notification log failed:", e)

#         return jsonify(success=False, message="Tampering detected in file metadata.")
    
@main_bp.route('/validate_step/<int:step_number>', methods=['POST'])
def validate_step(step_number):

    # Dummy logic – replace this with real per-step logic below
    step_messages = {
        1: "File integrity confirmed.",
        2: "Aadhar document appears valid.",
        3: "PAN card verified.",
        4: "KYC passed successfully.",
        5: "Document reading completed.",
        6: "Document analysis successful.",
        7: "Final evaluation done.",
        8: "Report generated.",
        9: "All steps completed."
    }

    failure_messages = {
        1: "Tampering detected.",
        2: "Invalid Aadhar card.",
        3: "PAN verification failed.",
        4: "KYC check failed.",
        5: "Failed to read documents.",
        6: "Analysis error.",
        7: "Final evaluation failed.",
        8: "Report generation failed.",
        9: "Post-process failed."
    }

    step_functions = {
        1: run_file_integrity_check,
        2: validate_aadhar,
        3: validate_pan,
        4: confirm_kyc_status,
        5: read_uploaded_documents,
        6: analyze_documents,
        7: run_final_evaluation,
        8: generate_report,
        9: wrapup
    }

    func = step_functions.get(step_number)
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if func:
        try:
            success = func(user)
        except Exception as e:
            print(f"Step {step_number} failed with exception:", e)
            success = False
    else:
        success = False

    if success:
        return jsonify(success=True, message=step_messages.get(step_number, "Step completed."))
    else:
        # Log failure to notification.json
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            notif_path = f"User_{user.id}_{user.first_name}/notification.json"
            try:
                blob_client = container_client.get_blob_client(notif_path)
                existing = []
                if blob_client.exists():
                    existing = json.loads(blob_client.download_blob().readall()).get("notifications", [])
                existing.append({
                    "message": f"Step {step_number} failed: {failure_messages.get(step_number)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                container_client.upload_blob(name=notif_path, data=json.dumps({"notifications": existing}), overwrite=True)
            except Exception as e:
                print("Notification log failed:", e)

        return jsonify(success=False, message=failure_messages.get(step_number, "Step failed."))
    
  
@main_bp.route('/report')
def report_page():
    user_id = session.get('user_id')    
    user = User.query.get(user_id)
    return render_template('report/report_page.html', user = user)