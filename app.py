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

@app.route('/mainpage')
def userpage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]

    return render_template('userpage.html', room_data=room_data, time_slots=time_slots)

if __name__ == "__main__":
    app.run(debug=True)