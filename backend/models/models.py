from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin,RoleMixin
from sqlalchemy import LargeBinary
from datetime import datetime,timedelta
IST = timedelta(hours=5, minutes=30)

db = SQLAlchemy()

class TimeStampMixin:
    created_at = db.Column(db.DateTime, default=lambda :datetime.utcnow() + IST)
    updated_at = db.Column(db.DateTime, default=lambda : datetime.utcnow() + IST, onupdate=lambda : datetime.utcnow() + IST)
    deleted_at = db.Column(db.DateTime,nullable=True)
    deleted_by = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)

    @classmethod
    def active(cls):
        return cls.query.filter(cls.deleted_at == None)


# Association table for many-to-many relationship between User and Role
class RolesUsers(db.Model,TimeStampMixin):
    id = db.Column(db.Integer(),primary_key=True)
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(),db.ForeignKey('role.id'))

class TeachersSubjects(db.Model, TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'),nullable = False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'),nullable = False)

class Role(db.Model,RoleMixin,TimeStampMixin):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50),unique = True)
    description = db.Column(db.String(255))

class User(db.Model,TimeStampMixin,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    active = db.Column(db.Boolean,default = True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    last_login_at = db.Column(db.DateTime)
    
    student = db.relationship('Student', foreign_keys='Student.user_id', backref='user', uselist=False)
    parent = db.relationship('Parent', foreign_keys='Parent.user_id', backref='user', uselist=False)
    teacher = db.relationship('Teacher', foreign_keys='Teacher.user_id', backref='user', uselist=False)

    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id',backref='user')
    roles = db.relationship(
        'Role',
        secondary=RolesUsers.__table__,
        backref=db.backref('users', lazy='dynamic'),
        foreign_keys=[RolesUsers.user_id, RolesUsers.role_id],
        primaryjoin=id == RolesUsers.user_id,
        secondaryjoin=Role.id == RolesUsers.role_id
    )



class Class(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    students = db.relationship('Student', backref='class_')
    timetable_entries = db.relationship('Timetable', backref='class_')

    __table_args__ = (
        db.UniqueConstraint('name', 'section', 'session_id', name='uq_class_section_session'),
    )


class Subject(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    
    timetable_entries = db.relationship('Timetable', backref='subject')
    grades = db.relationship('Grade', backref='subject')


class Session(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Example relationship: if classes are tied to a session
    classes = db.relationship('Class', backref='session')

class Student(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    parent_id = db.Column(db.Integer,db.ForeignKey('parent.id'),nullable=True)
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
    religion = db.Column(db.String(50))
    admission_date = db.Column(db.DateTime)
    roll_number = db.Column(db.String(20), unique=True)
    aadhaar_number = db.Column(db.String(12), unique=True)
    apaar_id = db.Column(db.String(20), unique=True)  # Unique ID for integration with Apaar


    attendances = db.relationship('Attendance', backref='student')
    grades = db.relationship('Grade', backref='student')
    fees = db.relationship('Fee', backref='student')
    face_encodings = db.relationship('FaceEncoding', backref='student')

    __table_args__=(
        db.UniqueConstraint('roll_number','class_id', name ='uq_rollno_class'),
    )

class Parent(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    aadhar_number = db.Column(db.String(12), unique=True)
    relationship = db.Column(db.String(50),nullable=False)  # e.g., Father, Mother, Guardian

    students = db.relationship('Student',backref='parent')  #one to many relationship


class Teacher(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    subjects = db.relationship('Subject', secondary='teachers_subjects', backref=db.backref('teachers',lazy='dynamic'))
    
    timetable_entries = db.relationship('Timetable', backref='teacher')
    grades = db.relationship('Grade', backref='teacher')


class Timetable(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    day_of_week = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)


class Attendance(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Grade(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    term = db.Column(db.String(50))
    score = db.Column(db.Numeric(5, 2))
    grade = db.Column(db.String(5))


class Fee(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount_due = db.Column(db.Numeric(10, 2))
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    due_date = db.Column(db.Date)
    payment_status = db.Column(db.Enum('Paid', 'Pending', 'Overdue'), default='Pending')

    payments = db.relationship('Payment', backref='fee')


class Payment(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    fee_id = db.Column(db.Integer, db.ForeignKey('fee.id'), nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    amount_paid = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Enum('Successful', 'Failed', 'Pending'))


class Message(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.Enum('Attendance', 'Fee', 'Exam', 'Announcement'))
    message = db.Column(db.Text)
    status = db.Column(db.Enum('Read', 'Unread'), default='Unread')
    delivery_method = db.Column(db.Enum('Email', 'Push', 'SMS'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FaceEncoding(db.Model,TimeStampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    encoding = db.Column(db.Text)  # Can store base64 or JSON of numpy array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    