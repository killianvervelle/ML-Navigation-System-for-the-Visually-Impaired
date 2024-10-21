from minio import Minio
from envs import *
import time
from io import BytesIO
from uuid import uuid4

class MinioController:
    def __init__(self):
        self.client = Minio(MINIO_HOSTNAME, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)

    def image_upload(self, file_bytes):
        file = BytesIO(file_bytes)

        image_name = f"auto_{int(round(time.time()))}_{uuid4()}.png"
        print(image_name)

        # Upload the image to MinIO
        self.client.put_object(
            MINIO_BUCKET,
            f"{MINIO_BUCKET_PREFIX}/{image_name}",
            file,
            file.getbuffer().nbytes
        )