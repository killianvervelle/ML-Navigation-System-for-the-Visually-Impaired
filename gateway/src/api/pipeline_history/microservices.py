from envs import *
import httpx
from .pipeline_models import MicroService
from io import BytesIO
from api.minio_controller import MinioController
from concurrent.futures import ThreadPoolExecutor


class PhotoValidatorMicroService(MicroService):
    name = "photo-validator"
    url = URL_PHOTO_VALIDATOR
    
    async def run_microservice(self, input: any) -> any:
        response = None
        async with httpx.AsyncClient() as client:
            response = await self._manage_request(client.post(f"{self.url}/process", files=self._get_image_to_httpx(input, "file")))
        return response.json()["result"]

class ObjectDetectorMicroService(MicroService):
    name = "object-detector"
    url = URL_OBJECT_DETECTOR

    async def run_microservice(self, input: any) -> any:
        response = None
        async with httpx.AsyncClient() as client:
            response = await self._manage_request(client.post(f"{self.url}/process", files=self._get_image_to_httpx(input, "file")))
        return response.json()["result"]
    
class ObjectToNLPMicroService(MicroService):
    name = "object-to-nlp"
    url = URL_OBJECT_TO_NLP

    async def run_microservice(self, input: any) -> any:
        response = None
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await self._manage_request(client.post(f"{self.url}/process", json=input))  
        return response.json()["result"]
    
class BusScreenCropperMicroService(MicroService):
    name = "bus-screen-cropper"
    url = URL_BUS_SCREEN_CROPPER

    def __init__(self) -> None:
        super().__init__()
        self.minio_ctrl = MinioController()

    async def run_microservice(self, input: any) -> any:
        response = None
        async with httpx.AsyncClient() as client:
            response = await self._manage_request(client.post(f"{self.url}/process", files=self._get_image_to_httpx(input, "file")))
            ThreadPoolExecutor().submit(self.minio_ctrl.image_upload, response.content)
        return BytesIO(response.content)

class BusScreenTextDetectorMicroService(MicroService):
    name = "bus-screen-text-detector"
    url = URL_BUS_SCREEN_TEXT_DETECTOR

    async def run_microservice(self, input: any) -> any:
        response = None
        async with httpx.AsyncClient() as client:
            response = await self._manage_request(client.post(f"{self.url}/process", files={
			"file": (
				"image.png",
				input,
				"image/png"
				)
			}))
        return response.json()["result"]
    
class ZeroShotObjectDetectorMicroService(MicroService):
    name = "zero-shot-object-detector"
    url = URL_ZERO_SHOT_OBJECT_DETECTOR

    async def run_microservice(self, input: any) -> any:
        response = None
        async with httpx.AsyncClient() as client:
            response = await self._manage_request(
                client.post(
                    f"{self.url}/process", files=self._get_image_to_httpx(input[0], "file"),
                    params={
                        "prompt": input[1]
                    }
                )
            )
        return response.json()["result"]