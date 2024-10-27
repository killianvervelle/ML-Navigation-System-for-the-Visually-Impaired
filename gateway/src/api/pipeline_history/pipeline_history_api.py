from uuid import uuid4
from datetime import datetime
from models.models import *
import base64
from PIL import Image
import io
from envs import *
from pymongo import MongoClient
from io import BytesIO
from fastapi import UploadFile

class PipelineHistoryAPI:
    def __init__(self) -> None:
        self.history = []
        self.image_resize = 300
        self.mongo_client = MongoClient(HOST_MONGODB)
        self.mongo_collection = self.mongo_client["public"]["history"]
        self.mongo_collection.create_index(
            "pipeline_id",
            unique=True
        )

    def get_history(self):
        history = []
        for document in self.mongo_collection.find().limit(10).sort("date", -1):
            history.append(PipelineHistory.parse_obj(document))
        return history
        

    async def create_history(self, image: UploadFile, mode: Mode, additional_inputs: dict = {}) -> str:
        pipeline_id = str(uuid4())
        pipeline_history = PipelineHistory(
            pipeline_id=pipeline_id,
            mode=mode,
            date=datetime.now(),
            image=await self.image_to_base64_url(image.file),
            additional_inputs=additional_inputs
        )
        self.mongo_collection.insert_one(pipeline_history.dict())
        return pipeline_id

    async def add_steps_history(self, pipeline_id: str, step_name: str, result: any, error: bool = False):
        if isinstance(result, BytesIO):
            result = await self.image_to_base64_url(result)
        pipelineHistoryStep = PipelineHistoryStep(step_name=step_name, result=str(result), error=error)
        self.mongo_collection.update_one({
            "pipeline_id": pipeline_id
        },
        {
            "$push": {
                "steps": pipelineHistoryStep.dict()
            }
        })
        
    def mark_history_as_completed(self, pipeline_id: str):
        self.mongo_collection.update_one({
            "pipeline_id": pipeline_id
        },
        {
            "$set": {
                "completed": True
            }
        })        
    
    async def image_to_base64_url(self, image: BytesIO):
        img = Image.open(image)
        img.thumbnail((img.width * self.image_resize // img.height, self.image_resize))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{base64_image}"
