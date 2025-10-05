from flask_restful import Resource, Api,reqparse,marshal_with,fields,marshal
from backend.sockets.socket import socketio
from backend.models.models import *
from flask import request, jsonify,make_response
from flask_socketio import emit
from datetime import datetime,timedelta,date
from werkzeug.security import check_password_hash,generate_password_hash
import jwt
from functools import wraps
from config import DevelopmentConfig
import re
import uuid
from collections import defaultdict
from sqlalchemy import and_,or_,not_,func,desc,asc,case
import numpy as np
import base64,io
import cv2
from config import DevelopmentConfig
from backend.embeddings import get_embedding_from_base64
import razorpay,hmac,hashlib
from decimal import Decimal

import dlib
from PIL import Image
import face_recognition
import pickle
import json
from sqlalchemy.exc import SQLAlchemyError



api = Api(prefix='/api')

def generate_username(first_name,last_name,role,user_id):
    # Generate a username by combining first and last name
    username = f"{first_name.lower()}.{last_name.lower()}{user_id}"
    
    if role == 'student':
        # For students, append a random number to ensure uniqueness
        username = f"{username}{'stu'}"
    elif role == 'teacher':
        username = f"{username}{'tea'}"

    # Ensure the username is unique by appending user_id if necessary
    username = f"{username}{user_id}"

    return username


def create_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'active':user.active,
        'role':[role.name for role in user.roles],
        'exp': datetime.utcnow() + timedelta(minutes=6000)  # Token valid for 1 day #token shpould update if user is active and if ideal then expires
    }
    token = jwt.encode(payload, DevelopmentConfig.SECRET_KEY, algorithm='HS256')
    return token

def token_required(roles=[]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith("Bearer "):
                return {"message": "Token is missing or invalid"}, 401
            token = auth_header.split(" ")[1]
            if not token:
                return {"message": "Token is missing!"}, 401
            try:
                payload = jwt.decode(token, DevelopmentConfig.SECRET_KEY, algorithms=['HS256'])
                # if roles:
                #     print(roles)
                
                # if payload.get('role'):
                #     print(payload.get('role'))



                if roles and not any(role in payload.get('role',[]) for role in roles):
                    return {"message": "You do not have permission to access this resource based on roles"}, 403
                request.user = payload
            except jwt.ExpiredSignatureError:
                return {"message": "Token has expired!"}, 401
            except jwt.InvalidTokenError:
                return {"message": "Invalid token!"}, 401
            return f(*args, **kwargs)
        return wrapper
    return decorator



class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email',type=str,required= True,help='Email is required') #email syntax verified
        parser.add_argument('password',type=str,required=True,help='Password is required')

        args = parser.parse_args() # now args is dictionary having email and password as keys
        email = args['email']
        password = args['password']

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return {'error': 'Invalid email format'}, 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return {'error': 'User not found'}, 404
        
        if user and not user.active:
            return {'error':'User has been deactivated'},400

        if check_password_hash(user.password,password):

            utcnow = datetime.utcnow()
            time_diff = timedelta(hours=5,minutes=30)  # Adjust for IST (UTC+5:30)
            istnow = utcnow + time_diff
            user.last_login_at = istnow
            token = create_token(user)
            
            db.session.commit()
            return {'message': 'Login successful','token':token}
            
        else:
            return {'error': 'Invalid password'}, 401

class GetUserById(Resource):
    def get(self,user_id):

        user = User.query.get(user_id)
        
        if not user.active:
            return {"error":"user is deactivated"},400
        else:
            return {'active':True},200



# <----------------------- class details CRUD OPeration ------------------>

#formatting class fields for response
class_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'section':fields.String,
    'created_at':fields.DateTime,
    'updated_at':fields.DateTime,
    'deleted_at':fields.DateTime,
    
    'session': fields.Nested({
        'id':fields.Integer,
        'name':fields.String,
        'is_active':fields.Boolean,

    }),  # Assuming session_id is an integer

    'user':fields.Nested({
        'id':fields.Integer,
        'phone_number':fields.String

    }),
}
class ClassGetCreate(Resource):
    
   
    
    @token_required(roles=['admin'])
    def get(self):
    
        # classes = Class.query.join(
        #     Session, Class.session_id == Session.id).filter(Session.deleted_at==None,Class.deleted_at==None,Session.is_active==True).all()
        
        classes = Class.query.all()
        
        return marshal(classes,class_fields),200
   
    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name',type=str,required=True,help='Class name is required') #trimming and lowercase conversion before storing
        parser.add_argument('section',type=str)
        #displayname,description
        #2A displayname 2-A
        parser.add_argument('session_id', type=int, required=True, help='Session ID is required')

        args = parser.parse_args()

        # Validate session_id 
        if not Session.query.get(args['session_id']):
            return {'message': 'Session not found'}, 404

        
        new_class = Class(name=args['name'].title(),section=args.get('section','A').upper(),session_id = args['session_id']) #providing defaukt section 'A' if not provided
        db.session.add(new_class)
        db.session.commit()
        return {'message': 'Class created successfully'}, 201

class ClassUpdateDelete(Resource):
    #SQL Injection and XSS attacks are prevented by using ORM and input validation
    
    @token_required(roles=['admin'])
    def get(self,class_id):
        class_info = Class.query.get(class_id)
        if not class_info:
            return {"mesage":"class not found"},404
        
        if class_info.deleted_at is not None:
            return {"message":"Class is deleted"},404
        return marshal(class_info,class_fields),200
    

    @token_required(roles=['admin'])
    def put(self,class_id):
        
        parser = reqparse.RequestParser()
        parser.add_argument('name',type=str,location='json')
        parser.add_argument('section',type=str,location='json')
        args = parser.parse_args()
        class_info = Class.query.get(class_id)
        if not class_info:
            return {"message": "Class not found"}, 404
        if args['name']:
            class_info.name = args['name'].title()
            
        if args['section']:
            class_info.section = args['section'].upper()
            
        db.session.commit()
        return {'message': 'Class updated successfully'}, 200
    

    @token_required(roles=['admin'])   
    def delete(self,class_id):
        class_info = Class.query.get(class_id)
        user_id = request.user['user_id'] #getting user id from token
        #user = User.query(user_id)
        if not class_info:
            return {"message": "Class not found"}, 404
        if class_info.deleted_at is not None:
            return {"message": "Class already deleted"}, 400
        class_info.deleted_at = datetime.utcnow() + IST
        class_info.deleted_by = user_id
        db.session.commit()
        
        return {'message': 'Class deleted successfully'}, 200
    
    @token_required(roles=['admin'])
    def patch(self,class_id):
        class_info = Class.query.get(class_id)
        user_id = request.user['user_id']

        if not class_info:
            return {'message':"class not found"}
        
        if class_info.deleted_at is None:
            return {'message':'class is already active'}
        
        class_info.deleted_at = None
        class_info.deleted_by = None
        db.session.commit()
        return {'message':'Class restored successfully'},200


# <----------------------- subject details CRUD OPeration ------------------>

subject_fields = {
    'id': fields.Integer,
    'name': fields.String, #subjectcode createdat updatedat
    'code': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime

    

}
class SubjectGetCreate(Resource):
    @marshal_with(subject_fields)
    @token_required(roles=['admin'])
    def get(Self):
        subjects = Subject.active().all()
        return subjects, 200
    
    
    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Subject name is required')
        parser.add_argument('code', type=str, required=True, help='Subject code is required')
        args = parser.parse_args()
        new_subject = Subject(name=args['name'].title(),
        code=args['code'].strip().upper(), #code is stored in uppercase
                              )
        db.session.add(new_subject) # Add the new subject to the session
        db.session.commit()
        return {'message': 'Subject created successfully'}, 201

