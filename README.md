# Companies House API Scraper

**Part of "Prov 2627"**

This Python script fetches company data from the UK Companies House API based on location and SIC (Standard Industrial Classification) codes. It then extracts and formats company addresses, saving them to a text file.

---
## Description

The script performs an advanced search for active companies using the specified location and SIC codes. It retrieves company names and registered office addresses. The addresses are then formatted and saved to a `.txt` file named dynamically based on the search location and the first SIC code provided (e.g., `London_62012.txt`).

The script requires a Companies House API key, which should be provided as a raw key (e.g., a UUID string) in a `.env` file.

---
## Features

* Fetches company data from the official Companies House API.
* Filters companies by location and one or more SIC codes.
* Authenticates using Basic Authentication with an API key.
* Formats company name and address details (address line 1, address line 2, locality, postal code).
* Skips companies with missing registered office address information.
* Saves the formatted addresses to a dynamically named `.txt` file.
* Reads API key, location, and SIC codes from a `.env` file for easy configuration.
* Includes basic error handling for API requests (HTTP errors, timeouts, connection errors) and file operations.
* Provides console output for progress and errors.
* Indicates if the API returned fewer items than total hits, suggesting pagination might be needed for complete results.

---
## Requirements

* Python 3.x
* `requests` library
* `python-dotenv` library

---
## Setup

1.  **Clone the repository (if applicable) or download the script.**
2.  **Install dependencies:**
    Open your terminal or command prompt and run:
    ```bash
    pip install requests python-dotenv
    ```
3.  **Create a `.env` file:**
    In the same directory as the script, create a file named `.env`.
4.  **Add your Companies House API Key and search parameters to the `.env` file:**
    Open the `.env` file and add the following lines, replacing the placeholder values with your actual raw API key and desired search criteria:

    ```env
    API_KEY=YOUR_RAW_API_KEY_HERE_WITHOUT_ENCODING
    LOCATION=London
    SIC_CODES=62012,62020
    ```
    * `API_KEY`: Your raw API key provided by Companies House (it's usually a long string of letters and numbers). **Do not Base64 encode it yourself; the script handles this.**
    * `LOCATION`: The town, city, or postcode to search for companies.
    * `SIC_CODES`: A comma-separated list of SIC codes to filter by (e.g., `62012` for "Business and domestic software development").

---
## Usage

Once the setup is complete, run the script from your terminal:

```bash
python your_script_name.py