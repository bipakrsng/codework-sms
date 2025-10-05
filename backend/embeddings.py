# import dlib
# import numpy as np
# import cv2
# import os

# #print(f"directory of present file {os.path.dirname(__file__)}")
# model_path = os.path.join(os.path.dirname(__file__),'api\shape_predictor_5_face_landmarks.dat',)
# model_path2 = os.path.join(os.path.dirname(__file__),'api\dlib_face_recognition_resnet_model_v1.dat')


# #print(f"first model path {model_path}")
# #print(f"second model path {model_path2}")
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor(model_path)
# face_rec = dlib.face_recognition_model_v1(model_path2)


# def get_face_embedding(image):
#     try:
#         print("---- DEBUG START ----")
#         print(f"Input type: {type(image)}")
#         print(f"Input dtype: {image.dtype if isinstance(image, np.ndarray) else 'N/A'}")
#         print(f"Input shape: {image.shape if isinstance(image, np.ndarray) else 'N/A'}")

#         # Ensure uint8
#         if image.dtype != np.uint8:
#             print("Converting to uint8")
#             image = image.astype(np.uint8)

#         # Ensure 3 channels (BGR)
#         if len(image.shape) == 2:  
#             print("Image is grayscale already")
#             gray = image
#         elif len(image.shape) == 3:
#             if image.shape[2] == 3:
#                 print("Converting BGR → GRAY")
#                 gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#                 gray = np.ascontiguousarray(gray)
#             elif image.shape[2] == 4:
#                 print("Image has alpha channel, converting BGRA → GRAY")
#                 bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
#                 gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
#             else:
#                 raise ValueError(f"Unsupported channel count: {image.shape[2]}")
#         else:
#             raise ValueError("Invalid image shape")

#         print(f"Gray image dtype: {gray.dtype}, shape: {gray.shape}")

#         # Run detector
#         faces = detector(gray)
#         print(f"Faces detected: {len(faces)}")
#         if len(faces) == 0:
#             return None

#         shape = predictor(gray, faces[0])
#         embedding = np.array(face_rec.compute_face_descriptor(image, shape))

#         print("---- DEBUG END ----")
#         return embedding
#     except Exception as e:
#         print(f" ERROR in get_face_embedding: {e}")
#         import traceback; traceback.print_exc()
#         return None

# embeddings.py - uses facenet-pytorch (MTCNN + InceptionResnetV1)
import io, base64, json
import numpy as np
from PIL import Image
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN

# device config
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# singletons loaded once
mtcnn = MTCNN(keep_all=False, device=device)          # detects and crops face
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)  # embedding model

def pil_from_base64(b64_string):
    """
    Accepts "data:image/png;base64,..." or raw base64 string.
    Returns PIL.Image RGB
    """
    header_removed = b64_string.split(',')[1] if ',' in b64_string else b64_string
    img_data = base64.b64decode(header_removed)
    return Image.open(io.BytesIO(img_data)).convert('RGB')

def get_embedding_from_pil(pil_img):
    """
    Input: PIL.Image (RGB)
    Output: 1-D numpy array (L2-normalized) or None if no face
    """
    # mtcnn returns a tensor cropped to face (3,160,160) or None
    face_tensor = mtcnn(pil_img)  # returns tensor or None
    if face_tensor is None:
        return None
    # if single face, ensure batch dim
    if face_tensor.ndim == 3:
        face_tensor = face_tensor.unsqueeze(0)
    face_tensor = face_tensor.to(device)
    with torch.no_grad():
        emb = resnet(face_tensor)   # shape (1, 512)
    emb_np = emb.cpu().numpy().reshape(-1)
    # L2 normalize
    norm = np.linalg.norm(emb_np)
    if norm > 0:
        emb_np = emb_np / norm
    return emb_np

def get_embedding_from_base64(b64_string):
    pil = pil_from_base64(b64_string)
    return get_embedding_from_pil(pil)
