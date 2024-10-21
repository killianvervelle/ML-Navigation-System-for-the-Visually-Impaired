import envs
from fastapi import FastAPI, APIRouter, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

# Imports required by the service's model
import cv2
import numpy as np

#Constants
api_description = """
This microservice take a picture in input.  The output of this microservice is the input picture and a boolean. 
    True if the picture is usable (no blur) or false if the picture is not usable (blur)
"""
THRESHOLD = 140


app = FastAPI(
    title="VisionAid Photo Validator API",
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

class ResponseModel(BaseModel):
    result: bool


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def is_image_valid(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    return bool(fm >= THRESHOLD)


@router.post("/process", response_model=ResponseModel)
def image_to_data(file: UploadFile):
    image = cv2.imdecode(np.frombuffer(file.file.read(), np.uint8), 1)
    return ResponseModel(result=is_image_valid(image)) 

app.include_router(router)
Instrumentator().instrument(app).expose(app)

