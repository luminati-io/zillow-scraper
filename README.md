# Zillow Scraper
This repository provides two distinct methods for scraping Zillow data:
1. A free, small-scale scraper for basic data collection
2. An enterprise-grade API solution for large-scale data extraction

## Table of Contents
- [Free Zillow Data Scraper](#free-zillow-data-scraper)
- [Limitations of Free Scraper](#limitations-of-free-scraper)
- [Zillow Scraper API](#zillow-scraper-api)
  - [Key Features](#key-features)
  - [Quick Start Guide](#quick-start-guide)
  - [Zillow Property Details by URL](#1-zillow-property-details-by-url)
  - [Zillow Properties Listing by Filters](#2-zillow-properties-listing-by-filters)
  - [Zillow Properties Listing by URL](#3-zillow-properties-listing-by-url)
  - [Zillow Price History](#4-zillow-price-history)
- [No-Code Scraper Option](#no-code-scraper-option)
- [Additional Options](#additional-options)
- [Support & Resources](#support--resources)

## Free Zillow Data Scraper
The free scraper allows you to collect property data from Zillow search pages on a small scale.

### Input Requirements
| Parameter | Required | Description |
|-----------|----------|-------------|
| coords    | Yes      | Boundary coordinates [west, east, south, north] |
| pages     | Yes      | Number of pages to scrape |

### Implementation
To use the scraper, modify the coordinates and page count in the following code according to your location and data requirements:
```python
# free_zillow_scraper/property_data.py
def get_search_params():
    return (
        -118.668176,  # West longitude
        -118.155289,  # East longitude
        33.703652,    # South latitude
        34.337306,    # North latitude
        5             # Number of pages to scrape
    )
```

**Hint:** Geographical coordinates can be found in the `<script>` tag of Zillow's search page for any location. Look for the following tag:
```bash
<script id="__NEXT_DATA__" type="application/json">
```

### Sample Output
```json
{
    "id": "20595672",
    "price": "$1,599,900",
    "zestimate": 1605500,
    "location": {
        "address": "2215 Wellington Rd, Los Angeles, CA 90016",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90016",
        "coordinates": {"lat": 34.036064, "lon": -118.33622},
    },
    "details": {
        "beds": 4,
        "baths": 3.0,
        "area_sqft": 1886,
        "lot_acres": 8577.0,
        "property_type": "SINGLE_FAMILY",
    },
    "listing": {
        "status": "House for sale",
        "days_on_zillow": 5,
        "broker": "ehomes",
        "url": "https://www.zillow.com/homedetails/2215-Wellington-Rd-Los-Angeles-CA-90016/20595672_zpid/",
    },
},
```

## Limitations of Free Scraper
The free Zillow scraper works well for small-scale data extraction but has the following limitations:

- **Rate Limiting:** Zillow blocks requests after a few scrapes.
- **IP Blocking:** Frequent scraping from the same IP can lead to bans.
- **Limited Scalability:** Not suitable for high-volume data collection.
- **Captcha:** Zillow may present CAPTCHAs to block automated requests.
- **Honeypots:** Zillow uses honeypot traps to detect and block bots.

For large-scale scraping, consider using the **Zillow Scraper API** described below.

##  Zillow Scraper API
The Bright Data [Zillow Scraper API](https://brightdata.com/products/web-scraper/zillow) provides a scalable, reliable, and hassle-free solution for extracting large-scale Zillow data without the need to build or maintain your own infrastructure.

### Key Features
- **Scalable & Reliable:** Optimized for high-volume and real-time data collection.
- **Anti-Blocking:** Built-in proxy rotation and CAPTCHA solving.
- **Legal Compliance:** Fully GDPR and CCPA compliant.
- **Global Coverage:** Access data from any region or language.
- **Real-Time Data:** Fresh data with minimal latency.
- **Advanced Filtering:** Customize data extraction with precise filters.
- **Pay-as-You-Go:** Only pay for successful responses.
- **Free Trial:** Includes 20 free API calls to get started.
- **Dedicated Support:** 24/7 technical assistance.
- **No-Code Option:** Scrape Zillow data via API or no-code scrapers.

### Quick Start Guide
- **Sign Up:** Create a [Bright Data account](https://brightdata.com/).
- **Get API Token:** Obtain your [API key](https://docs.brightdata.com/general/account/api-token) from the dashboard.
- **Choose Endpoint:** Select from the available API endpoints below.

## 1. Zillow Property Details by URL
Collect property details by providing the property URL.

<img width="700" alt="zillow-properties-listing-information" src="https://github.com/user-attachments/assets/bad6b74b-297d-4133-b4c3-de63a6b46fbd" />

### Input Parameters
| Parameter | Required | Description            |
|-----------|----------|------------------------|
| `url`       | Yes      | Zillow property URL   |


### Example Request
#### Python Code:
```python
properties = [
    {"url": "https://www.zillow.com/homedetails/73-Beverly-Park-Ln-Beverly-Hills-CA-90210/20533547_zpid/"},
    {"url": "https://www.zillow.com/homedetails/1945-N-Edgemont-St-Los-Angeles-CA-90027/20809871_zpid/"}
]
```

👉 Complete Python script: [zillow_properties.py](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_scraper/zillow_properties.py)

#### cURL Command:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '[
           {
             "url": "https://www.zillow.com/homedetails/2506-Gordon-Cir-South-Bend-IN-46635/77050198_zpid/?t=for_sale"
           }
         ]' \
     "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lfqkr8wm13ixtbd8f5&include_errors=true"
```

### Response Schema
```json
{
    "property_overview": {
        "address": "73 Beverly Park Ln, Beverly Hills, CA 90210",
        "price": "$89,900,000",
        "status": "FOR_SALE",
        "living_area": "28,500 sq ft",
        "lot_size": "2.68 acres",
        "bedrooms": 9,
        "bathrooms": 22,
    },
    "key_features": {
        "highlights": [
            "85-foot infinity lap pool",
            "Two kitchens (including commercial-grade)",
            "5,000 sq ft primary suite",
            "Screening room",
            "Gated community with guard",
        ],
        "views": ["City", "Ocean", "Mountain", "Canyon"],
    },
    "financial": {
        "last_sold": "2021-04-08 for $28,500,000",
        "property_tax_rate": "1.18%",
        "monthly_hoa": "$6,216",
    },
}
```

👉 This is a partial response. See the [full JSON response](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_data/zillow_properties.json) for complete property details.

## 2. Zillow Properties Listing by Filters
Search properties using location and other criteria.

<img width="700" alt="zillow-properties-listing-by-input" src="https://github.com/user-attachments/assets/b21de730-db2c-4dca-8964-9653e10350cc" />

💡 **Note:** Some properties may have multiple units, which can result in several records. To limit results, use the [Limit per input](https://docs.brightdata.com/scraping-automation/web-scraper-api/overview#limit-records).

### Input Parameters
| Parameter       | Required | Description                                          |
|---------------|----------|------------------------------------------------------|
| `location`      | Yes      | Can be a zip code, city, or state.                   |
| `listingCategory` | Yes    | Options: Sold, House for rent, House for sale.       |
| `HomeType`      | Yes      | Home type from Zillow (e.g., Houses, Apartments, Townhomes). |


### Example Request
#### Python Code:
```python
filters = [
    {"location": "92027", "listingCategory": "Sold", "HomeType": "Houses"},
    {"location": "New York", "listingCategory": "House for rent", "HomeType": "Condos"},
    {"location": "Colorado", "listingCategory": "", "HomeType": ""},
]
```
👉 Complete Python script: [zillow_discovered_properties.py](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_scraper/zillow_discovered_properties.py)

#### cURL Command:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '[{"location": "New York", "listingCategory": "House for rent", "HomeType": "Houses"},
          {"location": "02118", "listingCategory": "House for sale", "HomeType": "Condos"},
          {"location": "Colorado", "listingCategory": "", "HomeType": ""}]' \
     "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lfqkr8wm13ixtbd8f5&include_errors=true&type=discover_new&discover_by=input_filters"
```

### Response Schema
```json
{
    "address": {
        "streetAddress": "569 Hayward Pl",
        "city": "Escondido",
        "state": "CA",
        "zipcode": "92027",
    },
    "homeStatus": "SOLD",
    "bedrooms": 4,
    "bathrooms": 2,
    "livingArea": 1446,
    "livingAreaUnits": "Square Feet",
    "lotSize": 5933,
    "lotAreaUnits": "Square Feet",
    "homeType": "SINGLE_FAMILY",
    "yearBuilt": 1987,
    "lastSoldPrice": 689000,
    "dateSoldString": "2022-08-11",
    "zestimate": 818100,
    "rentZestimate": 3752,
    "schools": [
        {
            "name": "Glen View Elementary School",
            "distance": 0.6,
            "rating": 5,
            "grades": "K-5",
        },
        {
            "name": "Hidden Valley Middle School",
            "distance": 1.2,
            "rating": 5,
            "grades": "6-8",
        },
        {
            "name": "Orange Glen High School",
            "distance": 1.4,
            "rating": 5,
            "grades": "9-12",
        },
    ],
    "url": "https://www.zillow.com/homedetails/569-Hayward-Pl-Escondido-CA-92027/16696746_zpid/",
}
```

👉 This is a partial response. See the [full JSON response](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_data/zillow_discovered_properties.json) for complete property details.

## 3. Zillow Properties Listing by URL
Search for properties directly using Zillow search page URLs.

<img width="700" alt="zillow-properties-listing-by-url" src="https://github.com/user-attachments/assets/6c0b0f4a-20a0-437a-bac5-92b47c70dbd2" />


💡 **Note:** Some properties may have multiple units, which can result in several records. To limit results, use the [Limit per input](https://docs.brightdata.com/scraping-automation/web-scraper-api/overview#limit-records).


### Input Parameters:
| Parameter | Required | Description                          |
|-----------|----------|--------------------------------------|
| `url`       | Yes      | Direct Zillow search URL with complete search parameters |

### Example Request
#### Python Code:
```python
urls = [
    {"url": "https://www.zillow.com/south-bend-in/?searchQueryState=%7B%22pagination%22%3A..."},
    {"url": "https://www.zillow.com/new-york-ny/rentals/?searchQueryState=%7B%22isMapVisible%22%3A..."},
    {"url": "https://www.zillow.com/sands-point-ny/rentals/?searchQueryState=%7B%22isMapVisible%22%3A..."},
]
```
👉 Complete Python script: [zillow_discovered_properties_by_url.py](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_scraper/zillow_discovered_properties_by_url.py)

#### cURL Command:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '[{"url": "https://www.zillow.com/south-bend-in/?searchQueryState=%7B%22pagination%22%3A..."}]' \
     "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lfqkr8wm13ixtbd8f5&include_errors=true&type=discover_new&discover_by=url"
```

### Response Schema:
```json
{
    "zpid": 77029580,
    "address": {
        "streetAddress": "1937 Churchill Dr",
        "city": "South Bend",
        "state": "IN",
        "zipcode": "46617",
    },
    "price": 435000,
    "bedrooms": 4,
    "bathrooms": 4,
    "livingArea": 3197,
    "lotAreaValue": 0.46,
    "lotAreaUnits": "Acres",
    "yearBuilt": 1968,
    "homeStatus": "FOR_SALE",
    "zestimate": 420400,
    "lastSoldPrice": 134000,
    "dateSold": "2013-05-20",
    "schools": [
        {"name": "McKinley Elementary School", "rating": 4},
        {"name": "Edison Intermediate Center", "rating": 2},
        {"name": "Rise Up Academy At Eggleston", "rating": 1},
    ],
    "mortgageRates": {"thirtyYearFixedRate": 6.536},
    "listingProvidedBy": {"name": "Eric M Bomkamp", "phoneNumber": "574-360-2569"},
    "url": "https://www.zillow.com/homedetails/1937-Churchill-Dr-South-Bend-IN-46617/77029580_zpid/",
}
```
👉 This is a partial response. See the [full JSON response](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_data/zillow_discovered_properties_by_url.json) for complete property details.

## 4. Zillow Price History
Collect pricing history for a property.

<img width="700" alt="zillow-price-history" src="https://github.com/user-attachments/assets/e25e878b-6ddc-49fa-bb22-f23092aae5bf" />

### Input Parameters

| Parameter | Required | Description            |
|-----------|----------|------------------------|
| `url`       | Yes      | Zillow property URL.   |

### Example Request
#### Python Code:

```python
urls = [
    {"url": "https://www.zillow.com/homedetails/8305-Blue-Heron-Way-Raleigh-NC-27615/6468808_zpid/"},
    {"url": "https://www.zillow.com/homedetails/930-3rd-St-SE-Hickory-NC-28602/71557289_zpid/"},
]
```
👉 Complete Python script: [zillow_price_history.py](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_scraper/zillow_price_history.py)

#### cURL Command:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '[{"url": "https://www.zillow.com/homedetails/8305-Blue-Heron-Way-Raleigh-NC-27615/6468808_zpid/"},
          {"url": "https://www.zillow.com/homedetails/930-3rd-St-SE-Hickory-NC-28602/71557289_zpid/"}]' \
     "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lxu1cz9r88uiqsosl&include_errors=true"
```

### Response Schema:
```json
{
    "url": "https://www.zillow.com/homedetails/8305-Blue-Heron-Way-Raleigh-NC-27615/6468808_zpid/",
    "zpid": "6468808",
    "date": "2020-11-13T00:00:00.000Z",
    "event": "Sold",
    "price": 440000,
    "price_per_squarefoot": 127,
    "source": "Doorify MLS",
    "timestamp": "2025-02-09T16:56:42.074Z",
}
```
👉 This is a partial response. See the [full JSON response](https://github.com/triposat/Zillow-Scraper/blob/main/zillow_api_data/zillow_price_history.json) for complete property details.

## No-Code Scraper Option
Bright Data **No-Code Scraper** offers a user-friendly way to collect Zillow data without programming.
- Configure scrapers in minutes.
- Automate the entire data collection process.
- Download results directly in multiple formats.

For detailed instructions, visit our [Getting Started guide](https://github.com/triposat/Zillow-Scraper/blob/main/no-code-scraper.md).

## Additional Options
Fine-tune your data collection with these parameters:

| **Parameter**       | **Type**   | **Description**                                            | **Example**                  |
|---------------------|------------|------------------------------------------------------------|------------------------------|
| `limit`             | `integer`  | Max results per input                                   | `limit=10`                   |
| `include_errors`    | `boolean`  | Get error reports for troubleshooting                     | `include_errors=true`        |
| `notify`            | `url`      | Webhook notification URL to be notified upon completion  | `notify=https://notify-me.com/` |
| `format`            | `enum`     | Output format (e.g., JSON, NDJSON, JSONL, CSV)         | `format=json`                |

💡 **Pro Tip:** You can deliver data to an [external storage](https://docs.brightdata.com/scraping-automation/web-data-apis/web-scraper-api/overview#via-deliver-to-external-storage) or a [webhook](https://docs.brightdata.com/scraping-automation/web-data-apis/web-scraper-api/overview#via-webhook).

## Support & Resources
- **API Documentation:** [Bright Data Docs](https://docs.brightdata.com/scraping-automation/web-scraper-api/trigger-a-collection)
- **Scraping Best Practices:** [Avoid Getting Blocked](https://brightdata.com/blog/web-data/web-scraping-without-getting-blocked)
- **Technical Support:** [Contact Us](mailto:support@brightdata.com)
