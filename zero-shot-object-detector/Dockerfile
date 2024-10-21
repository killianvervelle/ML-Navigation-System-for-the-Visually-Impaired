FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
WORKDIR /app

ADD https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth weights/groundingdino_swinb_cogcoor.pth

RUN apt-get update && apt-get install gcc -y

RUN pip install groundingdino-py

COPY src/requirements.txt .
RUN pip install -r requirements.txt

COPY src .

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "main:app", "--port", "8000"]