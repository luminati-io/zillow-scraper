import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ZillowDiscoverPropertiesByUrlCollector:
    """Collects Zillow property data by URLs using the Bright Data API."""

    API_BASE_URL = "https://api.brightdata.com/datasets/v3"
    DATASET_ID = "gd_lfqkr8wm13ixtbd8f5"  # Dataset ID for Zillow properties

    def __init__(self, api_token: str):
        """Initialize with API token and headers."""
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def collect_properties(self, urls: List[Dict[str, str]]) -> Optional[bool]:
        """Trigger and monitor property discovery, then save results."""
        start_time = datetime.now()
        logging.info(f"Starting property discovery for {len(urls)} URLs...")

        collection_response = self._trigger_collection(urls)
        if not collection_response or "snapshot_id" not in collection_response:
            logging.error("Failed to initiate property discovery")
            return None

        snapshot_id = collection_response["snapshot_id"]
        last_status = None

        while True:
            status = self._check_status(snapshot_id)
            elapsed = (datetime.now() - start_time).seconds

            if status != last_status:
                if status == "running":
                    logging.info(f"Discovery in progress... ({elapsed}s elapsed)")
                elif status == "ready":
                    logging.info(f"Discovery completed in {elapsed} seconds")
                elif status in ["failed", "error"]:
                    logging.error(f"Discovery failed after {elapsed} seconds")
                    return None
                last_status = status

            if status == "ready":
                properties_data = self._fetch_data(snapshot_id)
                if properties_data:
                    self._save_data(properties_data)
                    logging.info("Data saved successfully")
                    return True
            elif status in ["failed", "error"]:
                return None

            time.sleep(5)

    def _trigger_collection(
        self, urls: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Trigger property discovery for the given URLs."""
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/trigger",
                headers=self.headers,
                params={
                    "dataset_id": self.DATASET_ID,
                    "include_errors": "true",
                    "type": "discover_new",
                    "discover_by": "url",
                },
                json=urls,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API error during collection trigger: {str(e)}")
            return None

    def _check_status(self, snapshot_id: str) -> Optional[str]:
        """Check the status of the property discovery process."""
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/progress/{snapshot_id}",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("status")
        except requests.exceptions.RequestException as e:
            logging.error(f"API error during status check: {str(e)}")
            return "error"

    def _fetch_data(self, snapshot_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch discovered property data once the snapshot is ready."""
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/snapshot/{snapshot_id}",
                headers=self.headers,
                params={"format": "json"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API error during data fetch: {str(e)}")
            return None

    def _save_data(
        self,
        data: List[Dict[str, Any]],
        filename: str = "zillow_discovered_properties_by_url.json",
    ) -> None:
        """Save discovered property data to a JSON file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")


def main() -> None:
    """Run the Zillow property discovery process with sample URLs."""
    api_token = "API_TOKEN"  # Replace with your actual API token
    collector = ZillowDiscoverPropertiesByUrlCollector(api_token)

    urls = [
        {
            "url": "https://www.zillow.com/south-bend-in/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-86.28027395481374%2C%22east%22%3A-86.21281103367116%2C%22south%22%3A41.6786743836223%2C%22north%22%3A41.717895122883554%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A20555%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isEntirePlaceForRent%22%3Atrue%2C%22isRoomForRent%22%3Afalse%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A14%7D"
        },
        {
            "url": "https://www.zillow.com/new-york-ny/rentals/?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22north%22%3A41.00895254824248%2C%22south%22%3A40.385290931417714%2C%22east%22%3A-73.48529623437503%2C%22west%22%3A-74.47406576562503%7D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22priorityscore%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22r4re%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A2000%7D%2C%22price%22%3A%7B%22max%22%3A392622%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22New%20York%20NY%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A6181%2C%22regionType%22%3A6%7D%5D%2C%22pagination%22%3A%7B%7D%7D"
        },
        {
            "url": "https://www.zillow.com/sands-point-ny/rentals/?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22north%22%3A40.89192762223818%2C%22south%22%3A40.814151726283534%2C%22east%22%3A-73.64006390429687%2C%22west%22%3A-73.76366009570312%7D%2C%22filterState%22%3A%7B%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A9000%2C%22min%22%3A200%7D%2C%22price%22%3A%7B%22max%22%3A1766800%2C%22min%22%3A39262%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22r4r%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22Sands%20Point%20NY%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16387%2C%22regionType%22%3A6%7D%5D%2C%22mapZoom%22%3A13%2C%22pagination%22%3A%7B%7D%7D"
        },
    ]

    collector.collect_properties(urls)


if __name__ == "__main__":
    main()