class SubjectUpdateDelete(Resource):
    
    @token_required(roles=['admin'])
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404
        if subject.deleted_at is not None:
            return {"message": "Subject already deleted"}, 400
        return marshal(subject,subject_fields), 200
    
    @token_required(roles=['admin'])
    def put(self, subject_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        parser.add_argument('code', type=str, location='json')
        args = parser.parse_args()
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404
        if args['name']:
            subject.name = args['name'].title()
        if args['code']:
            subject.code = args['code'].strip().upper()
        db.session.commit()
        return {'message': 'Subject updated successfully'}, 200

    @token_required(roles=['admin'])
    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        user_id = request.user['user_id']
        if not subject:
            return {"message": "Subject not found"}, 404
        if subject.deleted_at is not None:
            return {"message": "Subject already deleted"}, 400
        
        subject.deleted_at = datetime.utcnow() + IST
        subject.deleted_by = user_id
        db.session.commit()
        return {'message': 'Subject deleted successfully'}, 200
 

# <----------------------- session details CRUD OPeration ------------------>

session_fields={
    'id': fields.Integer,
    'name': fields.String,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'is_active': fields.Boolean,
    
}
class SessionGetCreate(Resource):
    @marshal_with(session_fields)
    @token_required(roles=['admin'])
    def get(self):
        sessions = Session.query.all()
        return sessions, 200
    
    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()
        # parser.add_argument('name', type=str, required=True, help='Session name is required')
        parser.add_argument('start_date', type=str, required=True, help='Start date is required')
        parser.add_argument('end_date', type=str, required=True, help='End date is required')
        # parser.add_argument('is_active', type=bool, default=True, help='Is active status')

        args = parser.parse_args()
        try:
            start_date = datetime.strptime(args['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(args['end_date'], '%Y-%m-%d').date()  
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        
        session_name = f"{start_date.year}-{end_date.year}"
        session = Session(name=session_name, start_date=start_date, end_date=end_date, is_active=True)
        db.session.add(session)
        db.session.commit()
        return {"message": "Session created successfully"}, 201
session_fields={
    'id': fields.Integer,
    'name': fields.String,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'is_active': fields.Boolean,
    
}  
class SessionUpdateDelete(Resource):
    @marshal_with(session_fields)
    @token_required(roles=['admin'])
    def get(self, session_id):
        session = Session.query.get(session_id)
        if not session:
            return {"message": "Session not found"}, 404
        if session.deleted_at is not None:
            return {"message": "Session is already deleted"}, 404
        return session, 200
    
    @token_required( roles=['admin'])
    def put(self, session_id):
        parser = reqparse.RequestParser() 
        
        parser.add_argument('start_date', type=str, location='json')
        parser.add_argument('end_date', type=str, location='json')
        parser.add_argument('is_active', type=str, location='json')
        args = parser.parse_args()
        print(args)
        session = Session.query.get(session_id)
        
        if not session:
            return {"message": "Session not found"}, 404
        
        start_date = None
        end_date = None
        print(f"start date is {args['start_date']}")

        if args['start_date'] not in [None,""]:
            try:
                print("this start")
                start_date = datetime.strptime(args['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid start date format. Use YYYY-MM-DD.'}, 400

        if args['end_date'] not in [None,""]:
            try:
                print("this end")
                end_date = datetime.strptime(args['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid end date format. Use YYYY-MM-DD.'}, 400

        
        

        if start_date and end_date:
            session_name = f"{start_date.year}-{end_date.year}"
            session.name = session_name

        if args['start_date']:
            session.start_date = start_date
        
        if args['end_date']:
            session.end_date = end_date

        if args['is_active']:
            if args['is_active'] == 'True':
                session.is_active = True
            else:
                session.is_active = False
        
        db.session.commit()
        return {'message': 'Session updated successfully'}, 200
    
    @token_required(roles=['admin'])
    def delete(self, session_id):
        c_session = Session.query.get(session_id)
        user_id = request.user['user_id']
        print(user_id)
        print(session_id)
        if not c_session:
            return {"message": "Session not found"}, 404
        if c_session.deleted_at is not None:
            return {"message": "Session is already deleted"}, 404
        print(c_session.deleted_at)
        c_session.deleted_at = datetime.utcnow() + IST
        print(IST)
        c_session.deleted_by = user_id

        db.session.commit()
        
        return {"message": "Session deleted successfully"}, 200


# <----------------------- student details CRUD OPeration ------------------>
    
student_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'parent_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'date_of_birth': fields.DateTime,
    'gender': fields.String,
    'address_line1': fields.String,
    'address_line2': fields.String,
    'city': fields.String,
    'state': fields.String,
    'country': fields.String,
    'postal_code': fields.String,
    'class_id': fields.Integer,
    'aadhaar_number': fields.String,
    'religion': fields.String,
    'admission_date': fields.DateTime,
    'roll_number': fields.String,

    'apaar_id': fields.String,
    'guardian_contact': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'deleted_at':fields.DateTime,
    
    # nested fields
    'parent': fields.Nested({
        'id': fields.Integer,
        'user_id': fields.Integer,
        'first_name': fields.String,
        'last_name': fields.String,
        'phone': fields.String,
        'email': fields.String,
        'aadhaar_number': fields.String,
        'relationship': fields.String,
        
        'user': fields.Nested({
            'id': fields.Integer,
            'username': fields.String,
            'email': fields.String,
            'phone_number': fields.String,
            'last_login_at': fields.DateTime
        })
    }),

    'user': fields.Nested({
        'id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'phone_number': fields.String,
        'last_login_at': fields.DateTime
    })
}

class StudentGetCreate(Resource):
    @marshal_with(student_fields)
    @token_required(roles=['admin'])
    def get(self):
        students = Student.query.all()
        if not students:
            return {"message":"student not found"},404

        return students, 200
    
    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()

        # --- User Fields ---
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        parser.add_argument('phone_number',type=str,required =True,help='Phone number is required')

        # --- Student Fields ---
        parser.add_argument('first_name', type=str, required=True, help='First name is required')
        parser.add_argument('last_name', type=str, required=True, help='Last name is required')
        parser.add_argument('date_of_birth', type=str, required=True, help='Date of birth is required')
        parser.add_argument('gender', type=str, required=True, help='Gender is required')
        parser.add_argument('address_line1', type=str, required=True, help='Address is required')
        parser.add_argument('address_line2', type=str)
        parser.add_argument('city', type=str, required=True, help='City is required')
        parser.add_argument('state', type=str, required=True, help='State is required')
        parser.add_argument('postal_code', type=str, required=True, help='Postal code is required')
        parser.add_argument('country', type=str, required=True, help='Country is required')
        parser.add_argument('class_id', type=int, required=True, help='Class ID is required')
        parser.add_argument('religion',type=str,required=True,help = 'Religion is required')
        parser.add_argument('admission_date',type=str,required=True,help="Admission Date is required")
        parser.add_argument('roll_number',type=str,required=True,help='Roll no is not provided')
        parser.add_argument('aadhaar_number', type=str, required=True, help='Aadhar number is required')
        parser.add_argument('apaar_id',type=str,required= True,help='Provide apaar id')

        # --- Guardian/Parent Fields ---
        parser.add_argument('guardian_first_name', type=str, required=True, help='Guardian first name is required')
        parser.add_argument('guardian_last_name', type=str, required=True, help='Guardian last name is required')
        parser.add_argument('guardian_email', type=str, required=True, help='Guardian email is required')
        parser.add_argument('guardian_phone', type=str, required=True, help='Guardian phone is required')
        parser.add_argument('relationship', type=str, required=True, help='Relationship is required')
        parser.add_argument('guardian_aadhaar_number',type= str,required=True,help='Guardian aadhar number is required')

        args = parser.parse_args()
        print(args)
        # --- Validate date format ---
        try:
            date_of_birth = datetime.strptime(args['date_of_birth'], '%Y-%m-%d').date()
            admission_date = datetime.strptime(args['admission_date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        print("date parsed")
        # --- Validate class ---
        class_info = Class.query.get(args['class_id'])
        if not class_info:
            return {'message': 'Class not found'}, 404

        try:

            new_student = Student(
                first_name=args['first_name'].strip().title(),
                last_name=args['last_name'].strip().title(),
                date_of_birth=date_of_birth,
                gender=args['gender'].strip().lower(),
                address_line1=args['address_line1'].strip().title(),
                address_line2=args.get('address_line2', '').strip().title(),
                city=args['city'].strip().title(),
                state=args['state'].strip().title(),
                postal_code=args['postal_code'].strip(),
                country=args['country'].strip().title(),
                class_id=args['class_id'],
                religion =args['religion'],
                admission_date=admission_date,
                roll_number=args['roll_number'].strip(),
                
                aadhaar_number=args['aadhaar_number'].strip(),
                apaar_id=args['apaar_id'].strip()

            )
            # print("new student created")
            db.session.add(new_student)
            # print("new student added",new_student)
            db.session.flush()  # get student.id
            # print("new student id is added and flushed",new_student.id)
            username = generate_username(
                new_student.first_name,
                new_student.last_name,
                'Student',
                new_student.id
            )
            # print("username generated",username)
            new_user = User(
                username=username,
                email=args['email'].strip(),
                password=generate_password_hash('student'),
                fs_uniquifier=str(uuid.uuid4()),
                phone_number = args['phone_number']
            )

            role = Role.query.filter_by(name='student').first()

            new_user.roles.append(role)

            db.session.add(new_user)
            db.session.flush()
            
            new_student.user_id = new_user.id

            # print("new student created with id",new_student.id)

            parent = Parent.query.filter_by(aadhaar_number=args['guardian_aadhaar_number'].strip()).first()
            if parent:
                new_student.parent_id = parent.id
                print("new student parent id is",new_student.parent_id)
                
            
            else:
                    parent = Parent(
                    first_name=args['guardian_first_name'].strip().title(),
                    last_name=args['guardian_last_name'].strip().title(),
                    email=args['guardian_email'].strip(),
                    phone=args['guardian_phone'].strip(),
                    relationship=args['relationship'].strip().title(),
                    aadhaar_number=args['guardian_aadhaar_number'].strip()
                    )
                    db.session.add(parent)
                    db.session.flush()

                    new_student.parent_id = parent.id

                    username = generate_username(parent.first_name,parent.last_name,'Parent',parent.id)

            
            
                    new_parent_user = User         (username=username,
                                   email=args['guardian_email'].strip(),
                                   password=generate_password_hash('parent'),
                                   fs_uniquifier=str(uuid.uuid4()),
                                   phone_number=args['guardian_phone'].strip()
                                   )
                    role = Role.query.filter_by(name='parent').first()
                    if role:
                        new_parent_user.roles.append(role)
            
        

                    db.session.add(new_parent_user)
                    db.session.flush()  # get new_user.id

                    parent.user_id = new_parent_user.id

            db.session.commit()

            return {"message": "Student and parent registered successfully", "student_id": new_student.id}, 201

        except Exception as e:
            import traceback
            db.session.rollback()
            print("Error occurred:", str(e))
            print(traceback.format_exc())
            return {"error": str(e)}, 500

class StudentUpdateDelete(Resource):
    
    @token_required( roles=['admin'])
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Student not found"}, 404
        if student.deleted_at is not None:
            return {"message": "Student is deleted"}, 404
        return marshal(student,student_fields), 200
    
    @token_required( roles=['admin'])
    def put(self, student_id):

        parser = reqparse.RequestParser()
        # --- User Fields ---
       
        
        
        parser.add_argument('phone_number',type=str,required =True,help='Phone number is required')

        # --- Student Fields ---
        parser.add_argument('first_name', type=str, required=True, help='First name is required')
        parser.add_argument('last_name', type=str, required=True, help='Last name is required')
        parser.add_argument('date_of_birth', type=str, required=True, help='Date of birth is required')
        parser.add_argument('gender', type=str, required=True, help='Gender is required')
        parser.add_argument('address_line1', type=str, required=True, help='Address is required')
        parser.add_argument('address_line2', type=str)
        parser.add_argument('city', type=str, required=True, help='City is required')
        parser.add_argument('state', type=str, required=True, help='State is required')
        parser.add_argument('postal_code', type=str, required=True, help='Postal code is required')
        parser.add_argument('country', type=str, required=True, help='Country is required')
        parser.add_argument('class_id', type=int, required=True, help='Class ID is required')
        parser.add_argument('religion',type=str,required=True,help = 'Religion is required')
        parser.add_argument('admission_date',type=str,required=True,help="Admission Date is required")
        parser.add_argument('roll_number',type=str,required=True,help='Roll no is not provided')
        parser.add_argument('aadhaar_number', type=str, required=True, help='Aadhar number is required')
        parser.add_argument('apaar_id',type=str,required= True,help='Provide apaar id')

        # --- Guardian/Parent Fields ---
        parser.add_argument('guardian_first_name', type=str, required=True, help='Guardian first name is required')
        parser.add_argument('guardian_last_name', type=str, required=True, help='Guardian last name is required')
        parser.add_argument('guardian_email', type=str, required=True, help='Guardian email is required')
        parser.add_argument('guardian_phone', type=str, required=True, help='Guardian phone is required')
        parser.add_argument('relationship', type=str, required=True, help='Relationship is required')
        parser.add_argument('guardian_aadhar_number',type= str,required=True,help='Guardian aadhar number is required')

        args = parser.parse_args()
        print(args)
        student = Student.query.get(student_id)
        

        if not student:
            return {"message": "Student not found"}, 404
        # if args['user_id']:
        #     user = User.query.get(args['user_id'])
        #     if not user:
        #         return {'message': 'User not found'}, 404
        #     student.user_id = args['user_id']
        if args['first_name']:
            student.first_name = args['first_name'].strip().title()
        if args['last_name']:
            student.last_name = args['last_name'].strip().title()
        if args['date_of_birth']:
            try:
                student.date_of_birth = datetime.strptime(args['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        if args['gender']:
            print("updating gender")
            student.gender = args['gender'].strip().title()
        if args['address_line1']:
            student.address_line1 = args['address_line1'].strip().title()
        if args['address_line2']:
            student.address_line2 = args['address_line2'].strip().title()
        if args['city']:
            student.city = args['city'].strip().title()
        if args['state']:
            student.state = args['state'].strip().title()
        if args['postal_code']:
            student.postal_code = args['postal_code'].strip()
        if args['country']:
            student.country = args['country'].strip().title()
        if args['class_id']:
            class_obj = Class.query.get(args['class_id'])
            if not class_obj:
                return {'message': 'Class not found'}, 404
            student.class_id = args['class_id']
        if args['religion']:
            student.religion = args['religion'].strip().title()
        if args['admission_date']:
            try:
                student.admission_date = datetime.strptime(args['admission_date'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid admission date format. Use YYYY-MM-DD.'}, 400
        if args['roll_number']:
            student.roll_number = args['roll_number'].strip()
        if args['aadhaar_number']:
            student.aadhaar_number = args['aadhaar_number'].strip()
        if args['apaar_id']:
            student.apaar_id = args['apaar_id'].strip()
        

        #updating user model related to this student 

        user = student.user
        
        if args['phone_number']:
            user.phone_number = args['phone_number']
        
        parent = student.parent
        parent_user = parent.user
        if args['guardian_first_name']:
            parent.first_name = args['guardian_first_name'].strip().title()
        if args['guardian_last_name']:
            parent.last_name = args['guardian_last_name'].strip().title()
        if args['guardian_email']:
            parent.email = args['guardian_email'].strip()
            parent_user.email = args['guardian_email'].strip()
        if args['guardian_phone']:
            parent.phone = args['guardian_phone'].strip()
            parent_user.phone_number = args['guardian_phone'].strip()
        if args['relationship']:
            parent.relationship = args['relationship'].strip().title()
        if args['guardian_aadhar_number']:
            parent.aadhar_number = args['guardian_aadhar_number'].strip()

        
        db.session.commit()
        return {'message': 'Student updated successfully'}, 200
    
    @token_required( roles=['admin'])
    def delete(self, student_id):
        student = Student.query.get(student_id)
        user_id = request.user['user_id']
        if not student:
            return {"message": "Student not found"}, 404
        if student.deleted_at is not None:
            return {'message': 'Student already deleted'}, 400
        student.deleted_at = datetime.utcnow() + IST
        student.deleted_by = user_id
        db.session.commit()
        return {'message': 'Student deleted successfully'}, 200
    
    @token_required(roles=['admin'])
    def patch(self,student_id):
        stu_info = Student.query.get(student_id)
        user_id = request.user['user_id']

        if not stu_info:
            return {'message':"Student not found"}
        
        if stu_info.deleted_at is None:
            return {'message':'Student is already active'}
        
        stu_info.deleted_at = None
        stu_info.deleted_by = None
        db.session.commit()
        return {'message':'Student restored successfully'},200

class StudentSubjectResource(Resource):
    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()
        
        parser.add_argument('student_id', type=int, required=True, help='Student ID is required')
        parser.add_argument('subject_ids', type=int, required=True, help='Subject ids is required',action='append')
        args = parser.parse_args()
        student_id = args['student_id']
        subject_ids = args['subject_ids']

        student = Student.query.get(student_id)
        if not student or student.deleted_at is not None:
            return {"message": "Student not found"}, 404

        class_id = student.class_id
        class_info = Class.query.get(class_id)

        if not class_info or class_info.deleted_at is not None:
            return {"message": "Class not found for the student"}, 404
        
        session_id = class_info.session_id
        session = Session.query.get(session_id)
        
        if not session or session.deleted_at is not None or not session.is_active:
            return {"message": "Session is not active or deleted"}, 400

        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        if len(subjects) != len(subject_ids):
            return {'message': 'One or more subject IDs are invalid'}, 400
        
        for subject in subjects:
            existing = StudentSubject.query.filter_by(
                student_id=student.id,
                subject_id=subject.id,
                class_id=class_id,
                session_id=session_id
            ).first()
            if not existing:
                ss = StudentSubject(
                    student_id=student.id,
                    subject_id=subject.id,
                    class_id=class_id,
                    session_id=session_id
                )
                db.session.add(ss)

        db.session.commit()
        return {'message': 'Subjects assigned to student successfully'}, 200

teacher_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'phone': fields.String,
    'email': fields.String,
    
    'user_id': fields.Integer,

    'user': fields.Nested({
        'id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'phone_number': fields.String,
    }),

    'subjects': fields.List( fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        'code': fields.String
    }))
}
teacher_admin_fields = {
    **teacher_fields,  # include everything from normal view
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'deleted_at': fields.DateTime,
    'deleted_by': fields.Integer
}

class TeacherGetCreate(Resource):
    @token_required(roles=['admin'])
    def get(self):
        teachers = Teacher.query.all()
        roles = request.user['role']
        if 'admin' in roles:
            return marshal(teachers,teacher_admin_fields)
        else:
            return marshal(teachers,teacher_fields)

    @token_required( roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()

        # --- User fields ---
        # parser.add_argument('email', type=str, required=True, help='Email is required')
        # parser.add_argument('password', type=str, required=True, help='Password is required')
        # parser.add_argument('phone_number', type=str, required=True, help='Phone number is required')

        # --- Teacher fields ---
        parser.add_argument('first_name', type=str, required=True, help='First name is required')
        parser.add_argument('last_name', type=str, required=True, help='Last name is required')
        parser.add_argument('subject_id', type=int, required=True,action='append', help='Subject ID is required')
        parser.add_argument('teacher_phone', type=str, required=True, help='Teacher phone is required')
        parser.add_argument('teacher_email', type=str, required=True, help='Teacher email is required')

        args = parser.parse_args()
        print(args)
    
        try:
            # Step 1: Create Teacher
            new_teacher = Teacher(
                first_name=args['first_name'].strip().title(),
                last_name=args['last_name'].strip().title(),
               
                phone=args['teacher_phone'].strip(),
                email=args['teacher_email'].strip()
            )
            db.session.add(new_teacher)
            db.session.flush()  # So we get new_teacher.id for username
            print(args.get('subject_id'))
            subject_ids = args.get('subject_id', [])  # a list of IDs
            if subject_ids:
                subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
                
                if len(subjects) != len(subject_ids):
                    return {'message': 'One or more subject IDs are invalid'}, 400

                for subject_obj in subjects:
                    if subject_obj not in new_teacher.subjects:
                        new_teacher.subjects.append(subject_obj)
                

            



            # Step 2: Generate username
            username = generate_username(
                new_teacher.first_name,
                new_teacher.last_name,
                'Teacher',
                new_teacher.id
            )

            # Step 3: Create User
            new_user = User(
                username=username,
                email=args['teacher_email'].strip(),
                password=generate_password_hash('teacher'),
                fs_uniquifier=str(uuid.uuid4()),
                phone_number=args['teacher_phone'].strip()
            )

            # Assign role
            role = Role.query.filter_by(name='teacher').first()
            if not role:
                return {'message': 'Teacher role not found'}, 404

            new_user.roles.append(role)
            db.session.add(new_user)
            db.session.flush()  # Get new_user.id

            # Step 4: Link user_id to teacher
            new_teacher.user_id = new_user.id

            # Step 5: Commit
            db.session.commit()

            return {
                "message": "Teacher created successfully",
                "teacher_id": new_teacher.id
            }, 201

        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return {"error": str(e)}, 500



class TeacherResourceUpdateDelete(Resource):
    @token_required(roles=['admin', 'teacher'])
    def get(self, teacher_id):
        teacher = Teacher.active().filter_by(id=teacher_id).first()
        if not teacher:
            return {"message": "Teacher not found"}, 404

        roles = request.user['role']
        

        if 'admin' in roles:
            return marshal(teacher, teacher_admin_fields)
        else:
            return marshal(teacher, teacher_fields)

    @token_required(roles=['admin'])
    def put(self, teacher_id):
        teacher = Teacher.query.get(teacher_id)
        if not teacher or teacher.deleted_at:
            return {"message": "Teacher not found or deleted"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str)
        parser.add_argument('last_name', type=str)
        parser.add_argument('phone', type=str)
        parser.add_argument('email', type=str)
        # Handle subject updates
        parser.add_argument('add_subject_ids', type=int, action='append')
        parser.add_argument('remove_subject_ids', type=int, action='append')

        args = parser.parse_args()

        if args['first_name']:
            teacher.first_name = args['first_name'].strip().title()
        if args['last_name']:
            teacher.last_name = args['last_name'].strip().title()
        if args['phone']:
            teacher.phone = args['phone'].strip()
        if args['email']:
            teacher.email = args['email'].strip()
        print(args['add_subject_ids'])
        # Add new subjects
        if args['add_subject_ids']:
            subjects_to_add = Subject.query.filter(Subject.id.in_(args['add_subject_ids'])).all()
            for subject in subjects_to_add:
                if subject not in teacher.subjects:
                    teacher.subjects.append(subject)

        # Remove subjects
        if args['remove_subject_ids']:
            for sub_id in args['remove_subject_ids']:
                subject = Subject.query.get(sub_id)
                if subject and subject in teacher.subjects:
                    teacher.subjects.remove(subject)

        db.session.commit()
        return {"message": "Teacher updated successfully"}, 200

    @token_required(roles=['admin'])
    def delete(self, teacher_id):
        teacher = Teacher.query.get(teacher_id)
        user_id = request.user['user_id']
        if not teacher or teacher.deleted_at:
            return {"message": "Teacher not found or already deleted"}, 404

        teacher.deleted_at = datetime.utcnow() + IST
        teacher.deleted_by = user_id

        db.session.commit()
        return {"message": "Teacher soft deleted successfully"}, 200
    
    @token_required(roles=['admin'])
    def patch(self,teacher_id):
        teacher_info = Teacher.query.get(teacher_id)
        user_id = request.user['user_id']

        if not teacher_info:
            return {'message':"Student not found"}
        
        if teacher_info.deleted_at is None:
            return {'message':'Student is already active'}
        
        teacher_info.deleted_at = None
        teacher_info.deleted_by = None
        db.session.commit()
        return {'message':'Student restored successfully'},200

timetable_fields = {
    'id':fields.Integer,
    'class_': fields.Nested({
        'id':fields.Integer,
        'name':fields.String,
        'section':fields.String,
        'session':fields.Nested({
            'id':fields.Integer,
            'name':fields.String,
            'start_date':fields.DateTime,
            'end_date':fields.DateTime,
            'is_active':fields.Boolean

        })
    }),
    'subject': fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        'subject_code': fields.String
        }),
    'teacher': fields.Nested({
        'id': fields.Integer,
        'first_name': fields.String,
        'last_name':fields.String,
        'phone': fields.String,
        'email': fields.String,
    }),
    'day_of_week': fields.String,
    'start_time':fields.String( attribute='formatted_start_time_slot'),
    'end_time': fields.String( attribute='formatted_end_time_slot'),
    'duration':fields.String(attribute='duration'),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime

}
class TimetableGetCreate(Resource):
    @token_required(roles=['admin'])
    def get(self,timetable_id=None):
        if timetable_id:
            timetable_entry = Timetable.query.get(timetable_id)
            if not timetable_entry or timetable_entry.deleted_at:
                return {'message': 'Timetable entry not found or deleted'}, 404
            return marshal(timetable_entry, timetable_fields), 200

    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('class_id', type=int, required=True)
        parser.add_argument('subject_id', type=int, required=True)
        parser.add_argument('teacher_id', type=int, required=True)
        parser.add_argument('day_of_week', type=str, required=True, choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],help='Day must be one of Monday, Tuesday, Wednesday, Thursday, Friday, Saturday')
        parser.add_argument('start_time', type=str, required=True, help='Start time is required in HH:MM format')
        parser.add_argument('end_time', type=str, required=True, help='End time is required in HH:MM format')
        args = parser.parse_args()
        try:
            start_time = datetime.strptime(args['start_time'], '%H:%M').time()
            end_time = datetime.strptime(args['end_time'], '%H:%M').time()
        except ValueError:
            return {'message': 'Invalid time format. Use HH:MM.'}, 400
        class_info = Class.query.get(args['class_id'])
        if not class_info or class_info.deleted_at:
            return {'message': 'Class not found or deleted'}, 404
        subject_info = Subject.query.get(args['subject_id'])
        if not subject_info or subject_info.deleted_at:
            return {'message': 'Subject not found   or deleted'}, 404
        teacher_info = Teacher.query.get(args['teacher_id'])
        if not teacher_info or teacher_info.deleted_at:
            return {'message': 'Teacher not found or deleted'}, 404
        
        #checking for timing consistency
        if start_time >= end_time:
            return {'message': 'Start time must be before end time'}, 400
        

        #checking for overlapping time slots for teacher
        overlapping_entries_teacher = Timetable.query.filter( Timetable.teacher_id == args['teacher_id'], 
        Timetable.day_of_week == args['day_of_week'],
        Timetable.deleted_at == None,
        Timetable.start_time < end_time,
        Timetable.end_time > start_time

        ).all()

        if overlapping_entries_teacher:
            return {'message': 'Teacher has overlapping time slots'}, 400
        
        #checking for overlapping time slots for class
        overlapping_entries_class = Timetable.query.filter(
            Timetable.class_id == args['class_id'],
            Timetable.day_of_week == args['day_of_week'],
            Timetable.deleted_at == None,
            Timetable.start_time < end_time,
            Timetable.end_time > start_time
            ).all()
        if overlapping_entries_class:
            return {'message': 'Class has overlapping time slots'}, 400

        #looking for identical entries to avoid duplicates
        existing_entry = Timetable.query.filter_by(
            class_id=args['class_id'],
            subject_id=args['subject_id'],
            teacher_id=args['teacher_id'],
            day_of_week=args['day_of_week'],
            start_time=start_time,
            end_time=end_time,
            deleted_at=None
            ).first()
        if existing_entry:
            return {'message': 'This timetable entry already exists'}, 400
        
        timetable_entry = Timetable(
            class_id=args['class_id'],
            subject_id=args['subject_id'],
            teacher_id=args['teacher_id'],
            day_of_week=args['day_of_week'],
            start_time=start_time,
            end_time=end_time  
        )
        db.session.add(timetable_entry)
        db.session.commit()
        return {'message': 'Timetable entry created successfully'}, 201
    
class TimetableUpdateDelete(Resource):
    @token_required(roles=['admin'])
    def get(self, class_id):
        class_info = Class.query.get(class_id)
        if not class_info or class_info.deleted_at:
            return {"message": "Class not found or deleted"}, 404


        timetable = Timetable.query.filter_by(
            class_id= class_id,deleted_at=None).order_by(Timetable.day_of_week,Timetable.start_time).all()
        if not timetable :
            return {"message": "Timetable not found for this class"}, 404
        
        grouped = defaultdict(list)
        for entry in timetable:
            grouped[entry.day_of_week].append({
                'id':entry.id,
                'subject':entry.subject.name,
                'teacher':entry.teacher.first_name,
                'start_time': entry.start_time.strftime('%H:%M'),
                'end_time': entry.end_time.strftime('%H:%M')
            })

        return jsonify({
                'class_name': class_info.name,
                'section': class_info.section,
                'timetable': grouped
            })

    @token_required(roles=['admin'])
    def put(self, timetable_id):
        parser = reqparse.RequestParser()
        parser.add_argument('class_id', type=int)
        parser.add_argument('subject_id', type=int, )
        parser.add_argument('teacher_id', type=int, )
        parser.add_argument('day_of_week', type=str, choices=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], help='Day must be one of Monday, Tuesday, Wednesday, Thursday, Friday, Saturday')
        parser.add_argument('start_time', type=str)
        parser.add_argument('end_time', type=str)
        args = parser.parse_args()
        
        
        timetable_entry = Timetable.query.get(timetable_id)
        if not timetable_entry or timetable_entry.deleted_at:
            print("passed timetable entry")
            return {'message': 'Timetable entry not found or deleted'}, 404
        
        class_info=subject_info=teacher_info=None

        if args['class_id']:
            class_info = Class.query.get(args['class_id'])
            if not class_info or class_info.deleted_at:
                print("passed class")
                return {'message': 'Class not found or deleted'}, 404
        
        if args['subject_id']:
            subject_info = Subject.query.get(args['subject_id'])
            if not subject_info or subject_info.deleted_at:
                print("passed subject")
                return {'message': 'Subject not found or deleted'}, 404
            
        if args['teacher_id']:
            teacher_info = Teacher.query.get(args['teacher_id'])
            if not teacher_info or teacher_info.deleted_at:
                print("passed teacher")
                return {'message': 'Teacher not found or deleted'}, 404
        
        try:
            if args['start_time']:
                args['start_time'] = datetime.strptime(args['start_time'], '%H:%M').time()
            if args['end_time']:
                args['end_time'] = datetime.strptime(args['end_time'], '%H:%M').time()
                
        except ValueError:
            print("failed timing parsing")
            return {'message': 'Invalid time format. Use HH:MM.'}, 400
        
        
        #checking for timing consistency
        if args['class_id'] and args['day_of_week']:
            conflict = Timetable.query.filter(
                Timetable.class_id == args['class_id'],
                Timetable.day_of_week == args['day_of_week'],
                Timetable.id != timetable_id,
                Timetable.deleted_at == None,
                Timetable.start_time < args['end_time'],
                Timetable.end_time > args['start_time']
            ).first()
        if conflict:
            return {'message': 'Class has overlapping time slots'}, 400
            
        # Define fields allowed to be updated
        updatable_fields = ['class_id', 'subject_id', 'teacher_id', 'day_of_week', 'start_time', 'end_time']

        

        for field in updatable_fields:
            if field in args and args[field] is not None:
                setattr(timetable_entry, field, args[field])

        db.session.commit()
        return {'message': 'Timetable entry updated successfully'}, 200
    
    @token_required(roles=['admin'])
    def delete(self, timetable_id):
        timetable_entry = Timetable.query.get(timetable_id)
        user_id = request.user['user_id']
        if timetable_entry.deleted_at:
            return {'message': 'Timetable entry is already deleted'}, 404
        
        timetable_entry.deleted_at = datetime.utcnow() + IST
        timetable_entry.deleted_by = user_id

        db.session.commit()
        return {'message': 'Timetable entry deleted successfully'}, 200

class TimeTableDeleteByclassID(Resource):
    @token_required(roles=['admin'])
    def delete(self, class_id):
        timetable_entries = Timetable.query.filter(Timetable.class_id == class_id, Timetable.deleted_at == None).all()
        if not timetable_entries:
            return {'message': 'No timetable entries found for this class'}, 404
        user_id = request.user['user_id']
        for timetable_entry in timetable_entries:
            timetable_entry.deleted_at = datetime.utcnow() + IST
            timetable_entry.deleted_by = user_id
        db.session.commit()
        return {'message': 'Timetable entries deleted successfully'}, 200
    
grade_fields={
    'id': fields.Integer,
    'student': fields.Nested({
        'id': fields.Integer,
        'first_name': fields.String,
        'last_name': fields.String,
        'roll_number': fields.String,
        }),
    'class': fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        'section': fields.String,
    }),

    'grade': fields.String,
    'term': fields.String,
    'subject': fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        }),
    'score': fields.Float,
    'teacher': fields.Nested({
        'id': fields.Integer,
        'first_name': fields.String,
        'last_name': fields.String,
        }),

}

