from abc import ABC, abstractmethod
from typing import Callable
from fastapi import UploadFile
from uuid import uuid4
from .pipeline_history_api import PipelineHistoryAPI
from models.models import *

class ServerChainingException(Exception):
    pass

class ParameterChainingException(Exception):
    def __init__(self, *args: object) -> None:        
        super().__init__(f"Pipeline has stopped prematurely in step {args[0]}: {args[1]}", args[0], args[1])

class MicroService(ABC):
    name: str
    url: str


    @abstractmethod
    async def run_microservice(self, pipeline_history_api, input: any) -> any:
        pass

    async def _manage_request(self, request):
        try:
            request_response = await request;
        except Exception as e:
            raise ServerChainingException(f"Error in step {self.name}: {e.args[0]}", self.name, e.args[0])
                
        if request_response.status_code != 200:
            raise ServerChainingException(f"Error in step {self.name}: {request_response.text}", self.name, request_response.text)
        
        return request_response
    
    def _get_image_to_httpx(self, image: UploadFile, param_name: str):
        return {
			param_name: (
				image.filename,
				image.file,
				image.content_type
				)
			}

class Element(ABC):

    @abstractmethod
    async def run_pipeline_element(self, pipeline_history_api, pipeline_id, param: any, additional_params: dict):
        pass
    


class PipelineElement(Element):
    microservice: MicroService
    passthrough: bool = False
    report_error: bool = True
    error_name: str
    result_check: Callable[[any], bool]


    def __init__(self, microservice, error_name="", result_check=lambda _: True, passthrough=False) -> None:
        super().__init__()
        self.microservice = microservice
        self.result_check = result_check
        self.error_name = error_name
        self.passthrough = passthrough

    async def run_pipeline_element(self, pipeline_history_api, pipeline_id, param, _):
        result = None
        
        result = await self.microservice.run_microservice(param)

        initial_result = result

        if not self.result_check(result):
            raise ParameterChainingException(self.microservice.name, self.error_name)


        if self.passthrough:
            result = param

        await pipeline_history_api.add_steps_history(pipeline_id, self.microservice.name, initial_result)

        return result, initial_result

    
class ConditionalPipelineElement(Element):
    init_pipeline_element: Element
    result_check: Callable[[any], bool]
    failed_passthrough: bool
    success_passthrough: bool
    failed_pipeline_elements: list[Element]
    success_pipeline_elements: list[Element]
    
    def __init__(
            self, 
            init_pipeline_element,
            result_check,
            failed_pipeline_elements,
            success_pipeline_elements, 
            failed_passthrough=False, 
            success_passthrough=False
        ) -> None:
        super().__init__()
        self.init_pipeline_element = init_pipeline_element
        self.result_check = result_check
        self.failed_pipeline_elements = failed_pipeline_elements
        self.success_pipeline_elements = success_pipeline_elements
        self.failed_passthrough = failed_passthrough,
        self.success_passthrough = success_passthrough


    async def run_pipeline_element(self, pipeline_history_api, pipeline_id, param, additional_params: dict):
        self.init_pipeline_element.report_error = False
        
        result, initial_result = await self.init_pipeline_element.run_pipeline_element(pipeline_history_api, pipeline_id, param, additional_params)

        success = self.result_check(initial_result)

        next_pipeline_elements = self.success_pipeline_elements if success else self.failed_pipeline_elements 
        
        previous_response = param if (self.failed_passthrough and not success) or (self.success_passthrough and success) else result

        for element in next_pipeline_elements:
            previous_response, _ = await element.run_pipeline_element(pipeline_history_api, pipeline_id, previous_response, additional_params)


        return previous_response, None

class MultiParamInputTransformer(Element):
    pipeline_element: Element
    additional_params_names: list[str]

    def __init__(self, pipeline_element: Element, additional_params_names: list[str]) -> None:
        super().__init__()
        self.pipeline_element = pipeline_element
        self.additional_params_names = additional_params_names

    async def run_pipeline_element(self, pipeline_history_api, pipeline_id, param: any, additional_params: dict):
        new_param = [param]
        for name in self.additional_params_names:
            new_param.append(additional_params[name])

        return await self.pipeline_element.run_pipeline_element(pipeline_history_api, pipeline_id, new_param, additional_params)


class Pipeline:
    elements: list[Element]
    pipeline_history_api: PipelineHistoryAPI
    mode: Mode

    def __init__(self, pipeline_history_api, mode, elements) -> None:
        self.pipeline_history_api = pipeline_history_api
        self.mode = mode
        self.elements = elements

    async def run_pipeline(self, initial_param: any, additional_params: dict = {}) -> any:
        pipeline_id = await self.pipeline_history_api.create_history(initial_param, self.mode, additional_params)

        previous_param = initial_param

        for element in self.elements:
            try:
                previous_param, _ = await element.run_pipeline_element(self.pipeline_history_api, pipeline_id, previous_param, additional_params)
            except ParameterChainingException as e:
                await self.pipeline_history_api.add_steps_history(pipeline_id, e.args[1], e.args[0])
                raise e
            except ServerChainingException as e:
                await self.pipeline_history_api.add_steps_history(pipeline_id, e.args[1], e.args[0], error=True)
                raise e

        self.pipeline_history_api.mark_history_as_completed(pipeline_id)

        return previous_param