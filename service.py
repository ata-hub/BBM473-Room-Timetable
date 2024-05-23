from db import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify, session
from datetime import datetime, time
import pandas as pd
import csv
import  jpype     
import  asposecells 
from asposecells.api import Workbook
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MyException(Exception):
    pass

class UserService(): 
    # frontend -> backend: username, password 
    def login(self, userDto):
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
            raise MyException('This user does not exist or is not allowed to enter this website.')
        
    #TODO frontend -> backend: permission_request_id, acceptance TODO : sonra request tabeldan da sil
    # backend -> frontend: sonuç
    def give_permission(self, permissionDto):   # for admin  
        username = permissionDto['username']
        room_id = permissionDto['room']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        current_user_role = session.get('role')
        print(session.get)

        if current_user_role == 'admin':
            cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
            user_exists = cursor.fetchone()

            if user_exists is None:
                print("HELLO2")
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
                           )
                           """, 
                           (username, room_id, username, room_id))
            conn.commit()

            if cursor.rowcount != 1:
                raise MyException("Can't give permission for a room in another department other than the student's own department")

            conn.close()
            return 'Permission given.'
        
        conn.close()
        raise MyException('This user is not allowed to give permissions.')

    # frontend -> backend: username, room_id 
    # backend -> frontend: sonuç
    def request_permission(self, requestDto):   # for instructor
        username = requestDto['username']
        room_id = requestDto['room']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        current_user_department = session.get('department')
        print("dept: ", current_user_department)

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
            raise MyException("Can't request permission for a room in another department.")

        conn.close()
        return 'Request made.'

    def list_awating_permission_requests(self):    # for admin 
        department = session.get('department')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # filter permissons by admin's department
        cursor.execute('SELECT * FROM room_permission_requests rpr, rooms r WHERE rpr.room_id = r.room_id AND r.department_id = %s', (department, ))
        permissions = cursor.fetchall()
        return permissions

    def list_awating_feature_requests(self):   # for admin 
        department = session.get('department')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("DEPARTMENT: ", department)
        # filter permissons by admin's department
        cursor.execute("""SELECT fr.room_id, fr.feature_id, fr.description 
                       FROM feature_requests fr, rooms r 
                       WHERE fr.room_id = r.room_id AND r.department_id = %s""", (department, ))
        permissions = cursor.fetchall()
        return permissions

    #def get_user_rooms(self):   #TODO kullanıcının erişimi olan odalar

    def logout(self):
        session.clear()
        return 'Logged out.'

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql = file.read()
    return sql
    
class RoomService(): # TODO test all of this service
    # backend -> frontend: liste
    def list_features(self): # this is for listing all possible features for request
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT name FROM features")
        features = cursor.fetchall()
        return features  #TODO turn to list

    # frontend -> backend: description, feature_id, room_id
    # backend -> frontend: boolean?
    def request_feature(self, featureDto):    # for inst (in the future student too)
        description = featureDto["description"]
        feature_id = featureDto["feature_id"]
        room_id = featureDto["room_id"]

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""INSERT INTO feature_requests(description, feature_id, room_id) 
                       VALUES (%s, %s, %s)""", (description, feature_id, room_id))
        conn.commit()
        conn.close()
        return "Feature requested."
    
    # frontend -> backend: feature_id, acceptance TODO (ekle) - sonra request tabeldan da sil
    # backend -> frontend: boolean?
    def add_new_feature(self, feature):   # for admin
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("INSERT INTO features(name) VALUES(%s)", (feature,))
        conn.commit()
        conn.close()
        return "Added new feature."
        
    # frontend -> backend: 
    # backend -> frontend: boolean?
    def make_reservation(self, reservationDto):
        user = session.get('username')
        event_title = reservationDto['title']
        event_description = reservationDto['description']
        start_time = reservationDto['start_time'] + ":00"   #TODO bu time ve date kısmı frontendden nasıl geldiğine bağlı
        end_time = reservationDto['end_time'] +":00"        # date i mm-dd-yyyy girmek gerekiyor
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
            return jsonify({'status': 'success', 'message': 'Reservation made.'})
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
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
            return jsonify({'status': 'success', 'message': 'Recurring reservation made.'})
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            cursor.close()
            conn.close()

    # backend -> frontend: reservation details list
    def list_user_reservations(self):    # all the reservations the user has made
        user = session.get('username')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""SELECT e.event_id , e.title , e.description, b.room_id, t.date, t.start_time, t.end_time 
                       FROM events e
                       INNER JOIN bookings b on b.event_id = e.event_id
                       INNER JOIN timeslots t on t.timeslot_id = b.timeslot_id
                       WHERE e.organizer = %s""", (user,)) 
        
        reservations = cursor.fetchall()

        if reservations is None:
            return "This user doesn't made any reservations."
        
        for row in reservations:
            if 'start_time' in row:
                 row['start_time'] = row['start_time'].isoformat()
            if 'end_time' in row:
                 row['end_time'] = row['end_time'].isoformat()
        
        return reservations # TODO bunu biraz karışık döndürüyor frontendde düzelt - liste olarak döndür

    # frontend -> backend: event_id
    def cancel_reservation(self, event_id):   # TODO bu doğru çalışmıyor timeslots tabledan silmiyo
        user = session.get('username')
        tx_sql = read_sql_file('./sql/delete_event.sql')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            email_subject = "Event canceled."
            email_content = " titled event has been canceled"
            self.send_emails(email_content, email_subject, event_id)

            cursor.execute(tx_sql, {'event_id': event_id, 'curr_user': user})
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Reservation canceled.'})
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
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
        new_day = changeDto["day"]
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
            self.send_emails(email_content, email_subject)

            return jsonify({'status': 'success', 'message': 'Reservation changed.'})
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            cursor.close()
            conn.close()

    def make_suggestion(self, reservationDto):
        user = session.get('username')
        start_time = reservationDto['start_time'] + ":00"   
        end_time = reservationDto['end_time'] +":00"        
        day = reservationDto['day']
        room = reservationDto['room']

        tx_sql = read_sql_file('./sql/make_suggestion_for_room_tx.sql')
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

            suggestions = cursor.fetchall()
            conn.commit()
            return suggestions
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            cursor.close()
            conn.close()

    def change_recurring_reservation(self, changeDto):
        user = session.get('username')
        new_to_start = changeDto["to_start"]
        new_to_end = changeDto["to_end"]
        new_start_day = changeDto["start_day"]
        new_end_day = changeDto["end_day"]
        new_room = changeDto["room"]
        new_interval = changeDto["interval"]   # TODO bunu kaldır
        event_id = changeDto["event_id"]

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
                'new_interval': new_interval,
                'event_id': event_id
            })

            conn.commit()

            email_subject = "Event changed."
            email_content = " titled event has been changed."
            self.send_emails(email_content, email_subject)

            return jsonify({'status': 'success', 'message': 'Reservation changed.'})
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            cursor.close()
            conn.close()

    def change_event_details(self, eventDto):   # TODO   bunu diğer changelerle birleştir
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
        
        conn.close()
        return 'Event details changed.'

    # backend - frontend: possible room listesi
    def make_recurring_suggestion(self, reservationDto):
        user = session.get('username')
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
            
            suggestions = cursor.fetchall()
            # TODO check type suggestions
            conn.commit()
            return suggestions
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': str(e)})
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
        
        title = list(cursor.fetchall())[0]

        cursor.execute("SELECT EXISTS (SELECT 1 FROM takes WHERE course_code = %s)", (title, ))
        course = int(list(cursor.fetchone())[0])
        recipients = []

        if course:
            recipients = self.email_for_course(title)
        else:
            recipients = self.email_for_department(session.get('department'))

        #The mail addresses and password
        sender_address = 'aycaakyol3@gmail.com'
        sender_pass = ""
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

    def get_reservation(self, booking_id):   # timetable üzerinden bakılırken - zaman kalırsa
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT e.event_id , e.title , e.description, b.room_id, t.start_time, t.end_time 
                       FROM events e
                       INNER JOIN bookings b on b.event_id = e.event_id
                       INNER JOIN timeslots t on t.timeslot_id = b.timeslot_id
                       WHERE b.booking_id 0 %s""", (booking_id, ))
        
        booking = cursor.fetchone()
        return booking
    
    # frontend -> backend: department, day ama guest değilse departmentı sessiondan çek
    #TODO departmana ol 
    def get_timetable(self, timetableDto):    # anasayfada göstermek için -- start end date olabilir
        start = timetableDto['start']         # TODO bunun için logine gerek olmamalı
        end = timetableDto['end']             

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""SELECT e.event_id , e.title , e.description, b.room_id, t.date, t.start_time, t.end_time 
                       FROM events e
                       INNER JOIN bookings b on b.event_id = e.event_id
                       INNER JOIN timeslots t on t.timeslot_id = b.timeslot_id
                       WHERE t.date BETWEEN %s::date AND %s::date""", (start, end))  # değiştir
        
        timetable = cursor.fetchall()
        return timetable
    
    # def get_user_timetable(self): #TODO benim rezervasyonlar 
    # def get_other_timetable(self):

    def export_timetable(self, timetableDto): # TODO test et
        start = timetableDto['start']  # gün 
        end = timetableDto['end']
        format = timetableDto['format']
        time = dict((key,value) for key, value in timetableDto.iteritems() if key in ['start', 'end'])

        timetable = jsonify(self.get_timetable(time))
        data_file = open("timetable.csv", "w", newline='')
        csv_writer = csv.writer(data_file)

        count = 0
        for data in timetable:
            if count == 0:
                header = data.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(data.values())
        
        data_file.close()

        if format == 'csv':
            return data_file
        elif format == 'excel':
            excel_file = pd.read_csv(data_file)
            excel_file.to_excel("timetable.xlsx", index=False, header=True)
            return excel_file
        else:
            excel_file = pd.read_csv(data_file)
            excel_file.to_excel("timetable.xlsx", index=False, header=True)

            jpype.startJVM() 
            workbook = Workbook("timetable.xlsx")
            workbook.save("timetable.pdf")
            jpype.shutdownJVM()
	
            with open("./timetable.pdf", 'r') as file:
                timetable = file.read()
            return timetable