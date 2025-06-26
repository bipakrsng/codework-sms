# import dlib
# import numpy as np
# import cv2
# import os

# model_path = os.path.join(os.path.dirname(__file__),'shape_predictor_68_face_landmarks.dat','shape_predictor_68_face_landmarks.dat')
# model_path2 = os.path.join(os.path.dirname(__file__),'dlib_face_recognition_resnet_model_v1.dat','dlib_face_recognition_resnet_model_v1.dat')
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor(model_path)
# face_rec = dlib.face_recognition_model_v1(model_path2)


# def get_face_embedding(image):
#     gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#     faces = detector(gray)

#     if len(faces) == 0:
#         return None
    
#     shape = predictor(gray,faces[0])

#     embedding = np.array(face_rec.compute_face_descriptor(image,shape))

#     return embedding
