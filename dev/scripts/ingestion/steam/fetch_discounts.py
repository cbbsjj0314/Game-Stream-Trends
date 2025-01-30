import logging
import json
import os
import requests
from datetime import datetime

DATA_TYPE = "discounts"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
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


def load_app_ids(file_path):
    if not os.path.exists(file_path):
        logging.warning(f"Test file not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        appids_data = json.load(f)

    if not isinstance(appids_data, list):
        logging.error("Invalid JSON format. Expected a list of objects.")
        return []

    return [entry["appid"] for entry in appids_data if "appid" in entry]


def save_discount_data(output_dir, idx, data):
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = f"{output_dir}/combined_{DATA_TYPE}_{idx}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    logging.info(f"Discount data for chunk {idx} saved to: {output_file}")


def process_discounts(file_path, output_dir):
    appids = load_app_ids(file_path)

    if not appids:
        logging.error("No valid appids available to fetch discounts.")
        return

    chunked_appids = list(chunk_list(appids, 1000))

    for idx, chunk in enumerate(chunked_appids, start=1):
        combined_discounts = get_discount_data(chunk)

        if combined_discounts:
            save_discount_data(output_dir, idx, combined_discounts)
        else:
            logging.error(f"Failed to fetch data for chunk {idx}.")


if __name__ == "__main__":
    process_discounts("dev/data/sample/app_ids.json", "dev/data/output/")
