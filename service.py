from db import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify, session

conn = get_db_connection()

class MyException(Exception):
    pass

class UserService(): 
    def login(self, userDto):
        username = userDto['username']
        password = userDto['password']
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()

        if user_data:
            conn.close()
            del user_data['password']
            return user_data
        else:
            raise MyException('This user does not exist or is not allowed to enter this website.')
        
    def give_permission(self, permissionDto):   # for admin  #TODO test this
        username = permissionDto['username']
        room_id = permissionDto['room']
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        current_user_role = session.get('role')

        if current_user_role == 'admin':
            cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
            user_exists = cursor.fetchone()

            if user_exists is None:
                cursor.execute('SELECT * FROM school_students WHERE student_id = %s', (username))
                student = cursor.fetchone()
                password = student['country_id']
                cursor.execute("INSERT INTO users(username, password, role, department_id) VALUES (%s, %s, 'student', %s)", (username, password, student['department_id']))

            cursor.execute("INSERT INTO user_permissions (username, room_id) SELECT %s, %s WHERE EXISTS (SELECT * FROM users, rooms WHERE users.room_id = rooms.room_id AND users.department_id = rooms.department_id)", (username, room_id))
            permission = cursor.fetchone()
            return permission
        
        raise MyException('This user is not allowed to give permissions.')


    # def request_permission(self, username, room):   # for instructor

    def list_awating_permission_requests(self):    # for admin
        department = session.get('department')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # filter permissons by admin's department
        cursor.execute('SELECT * FROM room_permission_requests rpr, rooms r WHERE rpr.room_id = r.room_id AND r.department_id = %s', (department))
        permissions = cursor.fetchall()
        return permissions

    # def list_awating_feature_requests(self):   # for admin

    
# class RoomService():
#     def request_feature(self):    # for inst (in the future student too)
    
#     def make_reservation(self):

#     def make_recurring_reservation(self):

#     def cancel_reservation(self):

#     def change_reservation_date(self):

#     def make_suggestion(self):

#     def send_emails(self):

#     def export_timetable(self, csv, excel, pdf):