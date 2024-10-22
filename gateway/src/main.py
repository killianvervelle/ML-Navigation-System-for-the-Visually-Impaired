import envs
from fastapi import FastAPI, APIRouter, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from models.models import *
from api.requests import Request
from api.pipeline_history.pipeline_models import ServerChainingException, ParameterChainingException
from typing import Literal

#Constants
api_description = """
This microservice runs the chaining of the microservices
"""

app = FastAPI(
    title="VisionAid Gateway API",
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

app.add_middleware(GZipMiddleware, minimum_size=1000)

router = APIRouter(
    prefix=envs.URL_PREFIX
)

request = Request()

@router.post("/process", response_model=ResponseOut)
async def process(image: UploadFile, mode: Literal[Mode.BUS, Mode.DESCRIPTION]):
    response = None

    try:
        response = await request.run(image, mode)
    except ServerChainingException as e:
        raise HTTPException(status_code=500, detail=e.args[0])
    except ParameterChainingException as e:
        raise HTTPException(status_code=422, detail=e.args[0])
    
    return response

@router.post("/process-tracking", response_model=ResponseOut)
async def process_tracking(image: UploadFile, prompt: str):
    response = None

    try:
        response = await request.run_tracking(image, prompt)
    except ServerChainingException as e:
        raise HTTPException(status_code=500, detail=e.args[0])
    except ParameterChainingException as e:
        raise HTTPException(status_code=422, detail=e.args[0])
    
    return response

@router.get("/pipelines-history", response_model=list[PipelineHistory])
async def pipeline_history():
    return request.get_history()


app.include_router(router)
#Prometheus instrumentator for metrics tracking
Instrumentator().instrument(app).expose(app)

