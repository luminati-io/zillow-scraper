import os
import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


class ZillowDiscoverPropertiesCollector:
    """
    A collector for discovering Zillow properties based on input filters.
    """

    API_BASE_URL = "https://api.brightdata.com/datasets/v3"
    DATASET_ID = "gd_lfqkr8wm13ixtbd8f5"  # Dataset ID for Zillow properties

    def __init__(self, api_token: str):
        """Initialize the collector with API token and headers."""
        if not api_token:
            raise ValueError("API token is required")
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def collect_properties(
        self,
        filters: List[Dict[str, str]],
        output_file: str = "zillow_discovered_properties.json",
    ) -> bool:
        """
        Execute full discovery workflow with indefinite running until completion.
        Returns True if successful, False otherwise.
        """
        start_time = datetime.now()
        logger = logging.getLogger(__name__)

        try:
            # Validate and clean filters before sending
            cleaned_filters = self._clean_filters(filters)
            if not cleaned_filters:
                logger.error("No valid filters provided after cleaning")
                return False

            logger.info(
                f"Starting property discovery for {len(cleaned_filters)} filters"
            )

            # Trigger collection and handle response
            collection_response = self._trigger_collection(cleaned_filters)
            if not collection_response or "snapshot_id" not in collection_response:
                logger.error("Failed to initiate property discovery")
                return False

            snapshot_id = collection_response["snapshot_id"]
            logger.debug(f"Received snapshot ID: {snapshot_id}")

            # Monitor collection indefinitely until completion
            properties_data = self._monitor_collection(snapshot_id, start_time)
            if not properties_data:
                return False

            # Save results with dynamic filename
            self._save_data(properties_data, output_file)
            logger.info(f"Data successfully saved to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Unexpected error during collection: {str(e)}")
            return False

    def _clean_filters(self, filters: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove empty values from filters to ensure API compatibility."""
        cleaned = []
        for f in filters:
            clean_filter = {k: v for k, v in f.items() if v and v.strip()}
            if clean_filter.get("location"):
                cleaned.append(clean_filter)
        return cleaned

    def _trigger_collection(
        self, filters: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """Initiate data collection with retry logic."""
        url = f"{self.API_BASE_URL}/trigger"
        params = {
            "dataset_id": self.DATASET_ID,
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "input_filters",
        }

        for attempt in range(3):
            try:
                response = requests.post(
                    url, headers=self.headers, params=params, json=filters, timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    logging.warning(f"Rate limited. Retrying in {wait} seconds...")
                    time.sleep(wait)
                else:
                    logging.error(
                        f"HTTP error: {e.response.status_code} - {e.response.text}"
                    )
                    return None
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {str(e)}")
                if attempt == 2:
                    return None
                time.sleep(1)
        return None

    def _monitor_collection(
        self, snapshot_id: str, start_time: datetime
    ) -> Optional[List[Dict]]:
        """Monitor collection progress indefinitely until completion."""
        logger = logging.getLogger(__name__)
        last_status = None
        status_counts = {}

        while True:
            status = self._check_status(snapshot_id)

            if status != last_status:
                logger.info(f"Status changed to {status}")
                last_status = status
                status_counts[status] = 1
            else:
                status_counts[status] = status_counts.get(status, 0) + 1

            elapsed = (datetime.now() - start_time).seconds
            if status == "ready":
                logger.info(f"Collection completed in {elapsed} seconds")
                return self._fetch_data(snapshot_id)
            if status in ["failed", "error"]:
                logger.error(f"Collection failed after {elapsed} seconds")
                return None

            # Log progress every 30 seconds for long-running operations
            if elapsed % 30 == 0:
                logger.info(
                    f"Still processing... Elapsed: {elapsed}s | Current status: {status}"
                )

            time.sleep(5)

    def _check_status(self, snapshot_id: str) -> str:
        """Check collection status with error handling."""
        try:
            response = requests.get(
                f"{self.API_BASE_URL}/progress/{snapshot_id}",
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
            return response.json().get("status", "unknown")
        except requests.exceptions.RequestException:
            return "error"

    def _fetch_data(self, snapshot_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve collected data with error handling."""
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
            logging.error(f"Failed to fetch data: {str(e)}")
            return None

    def _save_data(
        self, data: List[Dict[str, Any]], filename: str, backup: bool = True
    ) -> None:
        """Save data with backup option and error handling."""
        try:
            if backup and os.path.exists(filename):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{filename}.bak_{timestamp}"
                os.rename(filename, backup_name)
                logging.info(f"Created backup: {backup_name}")

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except (IOError, OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to save data: {str(e)}")
            raise


def main() -> None:
    """Execute the property discovery workflow with example filters."""
    api_token = "API_TOKEN"  # Replace with your actual API token

    collector = ZillowDiscoverPropertiesCollector(api_token)

    filters = [
        {"location": "92027", "listingCategory": "Sold", "HomeType": "Houses"},
        {
            "location": "New York",
            "listingCategory": "House for rent",
            "HomeType": "Condos",
        },
        {"location": "Colorado", "listingCategory": "", "HomeType": ""},
    ]

    success = collector.collect_properties(
        filters,
        output_file=f"zillow_properties_{datetime.now().strftime('%Y%m%d')}.json",
    )

    if success:
        logging.info("Discovery process completed successfully")
    else:
        logging.error("Discovery process failed")


if __name__ == "__main__":
    main()