# 할인 정보를 가져오는데 통화 기준은 한국임
# 다른 나라 통화로도 수정 가능

import logging
import requests
from dev.lib.minio_utils import MinIOConfig
from dev.lib.config import get_current_time

DATA_TYPE = "discounts"
MinIOConfig.setup_minio_logging(
    bucket_name=MinIOConfig.MINIO_BUCKET_NAME, data_type=DATA_TYPE
)


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def get_discount_data(appids_chunk):
    appids_str = ",".join(map(str, appids_chunk))
    url = f"https://store.steampowered.com/api/appdetails?appids={appids_str}&filters=price_overview"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch discount data for appids chunk: {e}")
        return None


def main():
    try:
        appids_data = MinIOConfig.download_from_minio(
            'data/raw/steam/app-list/appids.json'
        )
        if not appids_data or "steam_app_ids" not in appids_data:
            logging.error("No valid appids available to fetch discounts.")
            return

        appids = appids_data["steam_app_ids"]
        chunked_appids = list(chunk_list(appids, 1000))

        for idx, chunk in enumerate(chunked_appids, start=1):
            combined_discounts = get_discount_data(chunk)

            if combined_discounts:
                date_str = get_current_time().strftime('%Y-%m-%d')
                timestamp = get_current_time().strftime('%Y-%m-%d_%H-%M-%S')
                chunk_key = f'data/raw/steam/{DATA_TYPE}/{date_str}/combined_{DATA_TYPE}_{idx}_{timestamp}.json'
                MinIOConfig.upload_to_minio(combined_discounts, chunk_key)
                logging.info(
                    f"Discount data for chunk {idx} uploaded to MinIO: {chunk_key}"
                )
            else:
                logging.error(f"Failed to fetch or upload data for chunk {idx}.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
