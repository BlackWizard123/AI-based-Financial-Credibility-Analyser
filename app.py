import os
import json
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

from main import main_bp
from models import db, User

from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

load_dotenv()
app.secret_key = "naa thaan da LEO!!! LEO DAS"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://credimate_admin:#TechMahindra123@credimate-db.postgres.database.azure.com:5432/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = "credimate-data"
container_client = blob_service.get_container_client(container_name)

# db = SQLAlchemy(app)

db.init_app(app)
app.register_blueprint(main_bp, url_prefix='/')

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50), nullable=False)
#     last_name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     phone = db.Column(db.String(20), nullable=False)
#     password = db.Column(db.String(120), nullable=False)



@app.route('/')
def index():
    return render_template('login/index.html')

@app.route('/login')
def login_page():
    return render_template('login/login.html')

@app.route('/register')
def register_page():
    return render_template('login/register.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    print("inside")
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        new_user = User(
            first_name=firstName,
            last_name=lastName,
            email=email,
            phone=phone,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()

        # Get user ID after insertion
        user_folder = f"User_{new_user.id}_{new_user.first_name}/"
        notification_blob_path = f"{user_folder}notification.json"

        notification_content = {
        "notifications": [
            {
                "message": "Welcome!",
                "timestamp": datetime.now().isoformat()
            }
        ]
        }
        # Upload JSON to Azure
        container_client.upload_blob(
            name=notification_blob_path,
            data=json.dumps(notification_content),
            overwrite=True
        )

        print("working", firstName, lastName)
        return redirect(url_for('login_page'))

@app.route('/login_user', methods=['POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            print("success")
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main_bp.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login_page'))
    



if __name__ == '__main__':
    app.run(debug=True)