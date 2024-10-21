FROM python:3.10-alpine

# Installing FastAPI
WORKDIR /app
COPY svc/requirements.txt .
RUN pip install -r requirements.txt 

ADD svc .

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "main:app", "--port", "8000"]