import requests
import json
from datetime import datetime
from typing import Dict, Tuple

# Constants
API_URL = "https://www.zillow.com/async-create-search-page-state"
DEFAULT_REGION_ID = 12447
DEFAULT_REGION_NAME = "Los Angeles CA"


def get_user_input() -> Tuple[float, float, float, float, int]:
    """Get search parameters for Zillow query."""
    return (
        -118.668176,  # west
        -118.155289,  # east
        33.703652,  # south
        34.337306,  # north
        5,  # pages
    )


def get_request_headers() -> Dict:
    """Return headers for Zillow API requests."""
    return {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.5",
        "content-type": "application/json",
        "origin": "https://www.zillow.com",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }


def create_request_payload(
    bounds: Tuple[float, float, float, float], page: int
) -> Dict:
    """Create API request payload with search parameters."""
    west, east, south, north = bounds
    return {
        "searchQueryState": {
            "pagination": {"currentPage": page},
            "mapBounds": {
                "west": west,
                "east": east,
                "south": south,
                "north": north,
            },
            "usersSearchTerm": DEFAULT_REGION_NAME,
            "regionSelection": [{"regionId": DEFAULT_REGION_ID}],
            "filterState": {"sortSelection": {"value": "globalrelevanceex"}},
            "isListVisible": True,
        },
        "wants": {"cat1": ["listResults"], "cat2": ["total"]},
        "requestId": 6,
    }


def parse_property_data(property_data: Dict) -> Dict:
    """Parse individual property data from API response."""
    home_info = property_data.get("hdpData", {}).get("homeInfo", {})

    return {
        "id": property_data.get("zpid"),
        "price": property_data.get("price"),
        "zestimate": property_data.get("zestimate"),
        "location": {
            "address": property_data.get("address"),
            "city": property_data.get("addressCity"),
            "state": property_data.get("addressState"),
            "zip": property_data.get("addressZipcode"),
            "coordinates": {
                "lat": property_data.get("latLong", {}).get("latitude"),
                "lon": property_data.get("latLong", {}).get("longitude"),
            },
        },
        "details": {
            "beds": property_data.get("beds"),
            "baths": property_data.get("baths"),
            "area_sqft": property_data.get("area"),
            "lot_acres": home_info.get("lotAreaValue"),
            "property_type": home_info.get("homeType"),
        },
        "listing": {
            "status": property_data.get("statusText"),
            "days_on_zillow": home_info.get("daysOnZillow"),
            "broker": property_data.get("brokerName"),
            "url": property_data.get("detailUrl"),
        },
    }


def process_api_response(response_data: Dict, page_num: int) -> Dict:
    """Process and structure raw API response data."""
    results = {
        "page_number": page_num,
        "total_results": response_data.get("cat1", {})
        .get("searchList", {})
        .get("totalResultCount"),
        "properties": [],
    }

    properties = (
        response_data.get("cat1", {}).get("searchResults", {}).get("listResults", [])
    )

    for prop in properties:
        results["properties"].append(parse_property_data(prop))

    return results


def fetch_page_data(bounds: Tuple[float, float, float, float], page: int) -> Dict:
    """Fetch and process data for a single page."""
    headers = get_request_headers()
    payload = create_request_payload(bounds, page)

    try:
        response = requests.put(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return process_api_response(response.json(), page)

    except requests.exceptions.RequestException as e:
        print(f"Request failed for page {page}: {str(e)}")
        return None


def save_results(data: Dict, filename: str) -> None:
    """Save structured data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")


def generate_output_filename() -> str:
    """Generate timestamped output filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"zillow_data.json"


def main():
    """Main execution flow."""
    print("Starting Zillow Data Collector")

    west, east, south, north, total_pages = get_user_input()
    bounds = (west, east, south, north)

    dataset = {
        "metadata": {
            "search_area": bounds,
            "pages_requested": total_pages,
            "execution_time": datetime.now().isoformat(),
        },
        "results": [],
    }

    successful_pages = 0
    for page in range(1, total_pages + 1):
        print(f"Processing page {page}/{total_pages}...")
        page_data = fetch_page_data(bounds, page)

        if page_data:
            dataset["results"].append(page_data)
            successful_pages += 1
            print(f"Found {len(page_data['properties'])} properties")

    dataset["metadata"]["pages_received"] = successful_pages
    dataset["metadata"]["total_properties"] = sum(
        len(page["properties"]) for page in dataset["results"]
    )

    filename = generate_output_filename()
    save_results(dataset, filename)

    print("\nExecution Summary:")
    print(f"Successfully retrieved {successful_pages}/{total_pages} pages")
    print(f"Total properties collected: {dataset['metadata']['total_properties']}")


if __name__ == "__main__":
    main()