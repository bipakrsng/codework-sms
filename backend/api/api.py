from flask_restful import Resource, Api,reqparse,marshal_with,fields,marshal
from backend.models.models import *
from flask import request, jsonify,make_response
from flask_security import auth_required, current_user, roles_required
from datetime import datetime,timedelta
from werkzeug.security import check_password_hash
import jwt
from functools import wraps
from config import DevelopmentConfig
import re


api = Api(prefix='/api')

def create_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role':user.roles[0].name if user.roles else None,
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
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                payload = jwt.decode(token, DevelopmentConfig.SECRET_KEY, algorithms=['HS256'])
                if roles and payload.get('role') not in roles:
                    return jsonify({'message': 'You do not have permission to access this resource based on roles'}), 403
                request.user = payload
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token!'}), 401
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
            user.token = token
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
    @marshal_with(class_fields)
    def get(self):
        classes = Class.query.all()
        return classes,200
   
    
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

        
        new_class = Class(name=args['name'],section=args.get('section','A'),session_id = args['session_id']) #providing defaukt section 'A' if not provided
        db.session.add(new_class)
        db.session.commit()
        return {'message': 'Class created successfully'}, 201

class ClassUpdateDelete(Resource):
    #SQL Injection and XSS attacks are prevented by using ORM and input validation
    @marshal_with(class_fields)
    def get(self,class_id):
        class_info = Class.query.get(class_id)
        if not class_info:
            return {"mesage":"class not found"},404
        return class_info,200


    def put(self,class_id):
        
        parser = reqparse.RequestParser()
        parser.add_argument('name',type=str,location='json')
        parser.add_argument('section',type=str,location='json')
        args = parser.parse_args()
        class_info = Class.query.get(class_id)
        if not class_info:
            return {"message": "Class not found"}, 404
        if args['name']:
            class_info.name = args['name']
            
        if args['section']:
            class_info.section = args['section']
            
        db.session.commit()
        return {'message': 'Class updated successfully'}, 200
        
    def delete(self,class_id):
        class_info = Class.query.get(class_id)
        if not class_info:
            return {"message": "Class not found"}, 404
        db.session.delete(class_info)
        db.session.commit()
        return {'message': 'Class deleted successfully'}, 200
    

# <----------------------- subject details CRUD OPeration ------------------>

subject_fields = {
    'id': fields.Integer,
    'name': fields.String, #subjectcode createdat updatedat

    

}
class SubjectGetCreate(Resource):
    @marshal_with(subject_fields)
    def get(Self):
        subjects = Subject.query.all()
        return subjects, 200
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Subject name is required')
        args = parser.parse_args()
        new_subject = Subject(name=args['name'])
        db.session.add(new_subject) # Add the new subject to the session
        db.session.commit()
        return {'message': 'Subject created successfully'}, 201

