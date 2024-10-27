from fastapi import UploadFile
from envs import *
from models.models import *
from .pipeline_history.pipeline_history_api import PipelineHistoryAPI
from .pipeline_history.pipeline_models import *
from .pipeline_history.microservices import *

class Request:
    def __init__(self):
        self.pipeline_history_api = PipelineHistoryAPI()
        pass

    def get_history(self):
        return self.pipeline_history_api.get_history()

    async def run(self, image: UploadFile, mode: Mode):
        response = None
        if mode == Mode.BUS:
            response = await self.run_bus(image)
        elif mode == Mode.DESCRIPTION:
            response = await self.run_description(image)
        return response

    async def run_description(self, image: UploadFile) -> ResponseOut:
        pipeline = Pipeline(
            self.pipeline_history_api,
            Mode.DESCRIPTION, 
            elements=[
                PipelineElement(
                    microservice=PhotoValidatorMicroService(),
                    result_check=lambda result: result,
                    error_name="Photo is blurry",
                    passthrough=True
                ),
                PipelineElement(
                    microservice=ObjectDetectorMicroService(),
                    result_check=lambda result: len(result) != 0,
                    error_name="Array is empty"
                ),
                PipelineElement(
                    microservice=ObjectToNLPMicroService(),
                ),
            ]
        )
        response = await pipeline.run_pipeline(image)
        return ResponseOut(result=response)
    
    async def run_bus(self, image: UploadFile) -> ResponseOut:
        pipeline = Pipeline(
            self.pipeline_history_api,
            Mode.BUS, 
            elements=[
                PipelineElement(
                    microservice=PhotoValidatorMicroService(),
                    result_check=lambda result: result,
                    error_name="Photo is blurry",
                    passthrough=True
                ),
                ConditionalPipelineElement(
                    init_pipeline_element=PipelineElement(
                        microservice=ObjectDetectorMicroService(),
                        result_check=lambda result: len(result) != 0,
                        error_name="No object detected"
                    ),
                    success_passthrough=True,
                    result_check=lambda result: bool(next((x for x in result if x['class'] == 'bus'), None)),
                    failed_pipeline_elements=[],
                    success_pipeline_elements=[
                        PipelineElement(
                            microservice=BusScreenCropperMicroService(),
                            result_check=lambda result: bool(result.read()),
                            error_name="No screen detected"
                        ),
                        PipelineElement(
                            microservice=BusScreenTextDetectorMicroService(),
                            result_check=lambda result: len(result) != 0,
                            error_name="No text detected"
                        )
                    ]    
                ),
                PipelineElement(
                    microservice=ObjectToNLPMicroService(),
                ),
            ]
        )
        response = await pipeline.run_pipeline(image)
        return ResponseOut(result=response)
    
    async def run_tracking(self, image: UploadFile, prompt: str) -> ResponseOut:
        pipeline = Pipeline(
            self.pipeline_history_api,
            Mode.TRACKING, 
            elements=[
                PipelineElement(
                    microservice=PhotoValidatorMicroService(),
                    result_check=lambda result: result,
                    error_name="Photo is blurry",
                    passthrough=True
                ),
                MultiParamInputTransformer(
                    pipeline_element=PipelineElement(
                        microservice=ZeroShotObjectDetectorMicroService(),
                        result_check=lambda result: len(result) != 0,
                        error_name="Item not detected"
                    ),
                    additional_params_names=["prompt"]
                ),
                PipelineElement(
                    microservice=ObjectToNLPMicroService(),
                ),
            ]
        )
        response = await pipeline.run_pipeline(image, {"prompt": prompt})
        return ResponseOut(result=response)