class GradeGetCreate(Resource):
    @token_required(roles=['admin'])
    def get(self,student_id,class_id,term):
        student = Student.query.get(student_id)
        if not student or student.deleted_at:
            return {"message": "Student not found or deleted"}, 404
        class_info = Class.query.get(class_id)
        if not class_info or class_info.deleted_at:
            return {"message": "Class not found or deleted"}, 404
        grades = Grade.query.filter_by(student_id=student_id, class_id=class_id, term=term, deleted_at=None).all()
        if not grades:
            return {"message": "No grades found for this student in this class and term"}, 404
        return marshal(grades, grade_fields), 200

    @token_required(roles=['admin'])
    def post(self, student_id, class_id, term):
        parser = reqparse.RequestParser()
        parser.add_argument('subject_id', type=int, required=True, help='Subject ID is required')
        parser.add_argument('score', type=float, required=True, help='Marks are required')
        # parser.add_argument('student_id', type=int, help='Student ID is required')
        # parser.add_argument('class_id', type=int, help='Class ID is required')
        parser.add_argument('term', type=str, help='Term is required')
        parser.add_argument('teacher_id', type=int, help='Teacher Id is required')
        parser.add_argument('grade', type=str, help='Grade are required')

        args = parser.parse_args()
        student = Student.query.get(student_id)
        if not student or student.deleted_at:
            return {"message": "Student not found or deleted"}, 404
        class_info = Class.query.get(class_id)
        if not class_info or class_info.deleted_at:
            return {"message": "Class not found or deleted"}, 404
        subject = Subject.query.get(args['subject_id'])
        if not subject or subject.deleted_at:
            return {"message": "Subject not found or deleted"}, 404
        teacher = Teacher.query.get(args['teacher_id'])
        if not teacher or teacher.deleted_at:
            return {"message": "Teacher not found or deleted"}, 404
        print(args['subject_id'])
        existing_grade = Grade.query.filter_by(
            student_id=student_id,
            class_id=class_id,
            term=term,
            subject_id=args['subject_id'],
            deleted_at=None
            ).first()
        if existing_grade:
            return {"message": "Grade already exists for this student in this class and term"}, 400
        new_grade = Grade(
            student_id=student_id,
            class_id=class_id,
            term=term,
            subject_id=args['subject_id'],
            score=args['score'],
            teacher_id=args['teacher_id'],
            grade=args['grade']
        )
        db.session.add(new_grade)
        db.session.commit()
        return {'message':'grade added successfully'}, 201



