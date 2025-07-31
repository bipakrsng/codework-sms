from flask_restful import Resource, Api,reqparse,marshal_with,fields,marshal
from backend.models.models import *
from flask import request, jsonify,make_response

from datetime import datetime,timedelta
from werkzeug.security import check_password_hash,generate_password_hash
import jwt
from functools import wraps
from config import DevelopmentConfig
import re
import uuid




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
        'role':[role.name for role in user.roles],
        'exp': datetime.utcnow() + timedelta(minutes=15)  # Token valid for 1 day #token shpould update if user is active and if ideal then expires
    }
    token = jwt.encode(payload, DevelopmentConfig.SECRET_KEY, algorithm='HS256')
    return token

def token_required(roles=[]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            token = request.cookies.get('access_token')
            if not token:
                return {"message": "Token is missing!"}, 401
            try:
                payload = jwt.decode(token, DevelopmentConfig.SECRET_KEY, algorithms=['HS256'])
                if roles:
                    print(roles)
                
                if payload.get('role'):
                    print(payload.get('role'))
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
            return {'message': 'Invalid email format'}, 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return {'message': 'User not found'}, 404

        if check_password_hash(user.password,password):

            utcnow = datetime.utcnow()
            time_diff = timedelta(hours=5,minutes=30)  # Adjust for IST (UTC+5:30)
            istnow = utcnow + time_diff
            user.last_login_at = istnow
            token = create_token(user)
            
            db.session.commit()
            resp = make_response(jsonify({'message': 'Login successful','token':token}), 200)
            resp.set_cookie('access_token', token, httponly=True, secure=True, samesite=None)
            return resp
        else:
            return {'message': 'Invalid password'}, 401



# <----------------------- class details CRUD OPeration ------------------>

#formatting class fields for response
class_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'section':fields.String,
    'session_id': fields.Integer,  # Assuming session_id is an integer
}
class ClassGetCreate(Resource):
    #authentication missing
   
    
    @token_required(roles=['admin'])
    def get(self):
        classes = Class.active().all()
        
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
        if not class_info:
            return {"message": "Class not found"}, 404
        if class_info.deleted_at is not None:
            return {"message": "Class already deleted"}, 400
        class_info.deleted_at = datetime.utcnow() + IST
        class_info.deleted_by = user_id
        db.session.commit()
        
        return {'message': 'Class deleted successfully'}, 200
    

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
        sessions = Session.active().all()
        return sessions, 200
    
    @token_required(roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Session name is required')
        parser.add_argument('start_date', type=str, required=True, help='Start date is required')
        parser.add_argument('end_date', type=str, required=True, help='End date is required')
        parser.add_argument('is_active', type=bool, default=False, help='Is active status')

        args = parser.parse_args()
        try:
            start_date = datetime.strptime(args['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(args['end_date'], '%Y-%m-%d').date()  
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        session = Session(name=args['name'].title(), start_date=start_date, end_date=end_date, is_active=args['is_active'])
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
        parser.add_argument('name', type=str, location='json')
        parser.add_argument('start_date', type=str, location='json')
        parser.add_argument('end_date', type=str, location='json')
        parser.add_argument('is_active', type=bool, location='json')
        args = parser.parse_args()
        session = Session.query.get(session_id)
        if not session:
            return {"message": "Session not found"}, 404
        if args['name']:
            session.name = args['name'].title()
        if args['start_date']: 
            try:
                session.start_date = datetime.strptime(args['start_date'], '%Y-%m-%d').date()  
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        if args['end_date']:
            try:
                session.end_date = datetime.strptime(args['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        if args['is_active'] is not None:
            session.is_active = args['is_active']
        
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
    'guardian_contact': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    
    # nested fields
    'parent': fields.Nested({
        'id': fields.Integer,
        'user_id': fields.Integer,
        'first_name': fields.String,
        'last_name': fields.String,
        'phone': fields.String,
        'email': fields.String,
        'aadhar_number': fields.String,
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
        students = Student.active().all()
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
        parser.add_argument('aadhar_number', type=str, required=True, help='Aadhar number is required')
        parser.add_argument('apaar_id',type=str,required= True,help='Provide apaar id')

        # --- Guardian/Parent Fields ---
        parser.add_argument('guardian_first_name', type=str, required=True, help='Guardian first name is required')
        parser.add_argument('guardian_last_name', type=str, required=True, help='Guardian last name is required')
        parser.add_argument('guardian_email', type=str, required=True, help='Guardian email is required')
        parser.add_argument('guardian_phone', type=str, required=True, help='Guardian phone is required')
        parser.add_argument('relationship', type=str, required=True, help='Relationship is required')
        parser.add_argument('guardian_aadhar_number',type= str,required=True,help='Guardian aadhar number is required')

        args = parser.parse_args()

        # --- Validate date format ---
        try:
            date_of_birth = datetime.strptime(args['date_of_birth'], '%Y-%m-%d').date()
            admission_date = datetime.strptime(args['admission_date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

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
                aadhaar_number=args['aadhar_number'].strip(),
                apaar_id=args['apaar_id'].strip()

            )
            db.session.add(new_student)
            db.session.flush()  # get student.id

            username = generate_username(
                new_student.first_name,
                new_student.last_name,
                'Student',
                new_student.id
            )

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

            

            parent = Parent.query.filter_by(aadhar_number=args['guardian_aadhar_number'].strip()).first()
            if parent:
                new_student.parent_id = parent.id
                
            
            else:
                    parent = Parent(
                    first_name=args['guardian_first_name'].strip().title(),
                    last_name=args['guardian_last_name'].strip().title(),
                    email=args['guardian_email'].strip(),
                    phone=args['guardian_phone'].strip(),
                    relationship=args['relationship'].strip().title(),
                    aadhar_number=args['guardian_aadhar_number'].strip()
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
            db.session.rollback()
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
        parser.add_argument('aadhar_number', type=str, required=True, help='Aadhar number is required')
        parser.add_argument('apaar_id',type=str,required= True,help='Provide apaar id')

        # --- Guardian/Parent Fields ---
        parser.add_argument('guardian_first_name', type=str, required=True, help='Guardian first name is required')
        parser.add_argument('guardian_last_name', type=str, required=True, help='Guardian last name is required')
        parser.add_argument('guardian_email', type=str, required=True, help='Guardian email is required')
        parser.add_argument('guardian_phone', type=str, required=True, help='Guardian phone is required')
        parser.add_argument('relationship', type=str, required=True, help='Relationship is required')
        parser.add_argument('guardian_aadhar_number',type= str,required=True,help='Guardian aadhar number is required')

        args = parser.parse_args()

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
        teachers = Teacher.active().all()
        roles = request.user['role']
        if 'admin' in roles:
            return marshal(teachers,teacher_admin_fields)
        else:
            return marshal(teachers,teacher_fields)

    @token_required( roles=['admin'])
    def post(self):
        parser = reqparse.RequestParser()

        # --- User fields ---
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        parser.add_argument('phone_number', type=str, required=True, help='Phone number is required')

        # --- Teacher fields ---
        parser.add_argument('first_name', type=str, required=True, help='First name is required')
        parser.add_argument('last_name', type=str, required=True, help='Last name is required')
        parser.add_argument('subject_id', type=int, required=True,action='append', help='Subject ID is required')
        parser.add_argument('teacher_phone', type=str, required=True, help='Teacher phone is required')
        parser.add_argument('teacher_email', type=str, required=True, help='Teacher email is required')

        args = parser.parse_args()

    
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
                email=args['email'].strip(),
                password=generate_password_hash(args['password'].strip()),
                fs_uniquifier=str(uuid.uuid4()),
                phone_number=args['phone_number'].strip()
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

    
api.add_resource(Login, '/login')

# <------------Api class crud operations ------------->

api.add_resource(ClassGetCreate, '/get_classes',endpoint='classes_get')  # Using endpoint to avoid conflict with ClassUpdateDelete
api.add_resource(ClassGetCreate, '/create_class', endpoint='classes_post')  # Using endpoint to avoid conflict with ClassUpdateDelete
api.add_resource(ClassUpdateDelete, '/get_class/<int:class_id>', endpoint='classes_get_by_id')
api.add_resource(ClassUpdateDelete, '/update_class/<int:class_id>',endpoint='classes_update')
api.add_resource(ClassUpdateDelete, '/delete_class/<int:class_id>', endpoint='classes_delete')

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



# <---------------- Api teacher crud operations ------------->
api.add_resource(TeacherGetCreate, '/get_teachers', endpoint='teachers_get')
api.add_resource(TeacherGetCreate, '/create_teacher', endpoint='teachers_post')
api.add_resource(TeacherResourceUpdateDelete, '/get_teacher/<int:teacher_id>', endpoint='teachers _get_by_id')
api.add_resource(TeacherResourceUpdateDelete, '/update_teacher/<int:teacher_id>', endpoint='teachers_update')
api.add_resource(TeacherResourceUpdateDelete, '/delete_teacher/<int:teacher_id>', endpoint='teachers_delete')