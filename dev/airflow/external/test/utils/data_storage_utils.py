import logging
import os
import io
import json
import boto3
from dev.airflow.external.test.utils.path_utils import generate_storage_path
from dev.airflow.external.test.utils.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET_NAME,
)


def save_data(
    data, data_layer, data_origin, data_category, file_name, storage_mode="minio"
):
    """
    데이터를 MinIO 또는 로컬에 저장하는 함수.

    Args:
        data (dict): 저장할 데이터
        data_layer (str): 데이터 계층 (예: "bronze", "silver", "gold")
        data_origin (str): 데이터 출처 (예: "steam")
        data_category (str): 데이터 카테고리 (예: "players")
        file_name (str): 저장할 파일명 (예: "players_2025-02-18_10-45-30.json")
        storage_mode (str): "minio" 또는 "local" (기본값: "minio")
    """
    dir_path = generate_storage_path(data_layer, data_origin, data_category, "data")
    key = dir_path + file_name

    if storage_mode == "minio":
        upload_to_minio(data, key)
    else:
        save_to_local(data, key)


def save_to_local(data, key, ext="json"):
    local_path = f"./dev/{key}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    if ext == "json":
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    elif ext == "parquet":
        import pandas as pd

        df = pd.DataFrame(data)
        df.to_parquet(local_path, index=False)

    logging.info(f"Successfully saved data locally: {local_path}")


def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="ap-northeast-2",
        use_ssl=False,
    )


def upload_to_minio(data, key):
    try:
        json_data = json.dumps(data, indent=4)
        buffer = io.BytesIO(json_data.encode('utf-8'))
        minio_client = get_minio_client()
        minio_client.upload_fileobj(buffer, MINIO_BUCKET_NAME, key)
        logging.info(f"Successfully uploaded data to MinIO with key: {key}")
    except Exception as e:
        logging.error(f"Failed to upload to MinIO (key: {key}): {e}")


# MinIO에서 appids.json 다운로드
# 현재 appids.json에 있는 앱의 데이터만 수집 중
def download_from_minio(key):
    try:
        logging.info(
            f"Attempting to download from MinIO - Bucket: {MINIO_BUCKET_NAME}, Key: {key}"
        )
        minio_client = get_minio_client()
        response = minio_client.get_object(Bucket=MINIO_BUCKET_NAME, Key=key)
        data = json.loads(response['Body'].read())

        if not isinstance(data, list):
            logging.error("Invalid JSON format. Expected a list of objects.")
            return []

        logging.info(
            f"Successfully downloaded from MinIO - Bucket: {MINIO_BUCKET_NAME}, Key: {key}"
        )
        return [entry["appid"] for entry in data if "appid" in entry]

    except Exception as e:
        logging.error(
            f"Failed to download from MinIO - Bucket: {MINIO_BUCKET_NAME}, Key: {key}, Error: {e}"
        )
        return []
