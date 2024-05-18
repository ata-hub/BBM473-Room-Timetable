from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from service import UserService
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

user_service = UserService()

# @app.route("/")

# def login():
#     return render_template("login.html")

# Dummy room data (replace with actual data from the database)
room_data = [
    {"name": "Room 1"},
    {"name": "Room 2"},
    {"name": "Room 3"}
]

@app.route('/mainpage')
def userpage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]

    return render_template('userpage.html', room_data=room_data, time_slots=time_slots)

@app.route('/login', methods=['POST'])
def login(): 
    data = request.form  #TODO this can change later
    login_data = user_service.login(data)
    session['username'] = data['username']
    session['role'] = login_data['role']
    session['department'] = login_data['department_id']

    return login_data

@app.route('/give-permission', methods=['POST'])
def give_permission(): 
    data = request.form  
    return user_service.give_permission(data)

@app.route('/list-permission-requests', methods=['GET'])
def list_permission_requests(): 
    return user_service.list_awating_permission_requests()

@app.route('/request-permission', methods=['POST'])
def request_permission(): 
    data = request.form  
    return user_service.request_permission(data)

@app.route('/list-feature-requests', methods=['GET'])
def list_feature_requests(): 
    return user_service.list_awating_feature_requests()

@app.route('/logout', methods=['POST'])
def logout(): 
    return redirect(url_for('login'))   #TODO ???

if __name__ == "__main__":
    app.run(port=6000, debug=True)