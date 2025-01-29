import json
import io
import logging
from minio import Minio
from airflow.models import Variable
from dev.lib.config import get_current_time


class MinIOConfig:
    MINIO_BUCKET_NAME = Variable.get("GST_BUCKET_NAME")
    MINIO_ENDPOINT = Variable.get("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")

    @staticmethod
    def get_minio_client():
        return Minio(
            endpoint=MinIOConfig.MINIO_ENDPOINT,
            access_key=MinIOConfig.MINIO_ACCESS_KEY,
            secret_key=MinIOConfig.MINIO_SECRET_KEY,
            secure=False,
        )

    @staticmethod
    def download_from_minio(key):
        try:
            logging.info(
                f"Attempting to download from MinIO - Bucket: {MinIOConfig.MINIO_BUCKET_NAME}, Key: {key}"
            )
            minio_client = MinIOConfig.get_minio_client()
            response = minio_client.get_object(MinIOConfig.MINIO_BUCKET_NAME, key)
            data = json.loads(response.read().decode("utf-8"))
            logging.info(
                f"Successfully downloaded from MinIO - Bucket: {MinIOConfig.MINIO_BUCKET_NAME}, Key: {key}"
            )
            return data
        except Exception as e:
            logging.error(
                f"Failed to download from MinIO - Bucket: {MinIOConfig.MINIO_BUCKET_NAME}, Key: {key}, Error: {e}"
            )

    @staticmethod
    def upload_to_minio(data, key):
        try:
            json_data = json.dumps(data, indent=4).encode("utf-8")
            buffer = io.BytesIO(json_data)
            minio_client = MinIOConfig.get_minio_client()
            minio_client.put_object(
                bucket_name=MinIOConfig.MINIO_BUCKET_NAME,
                object_name=key,
                data=buffer,
                length=len(json_data),
                content_type="application/json",
            )
            logging.info(f"Successfully uploaded data to MinIO with key: {key}")
        except Exception as e:
            raise RuntimeError(f"Failed to upload to MinIO (key: {key}): {e}")

    class MinIOLogHandler(logging.Handler):
        def __init__(self, bucket_name, date_str, data_type, buffer_size=10):
            super().__init__()
            self.bucket_name = bucket_name
            self.date_str = date_str
            self.data_type = data_type
            self.buffer_size = buffer_size
            self.log_buffer = io.StringIO()
            self.buffer = []
            self.minio_client = MinIOConfig.get_minio_client()

        def emit(self, record):
            msg = self.format(record)
            self.log_buffer.write(msg + "\n")
            self.buffer.append(record)
            if len(self.buffer) >= self.buffer_size:
                self.flush()

        def flush(self):
            if len(self.buffer) == 0:
                return

            try:
                self._upload_logs_to_minio()
            except Exception as e:
                logging.error(f"Failed to upload logs to MinIO: {e}")
            finally:
                self.log_buffer = io.StringIO()
                self.buffer = []

        def _upload_logs_to_minio(self):
            self.log_buffer.seek(0)
            timestamp = get_current_time().strftime('%Y-%m-%d_%H-%M-%S')
            minio_key = f"logs/steam/{self.data_type}/{self.date_str}/fetch_{self.data_type}_{timestamp}.log"

            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=minio_key,
                data=io.BytesIO(self.log_buffer.getvalue().encode('utf-8')),
                length=len(self.log_buffer.getvalue().encode('utf-8')),
                content_type="text/plain",
            )
            logging.info(f"Logs uploaded to MinIO: {minio_key}")

    @staticmethod
    def setup_minio_logging(
        bucket_name, data_type, buffer_size=1000, log_level=logging.INFO
    ):
        date_str = get_current_time().strftime('%Y-%m-%d')
        log_handler = MinIOConfig.MinIOLogHandler(
            bucket_name, date_str, data_type, buffer_size=buffer_size
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(log_handler)
