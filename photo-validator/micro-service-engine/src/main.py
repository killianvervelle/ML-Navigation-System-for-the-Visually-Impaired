import asyncio
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from common_code.config import get_settings
from pydantic import Field
from common_code.http_client import HttpClient
from common_code.logger.logger import get_logger
from common_code.service.controller import router as service_router
from common_code.service.service import ServiceService
from common_code.storage.service import StorageService
from common_code.tasks.controller import router as tasks_router
from common_code.tasks.service import TasksService
from common_code.tasks.models import TaskData
from common_code.service.models import Service, FieldDescription
from common_code.service.enums import ServiceStatus, FieldDescriptionType

# Imports required by the service's model
from common_code.tasks.service import get_extension
import cv2
import numpy as np
import base64
import json


settings = get_settings()



class MyService(Service):
    """
    This microservice take a picture in input.  The output of this microservice is the input picture and a boolean. 
    True if the picture is usable (no blur) or false if the picture is not usable (blur)
    """

    # Any additional fields must be excluded for Pydantic to work
    model: object = Field(exclude=True)

    THRESHOLD = 140

    def __init__(self):
        super().__init__(
            name="VisionAid Photo Validator",
            slug="visionaid-photo-validator",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            # INPUT AND OUTPUT FIELDS
            data_in_fields=[
                FieldDescription(name="input_json", type=[FieldDescriptionType.APPLICATION_JSON]),
                #FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG])
            ],
            data_out_fields=[
                FieldDescription(name="output_json", type=[FieldDescriptionType.APPLICATION_JSON])
                #FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
                #FieldDescription(name="valid", type=[FieldDescriptionType.TEXT_PLAIN])
            ]
        )
        #The best threshold is 140 with a f1 score of 0.8083069704326786
        

    def variance_of_laplacian(self, image):
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def is_image_valid(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = self.variance_of_laplacian(gray)
        return bool(fm >= self.THRESHOLD)
    

    async def process(self, data):
        # NOTE that the data is a dictionary with the keys being the field names set in the data_in_fields
        raw = data["input_json"]
        
        # Decode the image
        input_dict = json.loads(raw.data)
        image_b64 = input_dict["image"]
        
        img_binary = base64.b64decode(image_b64)
        
        
        img = cv2.imdecode(np.frombuffer(img_binary, np.uint8), 1)

        # Detect Blur
        image_valid = self.is_image_valid(img)  

        # Encode the image with the same format as the input

        # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
        return {
            "output_json": TaskData(
                data=json.dumps({"image": image_b64, "valid": image_valid}),
                type=FieldDescriptionType.APPLICATION_JSON
            )
        }



api_description = """
This microservice take a picture in input.  The output of this microservice is the input picture and a boolean. 
    True if the picture is usable (no blur) or false if the picture is not usable (blur)
"""
api_summary = """
VisionAid Photo Validator
"""

# Define the FastAPI application with information
# TODO: 7. CHANGE THE API TITLE, VERSION, CONTACT AND LICENSE
app = FastAPI(
    title="VisionAid Photo Validator API",
    description=api_description,
    version="0.0.1",
    swagger_ui_parameters={
        "tagsSorter": "alpha",
        "operationsSorter": "method",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0 (GNU AGPLv3)",
        "url": "https://choosealicense.com/licenses/agpl-3.0/",
    },
)

# Include routers from other files
app.include_router(service_router, tags=['Service'])
app.include_router(tasks_router, tags=['Tasks'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)

service_service: ServiceService | None = None


@app.on_event("startup")
async def startup_event():
    # Manual instances because startup events doesn't support Dependency Injection
    # https://github.com/tiangolo/fastapi/issues/2057
    # https://github.com/tiangolo/fastapi/issues/425

    # Global variable
    global service_service

    logger = get_logger(settings)
    http_client = HttpClient()
    storage_service = StorageService(logger)
    my_service = MyService()
    tasks_service = TasksService(logger, settings, http_client, storage_service)
    service_service = ServiceService(logger, settings, http_client, tasks_service)

    tasks_service.set_service(my_service)

    # Start the tasks service
    tasks_service.start()

    async def announce():
        # TODO: enhance this to allow multiple engines to be used
        announced = False

        retries = settings.engine_announce_retries
        while not announced and retries > 0:
            announced = await service_service.announce_service(my_service)
            retries -= 1
            if not announced:
                time.sleep(settings.engine_announce_retry_delay)
                if retries == 0:
                    logger.warning(f"Aborting service announcement after {settings.engine_announce_retries} retries")

    # Announce the service to its engine
    asyncio.ensure_future(announce())


@app.on_event("shutdown")
async def shutdown_event():
    # Global variable
    global service_service
    my_service = MyService()
    await service_service.graceful_shutdown(my_service)
