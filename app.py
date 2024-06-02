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

repeatDict = {
    'weekly': 7,
    'monthly': 30,
    'yearly': 365
}

def timeslots(start_time_str, end_time_str):
    start_time = datetime.strptime(start_time_str, '%H:%M')
    end_time = datetime.strptime(end_time_str, '%H:%M')
    current_time = start_time
    intervals = []

    while current_time <= end_time:
        intervals.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=30)

    return intervals

def get_dummy_reservations():
    return [
        {
            'event_id': 1,
            'title': 'Conference',
            'description': 'Annual Conference',
            'room_id': 101,
            'start_time': datetime(2024, 6, 15, 9, 0),
            'end_time': datetime(2024, 6, 15, 17, 0)
        },
        {
            'event_id': 2,
            'title': 'Workshop',
            'description': 'Python Workshop',
            'room_id': 202,
            'start_time': datetime(2024, 6, 16, 10, 0),
            'end_time': datetime(2024, 6, 16, 12, 0)
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

@app.route('/render-guest-page', methods=['GET'])
def guest_render():
    department_id = request.args.get('departmentId')
    department_name = request.args.get('departmentName')
    return jsonify(success=True, redirect_url=url_for('guestPage', department_name=department_name, department_id=department_id))

@app.route('/guest', methods=['GET', 'POST'])
def guestPage():
    # Define time slots
    # time_slots = [f"{hour}:00" for hour in range(8, 20)]
    # department = request.form.get('departmentName')
    # session['department'] = request.form.get('departmentId')
    department_name = request.args.get('department_name')
    department_id = request.args.get('department_id')
    room_data = user_service.get_department_rooms(department_id)
    reservations = room_service.get_timetable(None, None, department_id)
    time_slots = timeslots('08:00', '20:00')

    if reservations == "False":
        reservations = []
    
    return render_template('guest.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="guest",
                           department=department_id,
                           reservations=reservations,
                           redirect_url=url_for('guestPage'))

@app.route('/get-by-day', methods=['GET'])
def get_reservation_for_day():
    day = request.args.get('day')
    mine = room_service.get_my_reservations_for_day(day)
    other = room_service.get_other_reservarions_for_day(day)
    print("mine: ", mine)
    print("other: ", other)
    return jsonify({
        'my_reservations': mine,
        'other_reservations': other
    })

@app.route('/get-by-dep', methods=['GET'])
def get_by_department():
    day = request.args.get('day')
    dep = request.args.get('dep')
    reservations = room_service.get_timetable(day, day, dep)
    
    if reservations == "False":
        reservations = []

    return jsonify({
        'reservations': reservations
    })

@app.route('/student')  # TODO  bunu test et
def studentPage():
    time_slots = timeslots('08:00', '20:00')
    room_data = user_service.get_user_rooms()
    mine = room_service.get_my_reservations_for_day(None)
    other = room_service.get_other_reservarions_for_day(None)

    return render_template('student.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="student",
                           username=session.get('username'),
                           department=session.get('department'))

@app.route('/instructor')
def instructorPage():
    room_data = user_service.get_user_rooms()
    mine = room_service.get_my_reservations_for_day(None)
    other = room_service.get_other_reservarions_for_day(None)
    time_slots = timeslots('08:00', '20:00')

    if mine == "False":
        mine = []
    if other == "False":
        other = []
    # my_reservations = room_service.get_my_reservations_for_day(None)

    return render_template('instructor.html', 
                           room_data=room_data, 
                           time_slots=time_slots, 
                           user_role="instructor",
                           my_reservations=mine, 
                           other_reservations=other,
                           username=session.get('username'),
                           department=session.get('department'))

@app.route('/admin')   # TODO bunu test et
def adminPage():
    time_slots = timeslots('08:00', '20:00')
    room_data = user_service.get_user_rooms()
    mine = room_service.get_my_reservations_for_day(None)
    other = room_service.get_other_reservarions_for_day(None)

    return render_template('admin.html',
                            room_data=room_data,
                            time_slots=time_slots,
                            user_role="admin",
                            username=session.get('username'),
                            department=session.get('department'))

#instructor making student request
@app.route('/student_request', methods=['POST'])
def student_request():
    student_username = request.form.get('studentUsername')
    student_room = request.form.get('studentRoom')
    
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
        'room_id': feature_room,
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
    requests = UserService().list_awating_permission_requests()
    print("pending student requests:", requests)
    return render_template('pending_students.html', requests=requests, user_role="admin")

@app.route('/admin/accept_student_request', methods=['POST'])
def accept_student_requests():
    data = request.json
    print("data received:",data)
    permission_id = data.get('permission_id')
    acceptance = data.get('acceptance')
    permissionDto={"id": permission_id, "acceptance": acceptance}
    try:
        result = UserService().give_permission(permissionDto)
        if result is not None:  # Check if result is not None before subscripting
            if result:  # Assuming result is a dictionary with 'success' and 'message' keys
                return jsonify({"success": True, "message": result})
            else:
                return jsonify({"success": False, "message": "Permission not granted."}), 400
        else:
            return jsonify({"success": False, "message": "Failed to process the request."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/admin/pending_feature_request')
def pending_feature_requests():
    requests = user_service.list_awating_feature_requests()
    return render_template('pending_features.html', requests=requests, user_role="admin")

@app.route('/admin/accept_feature_request', methods=['POST'])
def accept_feature_permission():
    data = request.json
    print("feature data:", data)
    request_id = data.get('request_id')
    acceptance = data.get('acceptance')
    requestDto={"request_id": request_id, "acceptance": acceptance}
    try:
        result = room_service.add_new_feature(requestDto)
        if result:
            return jsonify({"success": True, "message": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/reservation', methods=['POST'])  
def make_reservation():
    day = request.form.get('day')
    start_time = request.form.get('start_time') 
    end_time = request.form.get('end_time') 
    room = request.form.get('room')
    title = request.form.get('title')
    description = request.form.get('description')
    repeat = request.form.get('repeat')
    end_date = request.form.get('end_date')

    requestDto = {
            'title': title, 
            'description': description, 
            'start_time': start_time,
            'end_time': end_time,
            'room': room
        }

    try:
        if repeat == 'today':
            requestDto['day'] = day

            result = room_service.make_reservation(requestDto)
        else:
            requestDto['start_day'] = day
            requestDto['end_day'] = end_date
            requestDto['interval'] = repeatDict[repeat]
            
            result = room_service.make_recurring_reservation(requestDto)

        if result == "True":
            return jsonify({"success": True}), 200
        elif result == "No suggestion":
            return jsonify({"success": False, "message": "No suggestions"}), 400
        elif result == "False":
            return jsonify({"success": False, "message": "error"}), 400
        else:
            return jsonify({"success": False, "suggestions": result}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/events', methods=['GET'])
def eventsPage():
    # get reservation from backend service
    reservationList = room_service.get_all_my_reservations()
    user_role = session.get("role")
    username = session.get("username")
    room_data = user_service.get_user_rooms()
    print("room_data:", room_data)
    return render_template('events.html', reservationList=reservationList, 
                           user_role=user_role,
                           room_data=room_data,
                           username=username)

@app.route('/cancel-reservation', methods=['POST'])  # TODO test et
def cancel_reservation_route():
    if request.method == 'POST':
        # Get the event_id from the request data
        event_id = request.form.get('event_id')

        # Call the cancel_reservation function from your service.py
        result = room_service.cancel_reservation(event_id)

        # You might want to return a response based on the result of the cancellation
        if result == "True":
            return "Reservation cancelled successfully", 200
        else:
            return "Failed to cancel reservation", 500
    else:
        # Handle unsupported methods
        return "Method not allowed", 405
#my booking update function calls these two functions
@app.route('/change_event_details', methods=['POST'])
def change_event_details_controller():
    event_dto = request.json
    print("Change event received object:", event_dto)
    changed_fields = event_dto.get('changed_fields', [])
    event_id = event_dto.get('event_id')
    
    # Create a new eventDto
    eventDto = {
        'title': None,
        'description': None,
        'event_id': event_id
    }

    # Update eventDto with changed fields
    for field in changed_fields:
        if field['key'] == 'title':
            eventDto['title'] = field['value']
        elif field['key'] == 'description':
            eventDto['description'] = field['value']

    result = room_service.change_event_details(eventDto)
    print("Change event result:", result)
    return jsonify({'result': result})

#my booking update function calls these two functions
@app.route('/change_reservation', methods=['POST'])
def change_reservation_controller():
    change_dto = request.json
    print("Change reservation received object:", change_dto)
    changed_fields = change_dto.get('changed_fields', [])
    event_id = change_dto.get('event_id')

    # Create a new changeDto
    changeDto = {
        'to_start': None,
        'to_end': None,
        'day': None,
        'room': None,
        'event_id': event_id
    }

    # Update changeDto with changed fields
    for field in changed_fields:
        if field['key'] == 'to_start':
            changeDto['to_start'] = field['value']
        elif field['key'] == 'to_end':
            changeDto['to_end'] = field['value']
        elif field['key'] == 'day':
            changeDto['day'] = field['value']
        elif field['key'] == 'room':
            changeDto['room'] = field['value']

    result = room_service.change_reservation(changeDto)
    print("Change reservation result:", result)
    return jsonify({'result': result})

@app.route('/export', methods=['GET'])
def download_timetable():
    format = request.args.get('format')  
    start = request.args.get('start')
    end = request.args.get('end')
    return room_service.export_timetable(start, end, format)

if __name__ == "__main__":
    app.run(debug=True, port=7001)