import requests
import json
import os
import base64
from dotenv import load_dotenv


def fetch_company_data(raw_api_key, location, sic_codes_list):
    """
    Fetches company data from the Companies House API.

    Args:
        raw_api_key (str): The raw API key (e.g., a UUID).
        location (str): The location to search for companies.
        sic_codes_list (list): A list of SIC codes to filter by.

    Returns:
        dict: The JSON response from the API as a dictionary, or None if an error occurs.
    """
    base_url = "https://api.company-information.service.gov.uk/advanced-search/companies"
    sic_codes_query_param = ",".join(sic_codes_list)
    url = f"{base_url}?location={location}&company_status=active&size=500&sic_codes={sic_codes_query_param}"

    # Prepare API key for Basic Authentication: key + ":" then Base64 encode
    auth_string = f"{raw_api_key}:"
    encoded_auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    payload = {}
    headers = {
        'Authorization': f'Basic {encoded_auth_string}'
    }

    print(f"Requesting URL: {url}")  # For debugging purposes
    # print(f"Authorization Header: Basic {encoded_auth_string[:10]}...") # For debugging, show partial encoded key

    try:
        response = requests.get(url, headers=headers, data=payload, timeout=30)  # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from response.")
        if 'response' in locals():
            print(f"Response text: {response.text}")
    return None


def format_and_save_addresses(data, location, sic_codes_list):
    """
    Formats company addresses from the API data and saves them to a dynamically named text file.
    Skips records if registered_office_address is blank.

    Args:
        data (dict): The parsed JSON data from the API.
        location (str): The location used for the search, for filename.
        sic_codes_list (list): List of SIC codes, first one used for filename.
    """
    if not sic_codes_list:  # Should not happen if input validation is correct
        print("Error: SIC codes list is empty, cannot generate filename.")
        return

    # Generate filename: location_firstSICcode.txt
    # Sanitize location and SIC code for filename (basic sanitization)
    safe_location = "".join(c if c.isalnum() else "_" for c in location)
    safe_sic_code = "".join(c if c.isalnum() else "_" for c in sic_codes_list[0])
    output_filename = f"{safe_location}_{safe_sic_code}.txt"

    if not data or "items" not in data or not data["items"]:
        print(f"No company items found in the data or 'items' is empty for {location} / {', '.join(sic_codes_list)}.")
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(
                    f"No company data found for location '{location}' and SIC code(s) '{', '.join(sic_codes_list)}'.\n")
            print(f"Output file '{output_filename}' created with no data message.")
        except IOError as e:
            print(f"Error writing to file {output_filename}: {e}")
        return

    output_lines = []
    skipped_count = 0
    processed_count = 0

    for company in data["items"]:
        address_info = company.get("registered_office_address")

        # Skip if registered_office_address is missing, None, or an empty dictionary
        if not address_info:  # This checks for None or empty dict
            skipped_count += 1
            continue

        company_name = company.get("company_name", "N/A")

        # Ensure address_info is a dictionary before trying to .get() from it
        # (already handled by the `if not address_info` check if it was None,
        # but good for robustness if it could be other non-dict types)
        if not isinstance(address_info, dict):
            address_info = {}

        address_line_1 = address_info.get("address_line_1", "")
        address_line_2 = address_info.get("address_line_2", "")
        locality = address_info.get("locality", "")
        postal_code = address_info.get("postal_code", "")

        # Further check: if all essential address fields are empty, consider it blank
        if not company_name and not address_line_1 and not locality and not postal_code:
            # This is an additional check, the primary one is `if not address_info:`
            skipped_count += 1
            continue

        output_lines.append(str(company_name))
        output_lines.append(str(address_line_1))
        if address_line_2:
            output_lines.append(str(address_line_2))
        output_lines.append(str(locality))
        output_lines.append(str(postal_code))
        output_lines.append("----")
        processed_count += 1

    if not output_lines and processed_count == 0:  # All records might have been skipped
        print(
            f"All records were skipped due to missing address information for {location} / {', '.join(sic_codes_list)}.")
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(
                    f"No companies with complete address data found for location '{location}' and SIC code(s) '{', '.join(sic_codes_list)}'.\n")
                f.write(f"Total records received: {len(data.get('items', []))}, Total skipped: {skipped_count}\n")
            print(f"Output file '{output_filename}' created indicating all records skipped.")
        except IOError as e:
            print(f"Error writing to file {output_filename}: {e}")
        return

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"Addresses successfully written to {output_filename}")
        print(f"Total companies processed and written: {processed_count}")
        if skipped_count > 0:
            print(f"Total companies skipped due to missing address: {skipped_count}")

        api_hits = data.get('hits', 'N/A')
        print(f"Total hits reported by API: {api_hits}")
        # Compare API hits with sum of processed and skipped from items list
        total_items_from_api_page = len(data.get('items', []))
        if total_items_from_api_page < api_hits:  # Check if items on page is less than total hits
            print("Note: The number of items on this page is less than total API hits. ")
            print(
                "This might be due to the 'size' parameter limit per request. Pagination might be needed for all results.")

    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")


if __name__ == "__main__":
    load_dotenv()

    raw_api_key_from_env = os.getenv("API_KEY")

    if not raw_api_key_from_env:
        print("Error: API_KEY not found in .env file. Please create a .env file with your RAW API_KEY.")
        print("Example .env content: API_KEY=your_actual_api_key_without_encoding")
    else:
        location_input = os.getenv("LOCATION")
        sic_codes_input_str = os.getenv("SIC_CODES")

        if not location_input:
            print("Location cannot be empty.")
            exit()
        elif not sic_codes_input_str:
            print("SIC code(s) cannot be empty.")
            exit()
        else:
            sic_codes_list_input = [code.strip() for code in sic_codes_input_str.split(',') if code.strip()]
            if not sic_codes_list_input:
                print("SIC code(s) cannot be empty after stripping.")
            else:
                company_api_data = fetch_company_data(raw_api_key_from_env, location_input, sic_codes_list_input)

                if company_api_data:
                    format_and_save_addresses(company_api_data, location_input, sic_codes_list_input)
                else:
                    print("Could not retrieve or process company data. Please check previous error messages.")