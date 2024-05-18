from flask import Flask, render_template, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from service import UserService

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(port=6000, debug=True)