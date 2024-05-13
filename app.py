from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route("/")

def login():
    return render_template("login.html")

# Dummy room data (replace with actual data from the database)
room_data = [
    {"name": "Room 1"},
    {"name": "Room 2"},
    {"name": "Room 3"}
]

@app.route('/student')
def studentPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    return render_template('student.html', room_data=room_data, time_slots=time_slots, is_student=True)

@app.route('/instructor')
def instructorPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    return render_template('instructor.html', room_data=room_data, time_slots=time_slots, is_instructor=True)

@app.route('/admin')
def adminPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    return render_template('admin.html', room_data=room_data, time_slots=time_slots, is_admin=True)

@app.route('/events')
def eventsPage():
    
    return render_template('events.html', username = username)

if __name__ == "__main__":
    app.run(debug=True)