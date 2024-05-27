from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

users = {
    'student_user': {'password': 'studentpass', 'role': 'student'},
    'instructor_user': {'password': 'instructorpass', 'role': 'instructor'},
    'admin_user': {'password': 'adminpass', 'role': 'admin'},
}

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
    #TODO roomları backendden al (permissionlardan al)
    return render_template('student.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="student")

@app.route('/instructor')
def instructorPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    #TODO roomları backendden al (bütün departman odaları)
    return render_template('instructor.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="instructor")

@app.route('/admin')
def adminPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    #TODO roomları backendden al sistmdeki tüm odalar
    return render_template('admin.html',
                            room_data=room_data,
                            time_slots=time_slots,
                            user_role="admin")


@app.route('/student_request', methods=['POST'])
def student_request():
    student_username = request.form['studentUsername']
    student_room = request.form['studentRoom']
    # TODO add student request to db (permissions table and student_request_permission)
    # Process the request here
    # TODO db işlemleri olumlu gerçekleştiyse return jsonify(success=True)
    # TODO db işlemleri olumsuz gerçekleştiyse return jsonify(success=False)
    # TODO db üstteki jsonifyları implement ettikten sonra aşağıdaki satırları sil
    # For now, we'll simulate success or failure
    if student_username and student_room:
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/feature_request', methods=['POST'])
def feature_request():
    feature = request.form['feature']
    feature_room = request.form['featureRoom']
    # TODO add feature request to db (istenen feature feature tableda yoksa ekle and feature_request_permission)
    # Process the request here
    # TODO db işlemleri olumlu gerçekleştiyse return jsonify(success=True)
    # TODO db işlemleri olumsuz gerçekleştiyse return jsonify(success=False)
    # TODO db üstteki jsonifyları implement ettikten sonra aşağıdaki satırları sil
    # For now, we'll simulate success or failure
    if feature and feature_room:
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/admin/pending_student_request')
def pending_student_requests():
    return render_template('student_requests.html')

@app.route('/admin/pending_feature_request')
def pending_feature_requests():
    return render_template('feature_requests.html')

@app.route('/events')
def eventsPage():
    
    return render_template('events.html', username = username)

if __name__ == "__main__":
    app.run(debug=True)