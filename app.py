from datetime import datetime, timedelta, date
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
from service import MyException, RoomService, UserService

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)

user_service = UserService()
room_service = RoomService()

users = {
    'student_user': {'password': 'studentpass', 'role': 'student'},
    'instructor_user': {'password': 'instructorpass', 'role': 'instructor'},
    'admin_user': {'password': 'adminpass', 'role': 'admin'},
}

def get_dummy_reservations():
    return [
        {
            'event_id': 1,
            'title': 'Conference',
            'description': 'Annual Conference',
            'room_id': 101,
            'start_time': datetime.datetime(2024, 6, 15, 9, 0),
            'end_time': datetime.datetime(2024, 6, 15, 17, 0)
        },
        {
            'event_id': 2,
            'title': 'Workshop',
            'description': 'Python Workshop',
            'room_id': 202,
            'start_time': datetime.datetime(2024, 6, 16, 10, 0),
            'end_time': datetime.datetime(2024, 6, 16, 12, 0)
        }
        # Add more dummy bookings as needed
    ]

@app.route("/")
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST']) 
def login_post(): 
    data = {
        'username' : request.form.get('username'),
        'password' : request.form.get('password')
    }
    
    login_data = user_service.login(data)

    if login_data == "False":
        return jsonify(success=False, message="Wrong credentials.")
    else:
        session['username'] = data['username']
        session['role'] = login_data['role']
        session['department'] = login_data['department_id']
        session['logged_in'] = True

    if session['role'] == 'student':
        return jsonify(success=True, redirect_url=url_for('studentPage'))
    elif session['role'] == 'instructor':
        return jsonify(success=True, redirect_url=url_for('instructorPage'))
    else:
        return jsonify(success=True, redirect_url=url_for('adminPage'))
    
@app.route('/guest-login', methods=['GET'])
def guest_login():
    departments = user_service.get_all_departments()
    return jsonify(success=True, departments=departments)

# Dummy room data (replace with actual data from the database)
room_data = [
    "Room 1",
    "Room 2",
     "Room 3"
]

@app.route('/student')
def studentPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    #TODO roomları backendden al (permissionlardan al)
    room_data = user_service.get_user_rooms()
    return render_template('student.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="student",
                           username=session.get('username'),
                           department=session.get('department'))

@app.route('/instructor')
def instructorPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    #TODO roomları backendden al (bütün departman odaları)
    room_data = user_service.get_user_rooms()
    print("rooms for instructor:",room_data)
    return render_template('instructor.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="instructor",
                           username=session.get('username'),
                           department=session.get('department'))

@app.route('/admin')
def adminPage():
    # Define time slots
    time_slots = [f"{hour}:00" for hour in range(8, 20)]
    #TODO roomları backendden al sistmdeki tüm odalar
    room_data = user_service.get_user_rooms()
    return render_template('admin.html',
                            room_data=room_data,
                            time_slots=time_slots,
                            user_role="admin",
                            username=session.get('username'),
                            department=session.get('department'))

#instructor making student request
@app.route('/student_request', methods=['POST'])
def student_request():
    student_username = request.form['studentUsername']
    student_room = request.form['studentRoom']
    # TODO add student request to db (permissions table and student_request_permission)
    requestDto = {
        'username': student_username,
        'room': student_room
    }
    try:
        # Call the request_permission method with the requestDto
        result = user_service.request_permission(requestDto)
        if(result == 'True'):
            return jsonify(success=True)
    except MyException as e:
        # Handle custom exceptions
        return jsonify(success=False, message=str(e))
    except Exception as e:
        # Handle other exceptions
        return jsonify(success=False, message="An error occurred while processing the request.")
    
@app.route('/list_features', methods=['GET'])
def list_features():
    features = room_service.list_features()
    return jsonify(features=features)


@app.route('/feature_request', methods=['POST'])
def feature_request():
    feature = request.form.get('existingFeatures')
    print("feature is:",feature)
    new_feature = request.form.get('feature')
    feature_room = request.form.get('room')
    description = request.form.get('description')

    if feature == 'other':
        feature_id = None
    else:
        feature_id = feature
    print("feature_id is:", feature_id)
    requestDto = {
        'feature_id': feature_id,
        'new_feature': new_feature if feature_id is None else None,
        'room': feature_room,
        'description': description
    }
    print("dto is:",requestDto)
    #feature dropdownunda seçilen option other ise requestDto da feature_id null olacak, new_feature değeri girilen string olacak
    #eğer dropdownda other dışında bir şey seçilirse feature_id o seçilen featureın idsi olacak
    try:
        # Call the request_permission method with the requestDto
        result = room_service.request_feature(requestDto)
        if(result == 'True'):
            return jsonify(success=True)
    except MyException as e:
        # Handle custom exceptions
        print("MyException Error occured:",str(e) )
        return jsonify(success=False, message=str(e))
        
    except Exception as e:
        # Handle other exceptions
        print("Exception occured:",str(e) )
        return jsonify(success=False, message="An error occurred while processing the request.")

@app.route('/admin/pending_student_request')
def pending_student_requests():
    return render_template('student_requests.html')

@app.route('/admin/pending_feature_request')
def pending_feature_requests():
    return render_template('feature_requests.html')

@app.route('/events')
def eventsPage():
    # get reservation from backend service
    reservationList = get_dummy_reservations()
    #user_role = session.get('user_role')  # Adjust based on how you store the user role
    return render_template('events.html', reservationList=reservationList) # TODO user_role=user_role bunu ekle

if __name__ == "__main__":
    app.run(debug=True, port=7000)