def euclidean(a, b):
    return float(np.linalg.norm(a - b))

def is_match(known_encoding, captured_encoding, threshold=0.5):
    
    if isinstance(known_encoding, str):
        known_encoding = np.array(json.loads(known_encoding))
    elif isinstance(known_encoding, list):
        known_encoding = np.array(known_encoding)

    if isinstance(captured_encoding, str):
        captured_encoding = np.array(json.loads(captured_encoding))
    elif isinstance(captured_encoding, list):
        captured_encoding = np.array(captured_encoding)

    # Optional: round for consistency
    known_encoding = known_encoding.round(4)
    captured_encoding = captured_encoding.round(4)

    distance = euclidean(known_encoding,captured_encoding)
    return distance < threshold


class MarkAttendance(Resource):
    @token_required(roles=['teacher','admin'])
    def post(self):
        # data = request.json
        # captured_encoding = data.get("image")

        # if not captured_encoding:
        #     return {"error": "No face encoding provided"}, 400

        data = request.get_json()
        if not data:
            return {"error": "Invalid JSON"}, 400
        
        image_b64 = data.get("image")
        if not image_b64:
            return {"error": "mage are required"}, 400

        emb = get_embedding_from_base64(image_b64)
        if emb is None:
            return {"error": "No face detected"}, 400
        
        if not isinstance(emb, np.ndarray):
            emb = np.array(emb)

        emb = emb.round(4)

        # Fetch all registered encodings
        encodings = FaceEncoding.query.all()

        matched_student_id = None
        for enc in encodings:

            db_emb = json.loads(enc.encoding)
            db_emb = np.array(db_emb).round(4)

            if is_match(db_emb, emb, threshold=0.6):  # tune threshold
                matched_student_id = enc.student_id
                break

        if not matched_student_id:
            return {"status": "Face not recognized"}, 404

        # Check if already marked today
        today = date.today()
        existing = Attendance.query.filter(
            and_(Attendance.student_id == matched_student_id,
                Attendance.date == today)
        ).first()

        if existing:
            return {"status": "Already marked", "student_id": matched_student_id}, 200

        # Mark attendance
        new_attendance = Attendance(
            student_id=matched_student_id,
            date=today,
            status="Present",
            timestamp=datetime.utcnow()
        )
        db.session.add(new_attendance)
        db.session.commit()

        return {"status": "Attendance marked", "student_id": matched_student_id}, 201

