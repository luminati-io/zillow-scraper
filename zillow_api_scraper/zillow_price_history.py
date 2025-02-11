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


class ZillowPriceHistoryCollector:
    """Collects Zillow price history data using the Bright Data API."""

    API_BASE_URL = "https://api.brightdata.com/datasets/v3"
    DATASET_ID = "gd_lxu1cz9r88uiqsosl"  # Dataset ID for Zillow price history
    COLLECTION_TIMEOUT = 600  # Timeout for collection process in seconds

    def __init__(self, api_token: str):
        """Initialize with API token and headers."""
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def collect_price_history(self, urls: List[Dict[str, str]]) -> Optional[bool]:
        """Trigger and monitor price history collection, then save results."""
        start_time = datetime.now()
        logging.info(f"Starting price history collection for {len(urls)} URLs...")

        collection_response = self._trigger_collection(urls)
        if not collection_response or "snapshot_id" not in collection_response:
            logging.error("Failed to initiate price history collection")
            return None

        snapshot_id = collection_response["snapshot_id"]
        last_status = None

        while True:
            status = self._check_status(snapshot_id)
            elapsed = (datetime.now() - start_time).seconds

            if status != last_status:
                if status == "running":
                    logging.info(f"Collection in progress... ({elapsed}s elapsed)")
                elif status == "ready":
                    logging.info(f"Collection completed in {elapsed} seconds")
                elif status in ["failed", "error"]:
                    logging.error(f"Collection failed after {elapsed} seconds")
                    return None
                last_status = status

            if status == "ready":
                data = self._fetch_data(snapshot_id)
                if data:
                    self._save_data(data)
                    logging.info("Data saved successfully")
                    return True
            elif status in ["failed", "error"]:
                return None

            time.sleep(5)

    def _trigger_collection(
        self, urls: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Trigger price history collection for the given URLs."""
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/trigger",
                headers=self.headers,
                params={"dataset_id": self.DATASET_ID, "include_errors": "true"},
                json=urls,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API error during collection trigger: {str(e)}")
            return None

    def _check_status(self, snapshot_id: str) -> Optional[str]:
        """Check the status of the price history collection process."""
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
        """Fetch collected price history data once the snapshot is ready."""
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
        self, data: List[Dict[str, Any]], filename: str = "zillow_price_history.json"
    ) -> None:
        """Save collected price history data to a JSON file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")


def main() -> None:
    """Run the Zillow price history collection process with sample URLs."""
    api_token = "API_TOKEN"  # Replace with your actual API token
    collector = ZillowPriceHistoryCollector(api_token)

    urls = [
        {
            "url": "https://www.zillow.com/homedetails/8305-Blue-Heron-Way-Raleigh-NC-27615/6468808_zpid/"
        },
        {
            "url": "https://www.zillow.com/homedetails/930-3rd-St-SE-Hickory-NC-28602/71557289_zpid/"
        },
    ]

    collector.collect_price_history(urls)


if __name__ == "__main__":
    main()
