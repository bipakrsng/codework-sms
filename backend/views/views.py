# face_recognition_app.py
import cv2
from flask import current_app as app
import pickle
import numpy as np
from ..models.models import db
#from ..embeddings import get_face_embedding
from flask import render_template,request,jsonify
import base64


@app.get('/')
def home():
    return render_template('home.html')


@app.get('/register')
def register():
    return render_template('register.html')

# @app.post('/register')
# def register_face():
#     data = request.get_json()
#     name = data.get('name')
#     image_data = data.get('image')

#     if not name or not image_data:
#         return {"error": "Name and image data are required."}, 400
    
#     try:
#         # Decode the image data
#         img_data = image_data.split(',')[1]
#         img_array = np.frombuffer(base64.b64decode(img_data), np.uint8)
#         image = cv2.imdecode(img_array,cv2.IMREAD_COLOR)

#         embedding = get_face_embedding(image)
#         if embedding is None:
#             return jsonify({"error": "No face detected in the image."}), 400
        
#         all_face = Face.query.all()

#         # if not all_face:
#         #     return jsonify({"error": "No faces registered."}), 400

#         # Check if the face is already registered
#         if all_face:
#             for face in all_face:
#                 db_embedding = pickle.loads(face.embedding)
#                 dist = np.linalg.norm(embedding - db_embedding)
#                 if dist < 0.6:
#                     return jsonify({"error": "Face already registered."}), 400
#                 else:
#                     # Save the new face
#                     new_face = Face(name=name, embedding=pickle.dumps(embedding))
#                     db.session.add(new_face)
#                     db.session.commit()
#                     return jsonify({"message": "Face registered successfully."}), 200
#         else:
#             new_face = Face(name=name, embedding=pickle.dumps(embedding))
#             db.session.add(new_face)
#             db.session.commit()
#             return jsonify({"message": "Face registered successfully."}), 200
#     except Exception as e:
#         print(f"Error : {e}")
#         return jsonify({"error": "An error occurred while processing the image."}), 500

#  @app.get('/attendance')

# def attendance():
#     return render_template('attendance.html')

# @app.post('/attendance')
# def mark_attendance():
#     data = request.get_json()
#     if not data or 'image' not in data:
#         return jsonify({"error": "Image data is required."}), 400
#     image_data = data['image']
    

#     try:
#         # Decode the image data
#         img_data = image_data.split(',')[1]
#         img_array = np.frombuffer(base64.b64decode(img_data), np.uint8)
#         image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#         embedding = get_face_embedding(image)
#         if embedding is None:
#             return jsonify({"error": "No face detected in the image."}), 400
#         all_face = Face.query.all()
#         if not all_face:
#             return jsonify({"error": "No faces registered."}), 400
        
#         recognized_faces = None
#         for face in all_face:
#             db_embedding = pickle.loads(face.embedding)
#             dist = np.linalg.norm(embedding - db_embedding)
#             if dist < 0.6:
#                 recognized_faces=face.name
#                 break

#         if recognized_faces:
#             print(f"Recognized Faces: {recognized_faces}")
#             return jsonify({"message": f"welcome {recognized_faces}, Your attendance has been marked"}), 200
#         else:
#             print("No recognized faces found.")
#             return jsonify({"message": "you're not registered. contact administration to get yourself registered"}),200
#     except Exception as e:
#         print(f"Error : {e}")
#         return jsonify({"error": "An error occured while processing the image"}), 500


