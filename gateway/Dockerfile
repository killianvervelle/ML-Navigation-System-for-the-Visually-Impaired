FROM python:3.10-slim-bullseye

# Installing FastAPI
WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
ADD src .

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "main:app", "--port", "8000"]