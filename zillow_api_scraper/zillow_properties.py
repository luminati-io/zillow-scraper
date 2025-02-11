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


class ZillowPropertiesCollector:
    """Collects Zillow property data using the Bright Data API."""

    API_BASE_URL = "https://api.brightdata.com/datasets/v3"
    DATASET_ID = "gd_lfqkr8wm13ixtbd8f5"  # Dataset ID for Zillow properties

    def __init__(self, api_token: str):
        """Initialize with API token and headers."""
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def collect_properties(self, property_urls: List[Dict[str, str]]) -> Optional[bool]:
        """Trigger and monitor data collection, then save results."""
        start_time = datetime.now()
        logging.info(f"Starting collection for {len(property_urls)} properties...")

        collection_response = self._trigger_collection(property_urls)
        if not collection_response or "snapshot_id" not in collection_response:
            logging.error("Failed to initiate data collection")
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
                properties_data = self._fetch_data(snapshot_id)
                if properties_data:
                    self._save_data(properties_data)
                    logging.info("Data saved successfully")
                    return True
            elif status in ["failed", "error"]:
                return None

            time.sleep(5)

    def _trigger_collection(
        self, property_urls: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Trigger data collection for the given property URLs."""
        try:
            response = requests.post(
                f"{self.API_BASE_URL}/trigger",
                headers=self.headers,
                params={"dataset_id": self.DATASET_ID, "include_errors": "true"},
                json=property_urls,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API error during collection trigger: {str(e)}")
            return None

    def _check_status(self, snapshot_id: str) -> Optional[str]:
        """Check the status of the data collection process."""
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
        """Fetch collected data once the snapshot is ready."""
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
        self, data: List[Dict[str, Any]], filename: str = "zillow_properties.json"
    ) -> None:
        """Save collected data to a JSON file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")


def main() -> None:
    """Run the Zillow property collection process with sample URLs."""
    api_token = "API_TOKEN"  # Replace with your actual API token
    collector = ZillowPropertiesCollector(api_token)

    properties = [
        {
            "url": "https://www.zillow.com/homedetails/73-Beverly-Park-Ln-Beverly-Hills-CA-90210/20533547_zpid/"
        },
        {
            "url": "https://www.zillow.com/homedetails/73-Beverly-Park-Ln-Beverly-Hills-CA-90210/20533547_zpid/"
        },
        {
            "url": "https://www.zillow.com/homedetails/1945-N-Edgemont-St-Los-Angeles-CA-90027/20809871_zpid/"
        },
    ]

    collector.collect_properties(properties)


if __name__ == "__main__":
    main()