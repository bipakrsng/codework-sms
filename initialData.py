from app import app,datastore
from backend.models.models import db, User,Role
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    datastore.find_or_create_role(name = "admin",description = "Administrator with full access")
    datastore.find_or_create_role(name = "student",description = "User is student with limited access")
    datastore.find_or_create_role(name = "teacher",description = "User is teacher with limited access")

    db.session.commit()

    if not datastore.find_user(email="admin@gmail.com"):
        datastore.create_user(email="admin@gmail.com",username = "admin", password=generate_password_hash("admin123"),roles=["admin"])

    if not datastore.find_user(email="student@gmail.com"):
        datastore.create_user(email="student@gmail.com",username="student", password=generate_password_hash("student123"),roles=["student"])
    if not datastore.find_user(email="teacher@gmail.com"):
        datastore.create_user(email="teacher@gmail.com",username ="teacher", password=generate_password_hash("teacher123"),roles=["teacher"])
    db.session.commit()
                               
                
