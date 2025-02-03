import pandas as pd
import requests
from io import StringIO

def get_airport_destinations(airport_code):
    """Retrieves destination airports for a given IATA airport code using OpenFlights data.

    Args:
        airport_code: The IATA code of the airport (e.g., "SEA", "BOS").

    Returns:
        A set of destination airport IATA codes, or None if data retrieval fails.
    """
    try:
        # OpenFlights routes data URL
        url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

        # Fetch the data
        response = requests.get(url, timeout=10) # added timeout for robustness
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Use pandas for efficient data loading and filtering
        df_routes = pd.read_csv(StringIO(response.text), header=None,
                                names=['Airline', 'Airline ID', 'Source Airport', 'Source Airport ID',
                                       'Destination Airport', 'Destination Airport ID', 'Codeshare', 'Stops', 'Equipment'])

        # Filter the DataFrame for the given source airport
        destinations = set(df_routes[df_routes['Source Airport'] == airport_code]['Destination Airport'].unique())
        return destinations
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def find_common_destinations(airport1, airport2):
    """Finds the common destination airports between two airports.

    Args:
        airport1: The IATA code of the first airport.
        airport2: The IATA code of the second airport.

    Returns:
        A set of common destination airport IATA codes, or None if data retrieval fails for either airport.
    """
    destinations1 = get_airport_destinations(airport1)
    destinations2 = get_airport_destinations(airport2)

    if destinations1 is None or destinations2 is None:
        return None

    common_destinations = destinations1.intersection(destinations2)
    return common_destinations

if __name__ == "__main__":
    seatac_code = "SEA"
    logan_code = "BOS"

    common_cities = find_common_destinations(seatac_code, logan_code)

    if common_cities is not None:
        print(f"Common destinations between {seatac_code} (SeaTac) and {logan_code} (Logan):")
        if common_cities: # check to make sure the set isn't empty
            for city in common_cities:
                print(city)
        else:
            print("None")
    else:
        print("Could not retrieve destination data for one or both airports.")