import json
import requests
import pandas as pd
import streamlit as st


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

def extract_airport_data(airport_dict):
    """Extracts IATA, name, and display_name from an airport dictionary and returns a Pandas DataFrame.

    Args:
        airport_dict: A dictionary where keys are airport codes and values are airport information dictionaries.

    Returns:
        A Pandas DataFrame containing the extracted data, or an empty DataFrame if the input is invalid.
    """

    data = []
    for airport_code, airport_info in airport_dict.items():
        iata = airport_info.get('iata')  # Use .get() to handle missing keys safely
        name = airport_info.get('name')
        display_name = airport_info.get('display_name')

        if iata and name and display_name: # Check if the required values are present
            data.append({'iata': iata, 'name': name, 'display_name': display_name})
        else:
            print(f"Warning: Incomplete data for airport code: {airport_code}. Skipping.")

    df = pd.DataFrame(data)
    return df

def get_flight_times_df(airport_data, airport1_code, airport2_code, common_destinations):
    """Gets flight times for common destinations and returns a Pandas DataFrame.

    Args:
        airport_data: The loaded airport data (dictionary).
        airport1_code: IATA code of the first airport.
        airport2_code: IATA code of the second airport.
        common_destinations: A set of common destination IATA codes.

    Returns:
        A Pandas DataFrame with columns 'iata', airport1_code, and airport2_code, or an empty DataFrame if no data is found.
    """

    data = []
    for dest in common_destinations:
        time1 = None
        time2 = None

        origin1_info = airport_data.get(airport1_code)
        if origin1_info:
          routes1 = origin1_info.get('routes', [])
          for route in routes1:
              if route.get('iata') == dest:
                  time1 = route.get('min')
                  break  # Stop searching once time is found

        origin2_info = airport_data.get(airport2_code)
        if origin2_info:
          routes2 = origin2_info.get('routes', [])
          for route in routes2:
              if route.get('iata') == dest:
                  time2 = route.get('min')
                  break  # Stop searching once time is found

        data.append({'iata': dest, airport1_code: time1, airport2_code: time2})

    df = pd.DataFrame(data)
    return df

# Streamlit app
st.title("Common Destination Flight Times")

airport1_code = st.text_input("Enter first airport code (e.g., SEA):", "SEA")
airport2_code = st.text_input("Enter second airport code (e.g., BOS):", "BOS")

if airport1_code and airport2_code:
    url = "https://raw.githubusercontent.com/Jonty/airline-route-data/main/airline_routes.json"
    airport_data = read_airport_data_from_url(url)

    if airport_data:
        common_destinations = find_common_destinations(airport_data, airport1_code, airport2_code)

        if common_destinations:
            df_flights = get_flight_times_df(airport_data, airport1_code, airport2_code, common_destinations)
            airport_df = extract_airport_data(airport_data)

            if not df_flights.empty:
                common_destinations_df = df_flights.merge(airport_df, how='left', on='iata')

                # Calculate the difference in flight times (after the merge!)
                common_destinations_df['time_diff'] = abs(common_destinations_df[airport1_code] - common_destinations_df[airport2_code])

                # Filter by time difference (using the merged DataFrame)
                min_diff = st.slider("Minimum Time Difference (minutes)", 0, 500, 500)
                filtered_df = common_destinations_df[common_destinations_df['time_diff'] <= min_diff]  # Correct filtering

                filtered_df.rename(columns={'iata': 'Common Desitination (IATA)', airport1_code: f"{airport1_code} mins", airport2_code: f"{airport2_code} mins", "name": "Airport Name", "display_name": "City, Country"}, inplace=True)
                # Display the table
                st.dataframe(filtered_df)

            else:
                st.write(f"No flight information found for the common destinations between {airport1_code} and {airport2_code}.")
        else:
            st.write(f"No common destinations found between {airport1_code} and {airport2_code}.")
    else:
        st.write("Failed to load airport data. Please check the URL.")
elif not airport1_code and not airport2_code:
    st.write("Please enter both airport codes.")
elif not airport1_code:
    st.write("Please enter the first airport code")
else:
    st.write("Please enter the second airport code")
