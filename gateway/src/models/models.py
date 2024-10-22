from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Mode(str, Enum):
    DESCRIPTION = "description"
    BUS = "bus"
    TRACKING = "tracking"

class ResponseOut(BaseModel):
    result: str

class PipelineHistoryStep(BaseModel):
    error: bool
    step_name: str
    result: str

class PipelineHistory(BaseModel):
    pipeline_id: str
    image: str
    date: datetime
    mode: Mode
    additional_inputs: dict = {}
    steps: list[PipelineHistoryStep] = []
    completed: bool = False