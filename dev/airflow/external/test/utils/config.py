import os
from dotenv import load_dotenv
from airflow.models import Variable

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT") or Variable.get(
    "MINIO_ENDPOINT", default_var=""
)
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY") or Variable.get(
    "MINIO_ACCESS_KEY", default_var=""
)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY") or Variable.get(
    "MINIO_SECRET_KEY", default_var=""
)
MINIO_BUCKET_NAME = os.getenv("GST_BUCKET_NAME") or Variable.get(
    "GST_BUCKET_NAME", default_var=""
)
