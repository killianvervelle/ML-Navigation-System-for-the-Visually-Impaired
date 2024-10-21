from fastapi import FastAPI, APIRouter, UploadFile 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from api.grounding_dino import ObjectDetector

# Imports required by the service's model
from PIL import Image

#Constants
api_description = """
This microservice take a picture in input. The output of this microservice is a string with the bus number and the destination.
"""

app = FastAPI(
    title="VisionAid Zero Shot Object Detector API",
    description=api_description,
    version="0.0.1",
    openapi_url=f"/specification",
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

router = APIRouter()
object_detector = ObjectDetector()

@router.post("/process")
def process(file: UploadFile, prompt: str):
    image = Image.open(file.file).convert("RGB")
    object = object_detector.predict(image, prompt)

    return {
        'result': object
    }

app.include_router(router)
Instrumentator().instrument(app).expose(app)
