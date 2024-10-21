import envs
from fastapi import FastAPI, APIRouter, UploadFile 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# Imports required by the service's model
import numpy as np
from donut import DonutModel
from PIL import Image

#Constants
api_description = """
This microservice take a picture in input. The output of this microservice is a string with the bus number and the destination.
"""

app = FastAPI(
    title="VisionAid Bus Screen Text Detector API",
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


pretrained_model = DonutModel.from_pretrained("./model/exp1")
pretrained_model.eval()

task_prompt = f"<s_3_dataset>"

def get_text_output(input_img):
    return pretrained_model.inference(image=input_img, prompt=task_prompt)["predictions"][0]


@router.post("/process")
def image_to_data(file: UploadFile):
        image = Image.open(file.file)
        res = get_text_output(image)
        return JSONResponse({
                "result": res
    })

app.include_router(router)
Instrumentator().instrument(app).expose(app)