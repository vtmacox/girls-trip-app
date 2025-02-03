import json
import requests

def read_airport_data_from_url(url):
    """Reads airport data from a JSON file at a given URL.

    Args:
        url: The URL of the JSON file.

    Returns:
        A dictionary containing the airport data, or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=10)  # Added timeout for robustness
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        airport_data = response.json()
        return airport_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in the data from {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def get_airport_destinations(airport_data, airport_code):
    """Extracts destination airports for a given airport code.

    Args:
        airport_data: The loaded airport data (dictionary).
        airport_code: The IATA code of the airport.

    Returns:
        A set of destination airport IATA codes, or an empty set if the airport is not found or has no routes.
    """
    airport_info = airport_data.get(airport_code)
    if not airport_info:
        print(f"Airport {airport_code} not found in data.")
        return set()  # Return an empty set

    routes = airport_info.get('routes', [])  # Handle missing 'routes' key
    destinations = set()
    for route in routes:
        dest_iata = route.get('iata') # Handle missing 'iata' key in routes
        if dest_iata:
            destinations.add(dest_iata)
    return destinations


def find_common_destinations(airport_data, airport1, airport2):
    """Finds the common destination airports between two airports.

    Args:
        airport_data: The loaded airport data (dictionary).
        airport1: The IATA code of the first airport.
        airport2: The IATA code of the second airport.

    Returns:
        A set of common destination airport IATA codes.
    """
    destinations1 = get_airport_destinations(airport_data, airport1)
    destinations2 = get_airport_destinations(airport_data, airport2)

    common_destinations = destinations1.intersection(destinations2)
    return common_destinations

if __name__ == "__main":
    # Example usage:
    url = "https://raw.githubusercontent.com/Jonty/airline-route-data/main/airline_routes.json"
    airport_data = read_airport_data_from_url(url)

    if airport_data:
        airport1_code = "SEA"  # Seattle-Tacoma International Airport
        airport2_code = "BOS"  # Logan International Airport

        common_destinations = find_common_destinations(airport_data, airport1_code, airport2_code)

        if common_destinations:
            print(f"Common destinations between {airport1_code} and {airport2_code}:")
            for dest in common_destinations:
                print(dest)
        else:
            print(f"No common destinations found between {airport1_code} and {airport2_code}.")
    else:
        print("Failed to load airport data.")