class FetchAttendance(Resource):
    @token_required(roles=['teacher','admin'])
    def get(self):
        class_id = request.args.get('clas',type=int)
        course_id = request.args.get('course',type=int)
        date_str = request.args.get('date')
        print(class_id,course_id,date_str)

        if not class_id or not course_id or not date_str:
            return {"error": "class_id, course_id, and date are required"}, 400
        
        students = (
                db.session.query(Student)
                .join(StudentSubject, Student.id == StudentSubject.student_id)
                .filter(
                StudentSubject.class_id == class_id,
                StudentSubject.subject_id == course_id,
                Student.deleted_at.is_(None)
                )
                .all()
                )
        print(students)

        if not students:
            return {"message": "No students found for this class/course"}, 404

        result = []
        for student in students:
            attendance_record = (
                Attendance.query
                .filter(
                    Attendance.student_id == student.id,
                    func.date(Attendance.date) == date_str  # compares only the date part
                )
                .first()
            )
            result.append({
                "student_id": student.id,
                "name": f"{student.first_name} {student.last_name}",
                "status": attendance_record.status if attendance_record else None,
            })
        print(result)
        
        summary={
            "total": 200,
            "present": 40,
            "absent": 60
            }
        

        return {"students": result, "summary": summary}, 200
    
class FaceRegister(Resource):
    @token_required(roles=['admin'])
    def post(self):
        data = request.get_json()
        student_id = data.get("student_id")
        frames = data.get("frames")

        if not student_id or not frames:
            return {"error": "student_id and frames are required"}, 400

        student = Student.query.get(student_id)
        if not student:
            return {"error": "Invalid student_id"}, 400

        embeddings = []
        for f in frames:
            emb = get_embedding_from_base64(f)
            if emb is not None:
                embeddings.append(emb)

        if len(embeddings) < 2:
            return {"error": "Liveness check failed: not enough valid frames"}, 400

        # Simple liveness check: embeddings across frames must differ slightly
        diffs = [
            float(np.linalg.norm(embeddings[i] - embeddings[i+1]))
            for i in range(len(embeddings)-1)
        ]
        avg_diff = np.mean(diffs)

        if avg_diff < 0.01:  # tune this threshold experimentally
            return {"error": "Likely spoofed (static photo detected)"}, 400

        # Use mean embedding as stable representation
        emb = np.mean(embeddings, axis=0)

        # Existing duplicate check logic here...
        THRESHOLD = 0.6
        INTRA_STUDENT_THRESHOLD = 0.5

        all_faces = FaceEncoding.query.all()
        for row in all_faces:
            db_emb = np.array(json.loads(row.encoding))
            if euclidean(db_emb, emb) < THRESHOLD:
                if row.student_id == student_id:
                    return {'error':'Face already registered for this student'},400
                else:
                    return {'error':f"Face already registered with another student (ID:{row.student_id})"},400

        existing_student_faces = FaceEncoding.query.filter_by(student_id=student_id).all()
        if existing_student_faces:
            distances = [
                euclidean(np.array(json.loads(row.encoding)), emb)
                for row in existing_student_faces
            ]
            min_dist = min(distances)
            if min_dist > INTRA_STUDENT_THRESHOLD:
       
                return {'error': "New face does not match existing faces for this student"}, 400


        encoding_hash = str(hash(tuple(emb.round(4))))
        try:
            rec = FaceEncoding(
                student_id=student_id,
                encoding=json.dumps(emb.tolist()),
                encoding_hash=encoding_hash
            )
            db.session.add(rec)
            db.session.commit()
            return {'message': 'Embedding saved'}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error':'DB error','detail':str(e)},500


