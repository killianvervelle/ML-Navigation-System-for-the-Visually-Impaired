FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

WORKDIR /app

# Copy Model
COPY data/4_models/train_bus/exp1 ./model/exp1

# Installing FastAPI
#RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY micro-service/src/requirements.txt .
RUN pip install -r requirements.txt 


ADD micro-service/src .

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "main:app", "--port", "8000"]