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

    def list_awating_feature_requests(self):   # for admin #TODO RoomService'de request_feature yaptıktan sonra bunu bi daha test et
        department = session.get('department')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # filter permissons by admin's department
        cursor.execute('SELECT * FROM feature_requests fr, rooms r WHERE fr.room_id = r.room_id AND r.department_id = %s', (department, ))
        permissions = cursor.fetchall()
        return permissions

    def logout(self):
        session.clear()
        return 'Logged out.'

    
# class RoomService():
#     def request_feature(self):    # for inst (in the future student too)
    
#     def make_reservation(self):

#     def make_recurring_reservation(self):

#     def cancel_reservation(self):

#     def change_reservation_date(self):

#     def make_suggestion(self):

#     def send_emails(self):

#     def export_timetable(self, csv, excel, pdf):