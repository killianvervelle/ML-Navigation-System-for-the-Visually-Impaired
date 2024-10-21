import cv2
import numpy as np
from typing_extensions import Annotated
from fastapi import FastAPI, UploadFile, Query
from starlette.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from predict import Detetron
from pydantic import BaseModel, Field

# *****************************************************************************
#                  Some global constants and variables
# *****************************************************************************


NAME = 'Object_detector'
VERSION = '1.1.0'
DESCRIPTION = 'Detection of objects inside an image. The microservice outputs an array with the name of \
    the classes detected, their scores of relevancy and the coordinates of their respective bounding boxes'

# *****************************************************************************
#                  FastAPI entry point declaration
# *****************************************************************************

app = FastAPI(
    title=NAME,
    description=DESCRIPTION,
    version="0.0.1",
    #openapi_url=f"{envs.URL_PREFIX}/specification",
    #root_path=envs.URL_PREFIX,
    routes=[]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# *****************************************************************************
#                  Service's routes
# *****************************************************************************

class Bbox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ImageElements(BaseModel):
    class_name: str = Field(..., alias='class')
    score: float
    bbox: Bbox

class ResponseModel(BaseModel):
    result: list[ImageElements]

detectron = Detetron()

# Route used to upload images
# ex: curl -F 'file=@./images/bus.jpeg' http://127.0.0.1:8000/process/0.8
@app.post('/process', response_model=ResponseModel)
def load_image(file: UploadFile, thresh_value: Annotated[float, Query(ge=0, le=1)] = 0.75):
    image = cv2.imdecode(np.frombuffer(file.file.read(), np.uint8), 1)
    result = detectron.predict(image, thresh_value)
    print(result)
    return ResponseModel(result=result)

Instrumentator().instrument(app).expose(app)