from db import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import session, send_file
from datetime import timedelta, date, datetime
import pandas as pd
import csv
import os   
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MyException(Exception):
    pass

class UserService(): 
    # frontend -> backend: username, password 
    def login(self, userDto):  #TODO şifreyi db de gizle
        username = userDto['username']
        password = userDto['password']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()

        if user_data:
            conn.close()
            del user_data['password']
            return user_data
        else:
            conn.close()
            # raise MyException('This user does not exist or is not allowed to enter this website.')
            return "False"
        
    # frontend -> backend: permission_request_id, acceptance 
    # backend -> frontend: sonuç
    def give_permission(self, permissionDto):   # for admin 
        permission_id = permissionDto["id"]
        acceptance = permissionDto["acceptance"] 
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        current_user_role = session.get('role')
        
        cursor.execute("SELECT * FROM room_permission_requests WHERE request_id = %s", (permission_id, ))
        permission = cursor.fetchone()
        
        username = permission["username"]
        room_id = permission["room_id"]

        if current_user_role == 'admin' and acceptance:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
            user_exists = cursor.fetchone()

            if user_exists is None: 
                cursor.execute('SELECT * FROM school_students WHERE student_id = %s', (username,))
                student = cursor.fetchone()
                password = student['country_id']
                cursor.execute("INSERT INTO users(username, password, role, department_id) VALUES (%s, %s, 'student', %s)", (username, password, student['department_id']))

            cursor.execute("""INSERT INTO user_permissions(username, room_id) 
                           SELECT %s, %s 
                           WHERE EXISTS (
                           SELECT 1 
                           FROM users u
                           JOIN rooms r ON u.department_id = r.department_id
                           WHERE u.username = %s AND r.room_id = %s
                           ) AND 
                           NOT EXISTS (
                           SELECT username, room_id FROM user_permissions WHERE username = %s 
                           AND room_id = %s
                           )
                           """, 
                           (username, room_id, username, room_id, username, room_id))
            conn.commit()

            if cursor.rowcount != 1:
                raise MyException("Can't give permission for a room in another department other than the student's own department or if the permission exists")
        
        if current_user_role != 'admin':
            raise MyException('This user is not allowed to give permissions.')
        
        cursor.execute("DELETE FROM room_permission_requests WHERE request_id = %s", (permission_id, ))
        conn.commit()
        conn.close()
        return "True"

    # frontend -> backend: username, room_id 
    # backend -> frontend: sonuç
    def request_permission(self, requestDto):   # for instructor
        username = requestDto['username']
        room_id = requestDto['room']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        current_user_department = session.get('department')

        cursor.execute("""INSERT INTO room_permission_requests(room_id, username) 
                          SELECT %s, %s
                          WHERE EXISTS (
                          SELECT 1 
                          FROM rooms r
                          WHERE r.room_id = %s AND r.department_id = %s
                          )""", 
                          (room_id, username, room_id, current_user_department))
        conn.commit()

        if cursor.rowcount != 1:
            return "False"

        conn.close()
        return 'True'

    def list_awating_permission_requests(self):    # for admin 
        department = session.get('department')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # filter permissons by admin's department
        cursor.execute("""SELECT rpr.request_id, rpr.room_id, rpr.username, r.name
                       FROM room_permission_requests rpr, rooms r 
                       WHERE rpr.room_id = r.room_id AND r.department_id = %s""", (department, ))
        permissions = cursor.fetchall()
        return permissions

    def list_awating_feature_requests(self):   # for admin 
        department = session.get('department')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # filter permissons by admin's department
        cursor.execute("""SELECT fr.request_id, fr.room_id, fr.feature_id, fr.description, 
                       r.name AS name, f.name AS feature_name
                       FROM feature_requests fr, rooms r, features f
                       WHERE fr.room_id = r.room_id AND fr.feature_id = f.feature_id 
                       AND r.department_id = %s""", (department, ))
        requests = cursor.fetchall()
        return requests

    def get_user_rooms(self):   
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        user_department = session.get('department')
        user = session.get('username')
        role = session.get('role')
        rooms = []

        if role == 'student': 
            cursor.execute("""SELECT r.name, r.room_id FROM user_permissions up, rooms r 
                           WHERE up.room_id = r.room_id
                           AND username = %s""", (user, ))
            rooms = cursor.fetchall()

        elif role == 'instructor':
            cursor.execute("SELECT name, room_id FROM rooms WHERE department_id = %s", (user_department, ))
            rooms = cursor.fetchall()

        else:
            cursor.execute("""SELECT r.name AS name, r.room_id FROM rooms r, departments d
                           WHERE r.department_id = d.department_id
                           AND r.department_id = %s OR r.department_id = 0
                           """, (user_department, ))
            
            rooms = cursor.fetchall()
            # rooms = [(str(item["dname"]) + " - " + str(item["rname"])) for item in room_data]

        return rooms
    
    def get_department_rooms(self, department):   
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT name, room_id FROM rooms 
                        WHERE department_id = %s""", (department, ))

        rooms = cursor.fetchall()
        return rooms

    def get_all_departments(self):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT name, department_id FROM departments")
        departments = cursor.fetchall()
        return departments

    def logout(self):
        session.clear()
        return 'True'

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql = file.read()
    return sql

def change_date_format(date):   #turns dd-mm-yyyy to mm-dd-yyyy
    day = date.split("-")[0]
    month = date.split("-")[1]

    return month + "-" + day + "-" + date.split("-")[-1]

def calculate_interval(event_id):  
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #tx_sql = read_sql_file("./sql/calculate_interval.sql")
    cursor.execute("""WITH BookingPairs AS (
                    SELECT
                        b1.booking_id AS booking_id1,
                        b2.booking_id AS booking_id2,
                        b1.event_id,
                        t1.date AS date1,
                        t2.date AS date2,
                        ABS(t1.date - t2.date) AS date_diff
                    FROM
                        bookings b1
                        INNER JOIN bookings b2 ON b1.event_id = b2.event_id 
                        AND b1.booking_id < b2.booking_id
                        INNER JOIN timeslots t1 ON b1.timeslot_id = t1.timeslot_id
                        INNER JOIN timeslots t2 ON b2.timeslot_id = t2.timeslot_id
                        WHERE b1.event_id = %s
                )
                SELECT
                    date_diff
                FROM
                    BookingPairs """, (event_id, ))

    interval = cursor.fetchone()["date_diff"]
    return interval
    
class RoomService(): 
    def list_room_details(self): 
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        user_department = session.get('department')
        user = session.get('username')
        role = session.get('role')
        rooms = []

        if role == 'student': 
            cursor.execute("""SELECT r.name AS room_name, r.capacity, r.type, f.name AS feature_name, rf.is_working
                           FROM user_permissions up, rooms r, room_features rf, features f
                           WHERE up.room_id = r.room_id
                           AND r.room_id = rf.room_id 
                           AND rf.feature_id = f.feature_id
                           AND username = %s
                           AND f.is_accepted = true""", (user, ))
            rooms = cursor.fetchall()

        elif role == 'instructor':
            cursor.execute("""SELECT r.name AS room_name, r.capacity, r.type, f.name AS feature_name, rf.is_working 
                           FROM rooms r, room_features rf, features f 
                           WHERE r.room_id = rf.room_id
                           AND rf.feature_id = f.feature_id
                           AND r.department_id = %s
                           AND f.is_accepted = true""", (user_department, ))
            rooms = cursor.fetchall()

        else:
            cursor.execute("""SELECT d.name AS departmant_name, r.name AS room_name, r.capacity, r.type, f.name, rf.is_working 
                           FROM rooms r, departments d, room_features rf, features f 
                           WHERE r.department_id = d.department_id
                           AND r.room_id = rf.room_id
                           AND rf.feature_id = f.feature_id
                           AND d.department_id = %s OR d.department_id = 0
                           AND f.is_accepted = true""", (user_department, ))
            
            room_data = cursor.fetchall()
            rooms = [(str(item["departmant_name"]) + " - " + str(item["room_name"])) for item in room_data]

        return rooms
    # backend -> frontend: liste
    def list_features(self): # this is for listing all possible features for request
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT name, feature_id FROM features WHERE is_accepted = true")
        features = cursor.fetchall()
        return features  

    # frontend -> backend: description, feature_id, room_id
    # backend -> frontend: boolean?
    # ÖNEMLİ: logic şu şekilde: eğer feature zaten olan bir şeyse, is_working false'a çekilecek
    # ama yeni istenen bir şeyse bu ***description*** yazılacak ve sonra admin onaylarsa 
    # features table ına düşecek
    def request_feature(self, featureDto):    # for inst (in the future student too)
        description = featureDto["description"]
        feature_id = featureDto["feature_id"]
        room_id = featureDto["room_id"]
        new_feature = featureDto["new_feature"]

        tx_sql = read_sql_file('./sql/request_old_feature.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if feature_id:   #bu çalışacak mı null olursa?
            cursor.execute(tx_sql, {   
                'feature_id': feature_id,
                'description': description,
                'room_id': room_id
            }) 
            conn.commit()
        elif new_feature:  
            cursor.execute("INSERT INTO features (name, is_accepted) VALUES (%s, %s) RETURNING feature_id", (new_feature, False))
            conn.commit()

            new_feature_id = cursor.fetchone()
            print("feature id: ", new_feature_id)
            id = new_feature_id['feature_id']

            print("just id: ", id)

            cursor.execute("""INSERT INTO feature_requests (description, room_id, feature_id)
                           VALUES (%s, %s, %s)""", (new_feature, room_id, id))
            conn.commit()
        
        conn.close()
        return "True"  
    
    # frontend -> backend: feature_id, acceptance 
    # backend -> frontend: boolean?
    def add_new_feature(self, requestDto):   # for admin
        request_id = requestDto["request_id"]
        acceptance = requestDto["acceptance"]
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # eğer bu features tableında varsa -room_featuresda workinge çevir
        # eğer yoksa bir de featuresa ekle
        if acceptance:
            cursor.execute("""SELECT fr.*, f.is_accepted FROM feature_requests fr, features f
                           WHERE fr.feature_id = f.feature_id 
                           AND fr.request_id = %s""", (request_id, ))
            
            request = cursor.fetchone()

            if request["is_accepted"] == True:  # if adding existing feature
                tx_sql = read_sql_file("./sql/add_existing_feature.sql")

                cursor.execute(tx_sql, {
                    'feature_id': request["feature_id"],
                    'room_id': request["room_id"]
                })

                conn.commit()
            else:
                tx_sql = read_sql_file("./sql/add_new_feature.sql")
                
                cursor.execute(tx_sql, {
                    'feature_var': request["feature_id"],
                    'room_id': request["room_id"]
                })

                conn.commit()

        cursor.execute("DELETE FROM feature_requests WHERE request_id = %s", (request_id, ))
        conn.commit()
        conn.close()
        return "True"
        
    # frontend -> backend: 
    # backend -> frontend: boolean?
    def make_reservation(self, reservationDto): #TODO bu  ikisine de email atma ekle
        user = session.get('username')
        event_title = reservationDto['title']
        event_description = reservationDto['description']
        start_time = reservationDto['start_time'] + ":00"   
        end_time = reservationDto['end_time'] +":00"        
        day = reservationDto['day']
        room = reservationDto['room'] 

        tx_sql = read_sql_file('./sql/booking_tx.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(tx_sql, {
                'to_start': start_time,
                'to_end': end_time,
                'day': day,
                'room': room,
                'curr_user': user,
                'event_title': event_title,
                'event_desc': event_description
            })

            conn.commit()
            return "True"
        
        except psycopg2.Error as e:
            conn.rollback()

            if "this timeslot is taken" in str(e):
                suggestionDto = {key: value for key, value in reservationDto.items() if key in {
                'start_time', 'end_time', 'day', 'room'}}

                suggestions = self.make_suggestion(suggestionDto)

                if suggestions:
                    return suggestions
                else:
                    return "No suggestion"
            else:
                return "False"
        finally:
            cursor.close()
            conn.close()

    def make_recurring_reservation(self, reservationDto):
        user = session.get('username')
        event_title = reservationDto['title']
        event_description = reservationDto['description']
        start_time = reservationDto['start_time'] + ":00"   
        end_time = reservationDto['end_time'] +":00"
        start_day = reservationDto['start_day']
        end_day = reservationDto['end_day']
        room = reservationDto['room']
        interval = reservationDto['interval']

        tx_sql = read_sql_file('./sql/recurring_booking_tx.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try :
            cursor.execute(tx_sql, {
                'to_start': start_time,
                'to_end': end_time,
                'start_day': start_day,
                'end_day': end_day,
                'room': room,
                'curr_user': user,
                'event_title': event_title,
                'event_desc': event_description,
                'interval': interval
            })

            conn.commit()
            return "True"
        
        except psycopg2.Error as e:
            conn.rollback()

            if 'this timeslot is taken' in str(e):
                suggestionDto = {key: value for key, value in reservationDto.items() if key in {
                'start_time', 'end_time', 'start_day', 'end_day', 'room', 'interval'}}

                suggestions = self.make_recurring_suggestion(suggestionDto)

                if suggestions:
                    return suggestions
                else:
                    return "No suggestion"
            else:
                return "False"
        finally:
            cursor.close()
            conn.close()

    # backend -> frontend: reservation details list
    def list_user_reservations(self):    # all the reservations the user has made, returns date as dd-mm-yyyy
        user = session.get('username')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""SELECT e.event_id, e.title, e.description, 
                       b.room_id, to_char(t.date, 'dd-mm-yyyy'), t.start_time, t.end_time  
                       FROM events e 
                       INNER JOIN bookings b on b.event_id = e.event_id 
                       INNER JOIN timeslots t on t.timeslot_id = b.timeslot_id 
                       WHERE e.organizer = %s 
                       ORDER BY t.date ASC,
                       t.start_time ASC""", (user,))   
        
        reservations = cursor.fetchall()

        if reservations is None:
            return "False"
        
        for row in reservations:
            if 'start_time' in row:
                 row['start_time'] = row['start_time'].isoformat()
            if 'end_time' in row:
                 row['end_time'] = row['end_time'].isoformat()
        
        return reservations 

    # frontend -> backend: event_id
    def cancel_reservation(self, event_id):   
        user = session.get('username')
        tx_sql = read_sql_file('./sql/delete_event.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            email_subject = "Event cancelled."
            email_content = " titled event has been cancelled"
            self.send_emails(email_content, email_subject, event_id)
            
            cursor.execute(tx_sql, {'event_id': event_id, 'curr_user': user})
            conn.commit()
            return "True"
        except psycopg2.Error as e:
            conn.rollback()
            return "False"
        finally:
            cursor.close()
            conn.close()

    # def cancel_booking(self, booking_id):  #TODO - zaman kalırsa, booking_id de döndür list_user_reservationda

    # frontend kısmı için: chnage butonuna bastığında kutucuklar: room, start time, end time, date 
    # (eğer recurring ise bir kutucuk daha ve end date bu da)
    # bunlarda ilk başta olan reservationın değerleri yazıyor yani hepsi dolu
    # kullanıcı değiştirmek istediği şeyi kendi değiştiriyor ve submit ediyor
    def change_reservation(self, changeDto):
        user = session.get('username')
        new_to_start = changeDto["to_start"]
        new_to_end = changeDto["to_end"]
        new_day = change_date_format(changeDto["day"])
        new_room = changeDto["room"]
        event_id = changeDto["event_id"]

        tx_sql = read_sql_file('./sql/change_booking_tx.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(tx_sql, {
                'new_to_start': new_to_start,
                'new_to_end': new_to_end,
                'new_day': new_day,
                'new_room': new_room,
                'curr_user': user,
                'event_id': event_id
            })

            conn.commit()

            email_subject = "Event changed."
            email_content = " titled event has been changed."
            self.send_emails(email_content, email_subject, event_id)

            return "True"
        except psycopg2.Error as e:
            conn.rollback()
            return "False"
        finally:
            cursor.close()
            conn.close()

    def make_suggestion(self, reservationDto):   
        user = session.get('username')
        department = session.get('department')
        start_time = reservationDto['start_time'] + ":00"   
        end_time = reservationDto['end_time'] +":00"        
        day = reservationDto['day']
        room = reservationDto['room']

        tx_sql = read_sql_file('./sql/make_suggestion_tx.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(tx_sql, {
                'to_start': start_time,
                'to_end': end_time,
                'day': day,
                'room': room,
                'curr_user': user
            })

            cursor.execute("""SELECT * FROM rooms WHERE capacity >= 
                           (SELECT capacity FROM rooms WHERE room_id = %s)
                           AND department_id = %s
                           AND room_id <> %s""", (room, department, room))

            suggestions = cursor.fetchall()
            conn.commit()
            return suggestions
        except psycopg2.Error as e:
            conn.rollback()
            return "False"
        finally:
            cursor.close()
            conn.close()

    def change_recurring_reservation(self, changeDto): 
        user = session.get('username')
        new_to_start = changeDto["to_start"]
        new_to_end = changeDto["to_end"]
        new_start_day = change_date_format(changeDto["start_day"])
        new_end_day = change_date_format(changeDto["end_day"])
        new_room = changeDto["room"]
        event_id = changeDto["event_id"]
        old_interval = calculate_interval(event_id)   

        tx_sql = read_sql_file('./sql/change_recurring_booking_tx.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(tx_sql, {
                'new_to_start': new_to_start,
                'new_to_end': new_to_end,
                'new_start_day': new_start_day,
                'new_end_day': new_end_day,
                'new_room': new_room,
                'curr_user': user,
                'old_interval': old_interval,
                'event_id': event_id
            })

            conn.commit()

            email_subject = "Event changed."
            email_content = " titled event has been changed."
            self.send_emails(email_content, email_subject, event_id)

            return "True"
        except psycopg2.Error as e:
            conn.rollback()
            return "False"
        finally:
            cursor.close()
            conn.close()

    def change_event_details(self, eventDto):  
        title = eventDto["title"]
        description = eventDto["description"]
        event_id = eventDto["event_id"]
        username = session.get('username')

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""UPDATE events SET title = %s, description =%s 
                       WHERE event_id = %s
                       AND organizer = %s""", 
                       (title, description, event_id, username))
        
        conn.commit()
        conn.close()
        return 'True'

    # backend - frontend: possible room listesi
    def make_recurring_suggestion(self, reservationDto): 
        user = session.get('username')
        department = session.get('department')
        start_time = reservationDto['start_time'] + ":00"   
        end_time = reservationDto['end_time'] +":00"
        start_day = reservationDto['start_day']
        end_day = reservationDto['end_day']
        room = reservationDto['room']
        interval = reservationDto['interval']

        tx_sql = read_sql_file('./sql/make_recurring_suggestion_tx.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try :
            cursor.execute(tx_sql, {
                'to_start': start_time,
                'to_end': end_time,
                'start_day': start_day,
                'end_day': end_day,
                'room': room,
                'curr_user': user,
                'interval': interval
            })

            cursor.execute("""SELECT * FROM rooms WHERE capacity >= 
                           (SELECT capacity FROM rooms WHERE room_id = %s)
                           AND department_id = %s
                           AND room_id <> %s""", (room, department, room))
            
            suggestions = cursor.fetchall()
            conn.commit()
            return suggestions
        except psycopg2.Error as e:
            conn.rollback()
            return "False"
        finally:
            cursor.close()
            conn.close()

    def email_for_course(self, course_code):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT s.email FROM takes t, student s
                        WHERE t.student_id = s.student_id
                       AND t.course_code = %s """, (course_code,))
        
        emails = cursor.fetchall()
        emails = [item['email'] for item in emails]

        return emails

    def email_for_department(self, department_id):
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT email FROM instructor
                       WHERE department_id = %s """, (department_id,))
        
        instructor_emails = cursor.fetchall()
        instructor_emails = [item['email'] for item in instructor_emails]

        cursor.execute("""SELECT email FROM student
                       WHERE department_id = %s """, (department_id,))
        
        student_emails = cursor.fetchall()
        student_emails = [item['email'] for item in student_emails]

        emails = instructor_emails + student_emails

        return emails
    
    def send_emails(self, email_content, email_subject, event_id): 
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT title FROM events
                        WHERE event_id = %s """, (event_id, ))
        
        title = cursor.fetchone()["title"]
        cursor.execute("SELECT EXISTS (SELECT 1 FROM takes WHERE course_code = %s)", (title, ))
        course = cursor.fetchone()
        recipients = []

        if course:
            recipients = self.email_for_course(title)
        else:
            recipients = self.email_for_department(session.get('department'))

        #The mail addresses and password
        sender_address = 'aycaakyol3@gmail.com'
        sender_pass = "huzkdgfdckwnvqel"
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = "aycaakyol3@gmail.com"
        message['Bcc'] = ", ".join(recipients)
        message['Subject'] = email_subject
        message.attach(MIMEText(title + email_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, sender_address, text)
        session.quit() 

    # def get_reservation(self, booking_id):   # timetable üzerinden bakılırken - zaman kalırsa
    #     conn = get_db_connection()
    #     cursor = conn.cursor(cursor_factory=RealDictCursor)

    #     cursor.execute("""SELECT e.event_id , e.title , e.description, b.room_id, t.date, t.start_time, t.end_time 
    #                    FROM events e
    #                    INNER JOIN bookings b on b.event_id = e.event_id
    #                    INNER JOIN timeslots t on t.timeslot_id = b.timeslot_id
    #                    WHERE b.booking_id 0 %s""", (booking_id, ))
        
    #     booking = cursor.fetchone()
    #     return booking
    
    # frontend -> backend: department, day ama guest değilse departmentı sessiondan çek 
    # eğer tek gün ise start ve endi aynı gir
    def get_timetable(self, start, end, department):    # anasayfada göstermek için -- start end date olabilir
        if start is None or end is None:
            today = date.today()
            start = today #- timedelta(days=today.weekday())
            # end = start + timedelta(days=6) 
            start = start.strftime("%d-%m-%Y") 
            end = start
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT e.event_id , e.title , e.description, 
                       b.room_id, t.date, r.name AS room_name, 
                       to_char(t.start_time, 'HH24:MI') AS start_time, 
                       to_char(t.end_time, 'HH24:MI') AS end_time
                       FROM events e
                       INNER JOIN bookings b on b.event_id = e.event_id
                       INNER JOIN timeslots t on t.timeslot_id = b.timeslot_id
                       INNER JOIN rooms r on r.room_id = b.room_id
                       WHERE t.date BETWEEN to_date(%s, 'dd-mm-yyyy') AND to_date(%s, 'dd-mm-yyyy')
                       AND r.department_id = %s""", (start, end, department))  
        
        timetable = cursor.fetchall()
        
        if timetable:
            return timetable
        else:
            return "False"
    
    def get_all_my_reservations(self):
        user = session.get('username')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT e.event_id, e.title, e.description, e.organizer, 
                       r.room_id, r.name AS room_name, r.capacity, r.type,
                       string_agg(f.name, ', ') AS feature_name, t.date, 
                       to_char(t.start_time, 'HH24:MI') AS start_time, 
                       to_char(t.end_time, 'HH24:MI') AS end_time
                       FROM events e
                       INNER JOIN bookings b ON b.event_id = e.event_id
                       INNER JOIN timeslots t ON b.timeslot_id = t.timeslot_id
                       INNER JOIN rooms r ON r.room_id = b.room_id
                       INNER JOIN room_features rf ON r.room_id = rf.room_id
                       INNER JOIN features f ON f.feature_id = rf.feature_id
                       WHERE e.organizer = %s
                       AND f.is_accepted = true 
                       GROUP BY e.event_id, e.title, e.description, e.organizer, 
                       r.room_id, r.name, r.capacity, r.type, t.date, 
                       t.start_time, t.end_time""", (user, ))
        
        my_reservations = cursor.fetchall()

        if my_reservations:
            return my_reservations
        else:
            return "False"

    def get_my_reservations_for_day(self, day): 
        user = session.get('username')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if day is None:
            today = date.today()
            day = today.strftime("%d-%m-%Y")
        
        cursor.execute("""SELECT e.title, e.description, e.organizer, r.name AS room_name, r.capacity, r.type,
                       f.name AS feature_name, rf.is_working, t.date, to_char(t.start_time, 'HH24:MI') AS start_time, 
                       to_char(t.end_time, 'HH24:MI') AS end_time
                       FROM events e
                       INNER JOIN bookings b ON b.event_id = e.event_id
                       INNER JOIN timeslots t ON b.timeslot_id = t.timeslot_id
                       INNER JOIN rooms r ON r.room_id = b.room_id
                       INNER JOIN room_features rf ON r.room_id = rf.room_id
                       INNER JOIN features f ON f.feature_id = rf.feature_id
                       WHERE e.organizer = %s AND t.date = to_date(%s, 'dd-mm-yyyy')
                       AND f.is_accepted = true """, (user, day))
        
        my_reservations = cursor.fetchall()

        if my_reservations:
            return my_reservations
        else:
            return "False"
        
    def get_other_reservarions_for_day(self, day): 
        user = session.get('username')
        department  = session.get('department')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor) 

        if day is None:
            today = date.today()
            day = today.strftime("%d-%m-%Y") 

        cursor.execute("""SELECT e.title, e.description, e.organizer, r.name AS room_name, r.capacity, r.type,
                       f.name AS feature_name, rf.is_working, to_char(t.start_time, 'HH24:MI') AS start_time, 
                       to_char(t.end_time, 'HH24:MI') AS end_time
                       FROM events e
                       INNER JOIN bookings b ON b.event_id = e.event_id
                       INNER JOIN timeslots t ON b.timeslot_id = t.timeslot_id
                       INNER JOIN rooms r ON r.room_id = b.room_id
                       INNER JOIN room_features rf ON r.room_id = rf.room_id
                       INNER JOIN features f ON f.feature_id = rf.feature_id
                       WHERE e.organizer <> %s AND r.department_id = %s
                       AND t.date = to_date(%s, 'dd-mm-yyyy')
                       AND f.is_accepted = true """, (user, department, day))
        
        other_reservations = cursor.fetchall()

        if other_reservations:
            return other_reservations
        else:
            return "False"

    def export_timetable(self, start, end, format): 
        try:
            os.remove('./timetable.csv')
        except OSError:
            pass
            
        try:
            os.remove('./timetable.xlsx')
        except OSError:
            pass

        try:
            os.remove('./timetable.pdf')
        except OSError:
            pass

        department = session.get('department')
        if start is None or end is None:
            today = date.today()
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)

        start = datetime.strptime(start, '%Y-%m-%d').strftime("%d-%m-%Y")
        end = datetime.strptime(end, '%Y-%m-%d').strftime("%d-%m-%Y")

        timetable = self.get_timetable(start, end, department) 
        
        if timetable != "False":
            timetable = [dict(row) for row in timetable]
        else:
            timetable = []
        
        fieldnames = ['event_id', 'title', 'description', 'room_id', 'date', 'room_name', 'start_time', 'end_time']

        with open('timetable.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(timetable)

        if format == 'csv':
            return send_file('timetable.csv', as_attachment=True)
        elif format == 'excel':
            df = pd.DataFrame(timetable)
            df.to_excel("timetable.xlsx", index=False)
            return send_file('timetable.xlsx', as_attachment=True)
        else:  
            df = pd.DataFrame(timetable)

            html_content = df.to_html(index=False)
            pdfkit.from_string(html_content, "timetable.pdf")

            return send_file("timetable.pdf", as_attachment=True)