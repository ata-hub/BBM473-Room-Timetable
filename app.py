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

# *** USER SERVICE ***
@app.route('/login', methods=['POST'])  # WORKS
def login(): 
    data = request.form 
    login_data = user_service.login(data)
    session['username'] = data['username']
    session['role'] = login_data['role']
    session['department'] = login_data['department_id']
    session['logged_in'] = True

    return login_data

@app.route('/give-permission', methods=['POST']) #WORKS
def give_permission(): 
    if 'logged_in' in session:
        data = request.form  
        return user_service.give_permission(data)

@app.route('/list-permission-requests', methods=['GET'])  #WORKS
def list_permission_requests(): 
    if 'logged_in' in session:
        return user_service.list_awating_permission_requests()

@app.route('/request-permission', methods=['POST'])  # WORKS
def request_permission(): 
    if 'logged_in' in session:
        data = request.form  
        return user_service.request_permission(data)

@app.route('/list-feature-requests', methods=['GET'])   # WORKS
def list_feature_requests(): 
    if 'logged_in' in session:
        return user_service.list_awating_feature_requests()
    
@app.route('/user-rooms', methods=['GET'])  # WORKS
def get_user_rooms():
     if 'logged_in' in session:
        return user_service.get_user_rooms()

@app.route('/logout', methods=['POST'])  # WORKS
def logout(): 
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))   


# *** ROOM SERVICE ***
@app.route('/features', methods=['GET'])  #WORKS
def features(): 
    if 'logged_in' in session:
        return room_service.list_features()

@app.route('/room-details', methods=['GET'])  # WORKS
def room_details(): 
    if 'logged_in' in session:
        return room_service.list_room_details()

@app.route('/request-feature', methods=['POST'])  # WORKS
def request_feature():
    if 'logged_in' in session:
        data = request.form
        return room_service.request_feature(data)

@app.route('/add-feature', methods=['POST'])  # WORKS
def add_new_feature():
    if 'logged_in' in session:
        data = request.form
        return room_service.add_new_feature(data)

@app.route('/make-reservation', methods=['POST']) # WORKS
def make_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.make_reservation(data)

@app.route('/recurring-reservation', methods=['POST'])  # WORKS
def make_recurring_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.make_recurring_reservation(data)

@app.route('/reservations', methods=['GET'])  # WORKS
def list_reservation():
    if 'logged_in' in session:
        return room_service.list_user_reservations()

@app.route('/cancel', methods=['DELETE'])  # WORKS BUT WHY SO SLOW AAAAA
def cancel_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.cancel_reservation(data["event_id"])
    
@app.route('/change', methods=['POST'])  # WORKS
def change_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.change_reservation(data)
    
@app.route('/change-recurring', methods=['POST'])  # WORKS
def change_recurring_reservation():
    if 'logged_in' in session:
        data = request.form
        return room_service.change_recurring_reservation(data)
    
@app.route('/change-event', methods=['POST'])  # WORKS
def change_event_details():
    if 'logged_in' in session:
        data = request.form
        return room_service.change_event_details(data)

@app.route('/timetable', methods=['GET']) # WORKS
def get_timetable():
    start = request.form.get('start', None)
    end = request.form.get('end', None)
    department = request.form.get('department', session.get('department'))
    return room_service.get_timetable(start, end, department)

@app.route('/my-reservations', methods=['GET'])  # WORKS
def get_my_reservations():
    if 'logged_in' in session:
        start = request.form.get('start', None)
        end = request.form.get('end', None)
        return room_service.get_my_reservations(start, end)
    
@app.route('/other-reservations', methods=['GET'])   # WORKS
def get_other_reservations():
    if 'logged_in' in session:
        start = request.form.get('start', None)
        end = request.form.get('end', None)
        return room_service.get_other_reservarions(start, end)

@app.route('/export', methods=['GET'])
def export_timetable():
    if 'logged_in' in session:
        data = request.form
        start = request.form.get('start', None)
        end = request.form.get('end', None)
        format = request.form.get('format', 'excel')
        return room_service.export_timetable(start, end, format)

if __name__ == "__main__":
    app.run(port=6000, debug=True)