import envs
from fastapi import FastAPI, APIRouter, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# Imports required by the service's model
import cv2
import torch
import numpy as np

#Constants
api_description = """
This microservice take a picture in input.  The output of this microservice is 0 to 1 cropped picture of the bus screen
"""

app = FastAPI(
    title="VisionAid Bus Screen Cropper API",
    description=api_description,
    version="0.0.1",
    openapi_url=f"{envs.URL_PREFIX}/specification",
    #root_path=envs.URL_PREFIX,
    routes=[
        
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    prefix=envs.URL_PREFIX
)


model_name = 'best.pt'
PATH='./weights/' + model_name
model = torch.hub.load('ultralytics/yolov5', 'custom', path=PATH)  # load the model only one time!
model.conf = 0.5  # NMS confidence threshold
model.iou = 0.5  # NMS IoU threshold

def image_preprocessing(image):
    return image[:, :, ::-1],

def get_best_screen(image):
    image = image_preprocessing(image)

    preds = model(image)
    crops = preds.crop(save=False)
    best_confidence = 0
    best_im = []
    for crop in crops:
        if crop['conf'] > best_confidence:
            best_im = crop['im']
            best_confidence = crop['conf']
    return best_im

@router.post("/process",responses = {
        200: {
            "content": {"image/png": {}}
        }
    },
    response_class=Response
)
def image_to_data(file: UploadFile):
    image = cv2.imdecode(np.frombuffer(file.file.read(), np.uint8), 1)
    res = get_best_screen(image)
    if len(res) == 0:
        print("0 screen found")
        return None
    else:
        im_buf_arr = np.array(cv2.imencode(".png", res)[1])
        return Response(content=im_buf_arr.tobytes(), media_type="image/png")

app.include_router(router)
Instrumentator().instrument(app).expose(app)
