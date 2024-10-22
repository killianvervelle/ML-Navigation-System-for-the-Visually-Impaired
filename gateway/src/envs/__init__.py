import os
URL_PREFIX: str = os.getenv("URL_PREFIX", "")

# microservices
URL_PHOTO_VALIDATOR: str = os.getenv("URL_PHOTO_VALIDATOR", "http://localhost:8001")
URL_OBJECT_DETECTOR: str = os.getenv("URL_OBJECT_DETECTOR", "http://localhost:8002")
URL_OBJECT_TO_NLP: str = os.getenv("URL_OBJECT_TO_NLP", "http://localhost:8003")
URL_BUS_SCREEN_CROPPER: str = os.getenv("URL_BUS_SCREEN_CROPPER", "http://localhost:8004")
URL_BUS_SCREEN_TEXT_DETECTOR: str = os.getenv("URL_BUS_SCREEN_TEXT_DETECTOR", "http://localhost:8005")
URL_ZERO_SHOT_OBJECT_DETECTOR: str = os.getenv("URL_ZERO_SHOT_OBJECT_DETECTOR", "http://localhost:8006")


HOST_MONGODB: str = os.getenv("HOST_MONGODB", "mongodb://localhost:27017")

MINIO_HOSTNAME: str = os.getenv("MINIO_HOSTNAME", "localhost:9000")
MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "ROOT")
MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "ROOTROOT")
MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "pi-aimarket-visionaid")
MINIO_BUCKET_PREFIX: str = os.getenv("MINIO_FOLDER", "bus-screen-text-detector/data/1_base_images")