class FaceVerify(Resource):
    @token_required(roles=['admin'])
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "Invalid JSON"}, 400

        frames = data.get("frames")  # now expecting list of frames
        top_k = int(data.get("top_k", 1))

        if not frames:
            return {"error": "frames (list of base64 images) is required"}, 400

        if not isinstance(frames, list):
            return {"error": "frames is not instance of list"}, 400

        embeddings = []
        for b64 in frames:
            emb = get_embedding_from_base64(b64)
            if emb is not None:
                embeddings.append(emb)

        if len(embeddings) == 0:
            return {"error": "No valid face detected in frames"}, 400

        # Aggregate embeddings: average → more stable than single frame
        emb = np.mean(np.stack(embeddings), axis=0)
        emb = emb / np.linalg.norm(emb)  # L2 normalize again

        all_rows = FaceEncoding.query.all()
        if not all_rows:
            return {"error": "No embeddings stored"}, 404

        results = []
        for row in all_rows:
            db_emb = np.array(json.loads(row.encoding))
            dist = euclidean(db_emb, emb)
            results.append({
                "id": row.id,
                "student_id": row.student_id,
                "distance": float(dist)  # make JSON serializable
            })

        results = sorted(results, key=lambda x: x["distance"])[:top_k]
        return {"matches": results}, 200

class GetParentStudents(Resource):

    @token_required(roles=['parent'])
    def get(self,user_id=None):
        
        
        parent = Parent.query.filter_by(user_id=user_id, deleted_at=None).first()
        if not parent:
            return {"message": "Parent profile not found"}, 404

        students = Student.query.filter_by(parent_id=parent.id, deleted_at=None).all()
        if not students:
            return {"message": "No students found for this parent"}, 404

        return marshal(students, student_fields), 200

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'phone_number': fields.String,
    'roles': fields.List(fields.String(attribute='name')),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}
