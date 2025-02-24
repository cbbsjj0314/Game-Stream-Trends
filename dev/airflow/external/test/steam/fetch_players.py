import logging
import asyncio
import aiohttp
from dev.airflow.external.test.utils.config import Config
from dev.airflow.external.test.utils.data_storage_utils import save_data

STORAGE_MODE = "local"
DATA_LAYER = "bronze"
DATA_ORIGIN = "steam"
DATA_CATEGORY = "players"

Config.setup_minio_logging(
    bucket_name=Config.MINIO_BUCKET_NAME, data_type=DATA_CATEGORY
)


async def fetch_app_players_async(session, appid):
    url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            logging.info(f"players for appid {appid} fetched successfully.")
            return appid, data
    except Exception as e:
        logging.error(f"Failed to fetch players for appid {appid}: {e}")
        return appid, None


async def fetch_all_players(appids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_app_players_async(session, appid) for appid in appids]
        results = await asyncio.gather(*tasks)
        return {appid: data for appid, data in results if data}


def main():
    try:
        appids = Config.download_from_minio('data/raw/steam/app-list/appids.json')
        if not appids:
            logging.error("No appids available to fetch players.")
            return

        combined_players = asyncio.run(fetch_all_players(appids))

        if combined_players:
            save_data(
                data=combined_players,
                data_layer=DATA_LAYER,
                data_origin=DATA_ORIGIN,
                data_category=DATA_CATEGORY,
                storage_mode=STORAGE_MODE,
                ext="json",
            )
            logging.info("Combined players data saved successfully.")
        else:
            logging.error("No players data collected to upload.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