class SubjectUpdateDelete(Resource):
    @marshal_with(subject_fields)
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404
        return subject, 200

    def put(self, subject_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='json')
        args = parser.parse_args()
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404
        if args['name']:
            subject.name = args['name']
        db.session.commit()
        return {'message': 'Subject updated successfully'}, 200

    def delete(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404
        db.session.delete(subject)
        db.session.commit()
        return {'message': 'Subject deleted successfully'}, 200
    

# <----------------------- session details CRUD OPeration ------------------>

session_fields={
    'id': fields.Integer,
    'name': fields.String,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'is_active': fields.Boolean,
    'created_at': fields.DateTime
}
class SessionGetCreate(Resource):
    @marshal_with(session_fields)
    def get(self):
        sessions = Session.query.all()
        return sessions, 200
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
        session = Session(name=args['name'], start_date=start_date, end_date=end_date, is_active=args['is_active'])
        db.session.add(session)
        db.session.commit()
        return {'message': 'Session created successfully'}, 201
    
class SessionUpdateDelete(Resource):
    @marshal_with(session_fields)
    def get(self, session_id):
        session = Session.query.get(session_id)
        if not session:
            return {"message": "Session not found"}, 404
        return session, 200
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
            session.name = args['name']
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
    
    def delete(self, session_id):
        session = Session.query.get(session_id)
        if not session:
            return {"message": "Session not found"}, 404
        db.session.delete(session)
        db.session.commit()
        return {'message': 'Session deleted successfully'}, 200


# <----------------------- student details CRUD OPeration ------------------>
    
student_fields={
    'id': fields.Integer,
    'user_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'date_of_birth': fields.DateTime,
    'gender': fields.String,
    'address': fields.String, # need to change to address_line1, address_line2, city, state, postal_code, country
    'class_id': fields.Integer,
    'guardian_contact': fields.String
}
class StudentGetCreate(Resource):
    @marshal_with(student_fields)
    def get(self):
        students = Student.query.all()
        return students, 200
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='User ID is required')
        parser.add_argument('first_name', type=str, required=True, help='First name is required')
        parser.add_argument('last_name', type=str)
        parser.add_argument('date_of_birth', type=str, required=True, help='Date of birth is required')
        parser.add_argument('gender', type=str, required=True, help='Gender is required')
        parser.add_argument('address_line1', type=str, required=True, help='Address is required')
        parser.add_argument('address_line2', type=str)
        parser.add_argument('city', type=str, required=True, help='City is required')
        parser.add_argument('state', type=str, required=True, help='State is required')
        parser.add_argument('postal_code', type=str, required=True, help='Postal code is required')
        parser.add_argument('country', type=str, required=True, help='Country is required')
        parser.add_argument('class_id', type=int, required=True, help='Class ID is required')
        parser.add_argument('guardian_contact', type=str,required= True, help='Guardian contact is required')  
        args = parser.parse_args()
        try:
            date_of_birth = datetime.strptime(args['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        # Validate user_id and class_id
        user = User.query.get(args['user_id']) 
        if not user:
            return {'message': 'User not found'}, 404
        class_info = Class.query.get(args['class_id'])
        if not class_info:
            return {'message': 'Class not found'}, 404
        new_student = Student(
            user_id=args['user_id'],
            first_name=args['first_name'],
            last_name=args.get('last_name', ''),
            date_of_birth=date_of_birth,
            gender=args['gender'],
            address_lin1=args['address_line1'],
            address_line2=args.get('address_line2', ''),
            city=args['city'],
            state=args['state'],
            postal_code=args['postal_code'],
            country=args['country'],
            class_id=args['class_id'],
            guardian_contact=args['guardian_contact']
        )
        db.session.add(new_student)
        db.session.commit()
        return {'message': 'Student created successfully'}, 201

class StudentUpdateDelete(Resource):
    @marshal_with(student_fields)
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Student not found"}, 404
        return student, 200
    def put(self, student_id):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='json')
        parser.add_argument('first_name', type=str, location='json')
        parser.add_argument('last_name', type=str, location='json')
        parser.add_argument('date_of_birth', type=str, location='json')
        parser.add_argument( 'gender', type=str, location='json')
        parser.add_argument('address_line1', type=str, location='json')
        parser.add_argument('address_line2', type=str, location='json')
        parser.add_argument('city', type=str, location='json')
        parser.add_argument('state', type=str, location='json')
        parser.add_argument('postal_code', type=str, location='json')
        parser.add_argument('country', type=str, location='json')
        parser.add_argument('class_id', type=int, location='json')
        parser.add_argument('guardian_contact', type=str, location='json')
        args = parser.parse_args()
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Student not found"}, 404
        if args['user_id']:
            user = User.query.get(args['user_id'])
            if not user:
                return {'message': 'User not found'}, 404
            student.user_id = args['user_id']
        if args['first_name']:
            student.first_name = args['first_name'] 
        if args['last_name']:
            student.last_name = args['last_name']
        if args['date_of_birth']:
            try:
                student.date_of_birth = datetime.strptime(args['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        if args['gender']:
            student.gender = args['gender']
        if args['address_line1']:
            student.address_line1 = args['address_line1']
        if args['address_line2']:
            student.address_line2 = args['address_line2']
        if args['city']:
            student.city = args['city']
        if args['state']:
            student.state = args['state']
        if args['postal_code']:
            student.postal_code = args['postal_code']
        if args['country']:
            student.country = args['country']
        if args['class_id']:
            class_obj = Class.query.get(args['class_id'])
            if not class_obj:
                return {'message': 'Class not found'}, 404
            student.class_id = args['class_id']
        if args['guardian_contact']:
            student.guardian_contact = args['guardian_contact']
        db.session.commit()
        return {'message': 'Student updated successfully'}, 200
    
    def delete(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Student not found"}, 404
        db.session.delete(student)
        db.session.commit()
        return {'message': 'Student deleted successfully'}, 200
    



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