class GetUserbyPhone(Resource):
    @token_required(roles=['admin','teacher','parent','student'])
    def get(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            return {"message": "User not found"}, 404

        return marshal(user, user_fields), 200

fee_fields ={
    'id': fields.Integer,
    'student': fields.Nested({
        'id': fields.Integer,
        'first_name': fields.String,
        'last_name': fields.String,
        'roll_number': fields.String,
        }),
    'amount_due': fields.Float,
    'due_date': fields.DateTime,
    'is_paid': fields.Boolean,
    'amount_paid': fields.Float,
    'payment_status': fields.String,
}
class FeeGetCreate(Resource):
    @token_required(roles=['admin','parent'])
    def get(self, student_id=None):
        # Fetch all non-deleted fees
        fees_query = Fee.query.filter_by(deleted_at=None)

        if student_id:
            # Check student existence first
            student = Student.query.filter_by(id=student_id, deleted_at=None).first()
            if not student:
                return {"message": "Student not found or deleted"}, 404

            fees_query = fees_query.filter_by(student_id=student_id)

        # Fetch once
        fees = fees_query.all()

        if not fees:
            return {"message": "No fee records found"}, 404

        return marshal(fees, fee_fields), 200

    @token_required(roles=['admin'])
    def post(self,student_id=None):
        parser = reqparse.RequestParser()
        # parser.add_argument('student_id', type=int, required=True, help='Student ID is required')
        parser.add_argument('amount', type=float, required=True, help='Amount is required')
        parser.add_argument('due_date', type=str, required=True, help='Due date is required in YYYY-MM-DD format')
        args = parser.parse_args()

        student = Student.query.get(student_id)
        if not student or student.deleted_at:
            return {"message": "Student not found or deleted"}, 404

        try:
            due_date = datetime.strptime(args['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        new_fee = Fee(
            student_id=student_id,
            amount_due=args['amount'],
            due_date=due_date
        )
        db.session.add(new_fee)
        db.session.commit()
        return {'message': 'Fee record created successfully'}, 201

class GetPaymentsHistory(Resource):
    @token_required(roles=['admin','parent'])
    def get(self, student_id=None, fee_id=None):
        # Check student existence first
        student = Student.query.filter_by(id=student_id, deleted_at=None).first()
        if not student:
            return {"message": "Student not found or deleted"}, 404

        # Check fee existence
        fees = Fee.query.filter_by( student_id=student_id, deleted_at=None,payment_status='Paid').all()
        if not fees:
            return {"message": "Fee record not found for this student"}, 404

        all_payments =[]
        for fee in fees:
            payments = Payment.query.filter_by(fee_id=fee.id).all()
            if payments:
                all_payments.extend(payments)
        if not all_payments:
                return {"message": "No payment records found for this student"}, 404

        payment_fields = {
            'id': fields.Integer,
            'fee_id': fields.Integer,
            'provider': fields.String,
            'order_id': fields.String,
            'payment_id': fields.String,
            'payment_status': fields.String,
            'amount_paid': fields.Float,
            'payment_date': fields.DateTime,
            'transaction_id': fields.String,
            'payment_method': fields.String,
            'created_at': fields.DateTime
            }

        return marshal(all_payments, payment_fields), 200


razorpay_client = razorpay.Client(auth=(DevelopmentConfig.RAZORPAY_KEY_ID, DevelopmentConfig.RAZORPAY_KEY_SECRET))


class CreateOrder(Resource):
    def post(self,studentId, fee_id):
        fee = Fee.query.get(fee_id)
        if not fee:
            return {"message": "Fee not found"}, 404

        # Convert to paisa for Razorpay
        amount_in_paisa = int(float(fee.amount_due - fee.amount_paid) * 100)

        # Create order with Razorpay
        order = razorpay_client.order.create({
            "amount": amount_in_paisa,
            "currency": "INR",
            "payment_capture": 1
        })

        # Save Payment record (Pending)
        payment = Payment(
            fee_id=fee.id,
            provider="razorpay",
            order_id=order["id"],
            payment_status="Pending",
            amount_paid=fee.amount_due - fee.amount_paid
        )
        db.session.add(payment)
        db.session.commit()

        return {
            "order_id": order["id"],
            "amount": amount_in_paisa,
            "currency": "INR",
            "razorpay_key": DevelopmentConfig.RAZORPAY_KEY_ID
        }, 200


class VerifyPayment(Resource):
    def post(self):
        data = request.json
        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        if not (order_id and payment_id and signature):
            return {"message": "Missing payment details"}, 400

        # Step 1: Verify signature
        body = order_id + "|" + payment_id
        generated_signature = hmac.new(
            bytes(DevelopmentConfig.RAZORPAY_KEY_SECRET, 'utf-8'),
            bytes(body, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != signature:
            return {"message": "Signature verification failed"}, 400

        # Step 2: Fetch payment from DB
        payment = Payment.query.filter_by(order_id=order_id).first()
        if not payment:
            return {"message": "Payment record not found"}, 404

        # Step 3: Fetch from Razorpay server (optional but safer)
        payment_data = razorpay_client.payment.fetch(payment_id)
        status = payment_data.get("status")

        if status == "captured":
            payment.payment_id = payment_id
            payment.payment_status = "Successful"
            payment.payment_date = datetime.utcnow()
            payment.transaction_id = payment_data.get("acquirer_data", {}).get("bank_transaction_id")
            payment.payment_method = payment_data.get("method")

            # Update fee
            fee = payment.fee
            fee.amount_paid += Decimal(payment.amount_paid)
            if fee.amount_paid >= fee.amount_due:
                fee.payment_status = "Paid"

            db.session.commit()
            return {"message": "Payment successful"}, 200

        else:
            payment.payment_status = "Failed"
            db.session.commit()
            return {"message": "Payment failed"}, 400

def user_display_for(owner_id: int, other: User):
    
    contact = Contact.query.filter_by(owner_id=owner_id, contact_user_id=other.id).first()
    if contact and contact.saved_name:
        return contact.saved_name
    if other.profile_name:
        return other.profile_name
    return other.phone_number

class GetInboxMessages(Resource):
    @token_required(roles=['admin','teacher','parent','student'])
    def get(self):
        user_id = request.user['user_id']

        # Subquery: get latest message id for each conversation
        latest_msg_subq = (
            db.session.query(
                func.max(Message.id).label("latest_id"),
                func.least(Message.sender_id, Message.receiver_id).label("user1"),
                func.greatest(Message.sender_id, Message.receiver_id).label("user2")
            )
            .filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
            .group_by("user1", "user2")
            .subquery()
        )

        # Join messages with that subquery
        latest_msgs = (
            db.session.query(Message)
            .join(latest_msg_subq, Message.id == latest_msg_subq.c.latest_id)
            .order_by(Message.sent_at.desc())
            .all()
        )

        inbox = []
        for msg in latest_msgs:
            # Find the other person in chat
            other_user_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
            other_user = User.query.get(other_user_id)

            # Check if user already saved this number as contact
            print("Looking for contact", user_id, other_user_id)
            contact = Contact.query.filter_by(owner_id=user_id, contact_user_id=other_user_id).first()
            # print("contact found", contact)

            inbox.append({
                "message_id": msg.id,
                "text": msg.message_text,
                "timestamp": msg.sent_at.isoformat(),
                "is_sender": msg.sender_id == user_id,
                "other_user": {
                    "id": other_user.id,
                    "phone_number": other_user.phone_number,
                    "name": contact.custom_name if contact else None,  # show saved name if exists
                    "is_saved": True if contact else False
                }
            })

        # print("Inbox:", inbox)
        return inbox,200
class GetConversation(Resource):
    @token_required(roles=['admin','teacher','parent','student'])
    def get(self,other_id):
        current_user_id = request.user['user_id']

        # optional pagination
        limit = min(int(request.args.get('limit', 50)), 200)
        messages = (Message.query
                    .filter(
                        or_(
                            db.and_(Message.sender_id == current_user_id, Message.receiver_id == other_id),
                            db.and_(Message.sender_id == other_id, Message.receiver_id == current_user_id),
                        )
                    )
                    .order_by(Message.sent_at.asc())
                    .limit(limit)
                    .all())

        convo = [{
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message_text": m.message_text,
            "sent_at": m.sent_at.isoformat()
        } for m in messages]
        return convo, 200

class SendMessage(Resource):
    @token_required(roles=['admin','teacher','parent','student'])
    def post(self):
        current_user_id = request.user['user_id']
        data = request.get_json() or {}
        receiver_id = data.get('receiver_id')
        message_text = (data.get('message_text') or '').strip()

        if not receiver_id or not message_text:
            print("Missing fields", receiver_id, message_text)
            return {"error": "receiver_id and message_text required"}, 400
        if receiver_id == current_user_id:
            print("Cannot message self")
            return {"error": "cannot message yourself"}, 400

        # Ensure receiver exists
        if not User.query.get(receiver_id):
            return {"error": "receiver not found"}, 404

        msg = Message(sender_id=current_user_id, receiver_id=receiver_id, message_text=message_text, sent_at=datetime.utcnow() + IST)
        db.session.add(msg)
        db.session.commit()

        msg_data = {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "message_text": msg.message_text,
            "sent_at": msg.sent_at.isoformat()
        }

        socketio.emit('receive_message',msg_data, room=str(receiver_id))

        socketio.emit('receive_message',msg_data, room=str(current_user_id))
        return {"success": True}, 201
    
class ContactSave(Resource):
    @token_required(roles=['admin','teacher','parent','student'])
    def post(self):
        current_user_id = request.user['user_id']
        data = request.get_json() or {}
        contact_user_id = data.get('contact_user_id')
        custom_name = (data.get('saved_name') or '').strip()

        if not contact_user_id or not custom_name:
            return jsonify({"error": "contact_user_id and custom_name required"}), 400
        if contact_user_id == current_user_id:
            return jsonify({"error": "cannot save yourself as contact"}), 400

        # Ensure contact user exists
        contact_user = User.query.get(contact_user_id)
        if not contact_user:
            return jsonify({"error": "contact user not found"}), 404

        # Check if already saved
        contact = Contact.query.filter_by(owner_id=current_user_id, contact_user_id=contact_user_id).first()
        if contact:
            contact.custom_name = custom_name  # update name
            db.session.commit()
            return {"message": "Contact updated"}, 200

        # Create new contact
        new_contact = Contact(owner_id=current_user_id, contact_user_id=contact_user_id, custom_name=custom_name)
        db.session.add(new_contact)
        db.session.commit()
        return {"message": "Contact saved"}, 201

api.add_resource(Login, '/login')

api.add_resource(GetUserbyPhone, '/get_users/<string:phone_number>', endpoint='user_get_by_phone')
api.add_resource(GetUserById,'/check_status/<int:user_id>')
api.add_resource(ContactSave, '/save_contact', endpoint='save_contact')

# <-------------- Api message operations ------------->
api.add_resource(GetInboxMessages, '/messages/inbox', endpoint='get_inbox')
api.add_resource(GetConversation, '/messages/conversation/<int:other_id>', endpoint='get_conversation')
api.add_resource(SendMessage, '/messages/send',endpoint='send_message')



# <-------------- Api attendance operations ------------->

api.add_resource(MarkAttendance, '/attendance/mark', endpoint='mark_attendance')
api.add_resource(FetchAttendance, '/fetch_attendance', endpoint='fetch_attendance')



# <------------Api class crud operations ------------->

api.add_resource(ClassGetCreate, '/get_classes',endpoint='classes_get')  # Using endpoint to avoid conflict with ClassUpdateDelete
api.add_resource(ClassGetCreate, '/create_class', endpoint='classes_post')  # Using endpoint to avoid conflict with ClassUpdateDelete
api.add_resource(ClassUpdateDelete, '/get_class/<int:class_id>', endpoint='classes_get_by_id')
api.add_resource(ClassUpdateDelete, '/update_class/<int:class_id>',endpoint='classes_update')
api.add_resource(ClassUpdateDelete, '/delete_class/<int:class_id>', endpoint='classes_delete')
api.add_resource(ClassUpdateDelete,'/restore_class/<int:class_id>')

# <------------- Api subject crud operations ------------->     

api.add_resource(SubjectGetCreate, '/get_subjects', endpoint='subjects_get')  # Using endpoint to avoid conflict with SubjectUpdateDelete
api.add_resource(SubjectGetCreate, '/create_subject', endpoint='subjects_post')  # Using endpoint to avoid conflict with SubjectUpdateDelete
api.add_resource(SubjectUpdateDelete, '/get_subject/<int:subject_id>', endpoint='subjects_get_by_id')
api.add_resource(SubjectUpdateDelete, '/update_subject/<int:subject_id>', endpoint='subjects_update')
api.add_resource(SubjectUpdateDelete, '/delete_subject/<int:subject_id>', endpoint='subjects_delete')

# <---------------- Api session crud operations ------------->

api.add_resource(SessionGetCreate, '/get_sessions', endpoint='sessions_get')  # Using endpoint to avoid conflict with SessionUpdateDelete
api.add_resource(SessionGetCreate, '/create_session', endpoint='sessions_post')  # Using endpoint to avoid conflict with SessionUpdateDelete
api.add_resource(SessionUpdateDelete, '/get_session/<int:session_id>', endpoint='sessions_get_by_id')
api.add_resource(SessionUpdateDelete, '/update_session/<int:session_id>', endpoint='sessions_update')
api.add_resource(SessionUpdateDelete, '/delete_session/<int:session_id>', endpoint='sessions_delete')

# <- <---------------- Api student crud operations -------------> 

api.add_resource(StudentGetCreate, '/get_students', endpoint='students_get') 
api.add_resource(StudentGetCreate, '/create_student', endpoint='students_post')
api.add_resource(StudentUpdateDelete, '/get_student/<int:student_id>', endpoint='students_get_by_id')
api.add_resource(StudentUpdateDelete, '/update_student/<int:student_id>', endpoint='students_update')
api.add_resource(StudentUpdateDelete, '/delete_student/<int:student_id>', endpoint='students_delete')
api.add_resource(StudentUpdateDelete,'/restore_student/<int:student_id>',endpoint='student_restore')
api.add_resource(StudentSubjectResource, '/assign_subject_to_student', endpoint='students_aubject assignment')


# <---------------- Api teacher crud operations ------------->
api.add_resource(TeacherGetCreate, '/get_teachers', endpoint='teachers_get')
api.add_resource(TeacherGetCreate, '/create_teacher', endpoint='teachers_post')
api.add_resource(TeacherResourceUpdateDelete, '/get_teacher/<int:teacher_id>', endpoint='teachers _get_by_id')
api.add_resource(TeacherResourceUpdateDelete, '/update_teacher/<int:teacher_id>', endpoint='teachers_update')
api.add_resource(TeacherResourceUpdateDelete, '/delete_teacher/<int:teacher_id>', endpoint='teachers_delete')
api.add_resource(TeacherResourceUpdateDelete,'/restore_teachers/<int:teacher_id>',endpoint='teachers_restore')

# <---------------- Api timetable crud operations ------------->

api.add_resource(TimetableGetCreate, '/create_timetable', endpoint='timetable_post')
api.add_resource(TimetableGetCreate, '/get_timetable_timetable_id/<int:timetable_id>', endpoint='timetable_get_by_id')
api.add_resource(TimetableUpdateDelete, '/get_timetable/<int:class_id>', endpoint='timetable_get_by_class_id')
api.add_resource(TimetableUpdateDelete, '/update_timetable/<int:timetable_id>', endpoint='timetable_update')
api.add_resource(TimetableUpdateDelete, '/delete_timetable/<int:timetable_id>', endpoint='timetable_delete')
api.add_resource(TimeTableDeleteByclassID, '/delete_timetables_by_class_id/<int:class_id>', endpoint='timetables_class_delete')

# <---------------- Api grade crud operations ------------->
api.add_resource(GradeGetCreate, '/get_grades/<int:student_id>/<int:class_id>/<string:term>', endpoint='grades_get')
api.add_resource(GradeGetCreate, '/create_grade/<int:student_id>/<int:class_id>/<string:term>', endpoint='grades_post')

# <---------------- Api fees crud operations ------------->
api.add_resource(FeeGetCreate, '/get_fees/<int:student_id>', endpoint='fees_get_all')
api.add_resource(FeeGetCreate, '/create_fees/<int:student_id>', endpoint='fees_create')
api.add_resource(GetPaymentsHistory, '/get_payments_history/<int:student_id>', endpoint='payments_history_get')


# <---------------- Api parent students operations ------------->
api.add_resource(GetParentStudents, '/get_parent_students/<int:user_id>', endpoint='parent_students_get')


# <---------------- Api payment operations ------------->
api.add_resource(CreateOrder, '/create_order/<int:studentId>/<int:fee_id>', endpoint='create_order')
api.add_resource(VerifyPayment, '/verify_payment', endpoint='verify_payment')


# <---------------- Face register operations ------------->

api.add_resource(FaceRegister, '/register_face', endpoint='face_register')
api.add_resource(FaceVerify, '/verify_face', endpoint='face_verify')