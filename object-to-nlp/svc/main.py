from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import openai
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
import os
from fastapi.encoders import jsonable_encoder

from typing import Optional
from prometheus_fastapi_instrumentator.metrics import Info
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import metrics


# *****************************************************************************
#                  Some global constants and variables
# *****************************************************************************


NAME = 'Object_NLP'
VERSION = '1.1.0'
DESCRIPTION = 'Object to NLP microservice'
openai.api_key = os.getenv("OPENAI_API_KEY")


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

class Bbox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ImageElements(BaseModel):
    class_name: str = Field(..., alias='class')
    bbox: Bbox

class BusData(BaseModel):
    bus_number: Optional[str] = Field("", alias="busNumber", )
    bus_destination: Optional[list[str] | str] = Field("", alias="busDestination")

class TrackingImageElement(BaseModel):
    item: str
    position: Bbox

class ResponseModel(BaseModel):
    result: str

# *****************************************************************************
#                  Service's routes
# *****************************************************************************



openia_total_spent_metric = Counter(
        "openai_spent_total",
        "Total amount in $ used",
        labelnames=("mode",)
)

openia_total_tokens_metric = Counter(
        "openai_used_tokens_total",
        "The number of tokens that have been used",
        labelnames=("mode",)
)

def describe_tracking(image_elements):
    prompt = f"""You are an assistant that help blind people to find a certain object.
    You take in input a JSON that contains the name of the item, and its bounding box. The bounding box are values normalized between 0 and 1.
    You give very short and concise phrases. You give the general direction of the object.
    Here is some examples of outputs:
    - The bounding box is on the left: The {{item}} is on the left.
    - The bounding box is on the right: The {{item}} is on the right.
    - The bounding box is on the center: The {{item}} is straight ahead.
    """

    return prompt, str(jsonable_encoder(image_elements))

def describe_scene(image_elements):
    # Example of request:  curl -X POST -H "Content-Type: application/json" -d '{"class": "bus", "score": 0.9, "bbox": {"x1": 20, "y1": 20, "x2": 80, "y2": 80}}' http://localhost:8000/process/
    prompt = f"""You are an assistant that help blind people to be able to know what is nearby.
    You take in input a JSON that contains the class of an object detected in a picture, and its bounding box. The bounding boxes are normalized between 0 and 1.
    You give very short and concise phrases. An example of output would be: There is a cat on the left, and a dog on the right."""

    return prompt, str(jsonable_encoder(image_elements))

def describe_bus(bus_data):
    prompt = f"""You are an assistant that help blind people to be able to know what is nearby.
    You take in input a JSON that contains the bus number and the bus direction. You tell the user what bus is detected and to which direction.
    The output may only contain one of the two elements, for example only the bus destination or the bus number.

    You give very short and concise phrases. Example of outputs would be:
    - busDestination and busNumber present: There is the bus number 20 headed to Romont.
    - Only busNumber present: There is the bus number 13.
    - Only busDestination present: There is the bus headed to Fribourg."""

    return prompt, str(jsonable_encoder(bus_data))

@app.post('/process')
def task_gpt(input_data: list[ImageElements] | TrackingImageElement | BusData):


    prompt = str_input = ""
    mode = ""

    if isinstance(input_data, list):
        prompt, str_input = describe_scene(input_data)
        mode = "description"
    elif isinstance(input_data, TrackingImageElement):
        prompt, str_input = describe_tracking(input_data)
        mode = "tracking"
    else:
        prompt, str_input = describe_bus(input_data)
        mode = "bus"

    print(prompt, str_input)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str_input}
        ]
    )
    
    print(f"Request price: {response.usage.total_tokens / 1000 * 0.002}$")
    openia_total_spent_metric.labels(mode).inc(response.usage.total_tokens / 1000 * 0.002)
    openia_total_tokens_metric.labels(mode).inc(response.usage.total_tokens)

    return ResponseModel(result=response.choices[0].message.content)


Instrumentator().instrument(app).expose(app)
