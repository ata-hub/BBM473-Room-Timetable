from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from service import UserService, RoomService
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)

user_service = UserService()
room_service = RoomService()

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
    session['logged_in'] = True

    return login_data

@app.route('/give-permission', methods=['POST'])
def give_permission(): 
    if 'logged_in' in session:
        data = request.form  
        return user_service.give_permission(data)

@app.route('/list-permission-requests', methods=['GET'])
def list_permission_requests(): 
    if 'logged_in' in session:
        return user_service.list_awating_permission_requests()

@app.route('/request-permission', methods=['POST'])
def request_permission(): 
    if 'logged_in' in session:
        data = request.form  
        return user_service.request_permission(data)

@app.route('/list-feature-requests', methods=['GET'])
def list_feature_requests(): 
    if 'logged_in' in session:
        return user_service.list_awating_feature_requests()

@app.route('/logout', methods=['POST'])
def logout(): 
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))   #TODO ???

@app.route('/features', methods=['GET'])
def features(): 
    if 'logged_in' in session:
        return room_service.list_features()

@app.route('/request-feature', methods=['POST'])
def request_feature():
    if 'logged_in' in session:
        data = request.form
        return room_service.request_feature(data)

@app.route('/add-feature', methods=['POST'])
def add_new_feature():
    if 'logged_in' in session:
        data = request.form
        return room_service.add_new_feature(data["name"])

@app.route('/make-reservation', methods=['POST'])
def make_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.make_reservation(data)

@app.route('/recurring-reservation', methods=['POST'])
def make_recurring_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.make_recurring_reservation(data)

@app.route('/reservations', methods=['GET'])
def list_reservation():
    if 'logged_in' in session:
        return room_service.list_user_reservations()

@app.route('/cancel', methods=['DELETE'])
def cancel_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.cancel_reservation(data["event_id"])

@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    if 'logged_in' in session:
        data = request.form
        return room_service.make_suggestion(data)

@app.route('/recurring-suggestions', methods=['GET'])
def get_recurring_suggestions():
    if 'logged_in' in session:
        data = request.form
        return room_service.make_recurring_suggestion(data)

@app.route('/timetable', methods=['GET'])
def get_timetable():
    data = request.form
    return room_service.get_timetable(data)

@app.route('/my-reservations', methods=['GET'])
def get_my_reservations():
    if 'logged_in' in session:
        data = request.form
        return room_service.get_my_reservations(data)
    
@app.route('/other-reservations', methods=['GET'])
def get_other_reservations():
    if 'logged_in' in session:
        data = request.form
        return room_service.get_other_reservarions(data)

@app.route('/export-timetable', methods=['GET'])
def export_timetable():
    if 'logged_in' in session:
        data = request.form
        return room_service.export_timetable(data)

if __name__ == "__main__":
    app.run(port=6000, debug=True)