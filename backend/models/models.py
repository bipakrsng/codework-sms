from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin,RoleMixin
from sqlalchemy import LargeBinary
from datetime import datetime


db = SQLAlchemy()

# Association table for many-to-many relationship between User and Role
class RolesUsers(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(),db.ForeignKey('role.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    email = db.Column(db.String(100),unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean,default = True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    last_login_at = db.Column(db.DateTime)
    token= db.Column(db.String(255),unique= True,nullable=True)

    student = db.relationship('Student', backref='user', uselist=False)
    teacher = db.relationship('Teacher', backref='user', uselist=False)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')
    notifications = db.relationship('Notification', backref='user')
    roles = db.relationship('Role',secondary='roles_users',backref= db.backref('users',lazy='dynamic'))

class Role(db.Model,RoleMixin):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50),unique = True)
    description = db.Column(db.String(255))

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    students = db.relationship('Student', backref='class_')
    timetable_entries = db.relationship('Timetable', backref='class_')


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    timetable_entries = db.relationship('Timetable', backref='subject')
    grades = db.relationship('Grade', backref='subject')

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Example relationship: if classes are tied to a session
    classes = db.relationship('Class', backref='session')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.DateTime)
    gender = db.Column(db.Enum('male', 'female', 'other'))
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    guardian_contact = db.Column(db.String(50))


    attendances = db.relationship('Attendance', backref='student')
    grades = db.relationship('Grade', backref='student')
    fees = db.relationship('Fee', backref='student')
    face_encodings = db.relationship('FaceEncoding', backref='student')


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    timetable_entries = db.relationship('Timetable', backref='teacher')
    grades = db.relationship('Grade', backref='teacher')


class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day_of_week = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    term = db.Column(db.String(50))
    score = db.Column(db.Numeric(5, 2))
    grade = db.Column(db.String(5))


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount_due = db.Column(db.Numeric(10, 2))
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    due_date = db.Column(db.Date)
    payment_status = db.Column(db.Enum('Paid', 'Pending', 'Overdue'), default='Pending')

    payments = db.relationship('Payment', backref='fee')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fee_id = db.Column(db.Integer, db.ForeignKey('fee.id'), nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    amount_paid = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Enum('Successful', 'Failed', 'Pending'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.Enum('Attendance', 'Fee', 'Exam', 'Announcement'))
    message = db.Column(db.Text)
    status = db.Column(db.Enum('Read', 'Unread'), default='Unread')
    delivery_method = db.Column(db.Enum('Email', 'Push', 'SMS'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FaceEncoding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    encoding = db.Column(db.Text)  # Can store base64 or JSON of numpy array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    