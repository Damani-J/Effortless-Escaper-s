import requests
import pandas as pd
from datetime import datetime

# API keys
WEATHER_API_KEY = 'cd429d175aba4e43af731417242009'
AMADEUS_API_KEY = 'NMPtPNqSeWRp3G7iqmvA2lBTU5GA14er'
AMADEUS_API_SECRET = 'VZmM4osAyKc2KUGY'
ENDPOINT = 'https://tripadvisor1.p.rapidapi.com/locations/search'

# Function to convert Celsius to Fahrenheit
def c_to_f(celsius):
    return round((celsius * 9/5) + 32, 1)

# Function to format date
def format_date(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    month = date_obj.strftime('%m').lstrip('0')
    day = date_obj.strftime('%d').lstrip('0')
    year = date_obj.strftime('%y')
    return f"{month}/{day}/{year}"

# Function to convert date for API
def convert_date_for_api(input_date):
    date_obj = datetime.strptime(input_date, '%m/%d/%Y')
    return date_obj.strftime('%Y-%m-%d')

# Function to fetch weather
def fetch_weather(city, date):
    url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    data = response.json()
    
    avg_temp_low_c = data['forecast']['forecastday'][0]['day']['mintemp_c']
    avg_temp_high_c = data['forecast']['forecastday'][0]['day']['maxtemp_c']
    
    avg_temp_low_f = c_to_f(avg_temp_low_c)
    avg_temp_high_f = c_to_f(avg_temp_high_c)
    
    return avg_temp_low_f, avg_temp_high_f

# Function to get access token for Amadeus API
def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': AMADEUS_API_KEY,
        'client_secret': AMADEUS_API_SECRET
    }
    response = requests.post(url, data=data)
    return response.json()['access_token']

# Function to get average flight price
def get_average_flight_price(access_token, origin, destination, departure_date, num_adults):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': departure_date,
        'adults': num_adults,
        'max': 5
    }
    response = requests.get(url, headers=headers, params=params)
    flight_offers = response.json().get('data', [])
    
    if not flight_offers:
        return 0  # Return 0 if there are no flight offers
    
    total_price = sum(float(offer['price']['total']) for offer in flight_offers)
    average_price = total_price / len(flight_offers)
    return average_price * num_adults  # Multiply by number of adults

# Function to search locations
def search_locations(keywords):
    api_key = "28DB21DB31E2437EA53EA73A21C31A25"  # Replace with your TripAdvisor API key
    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    
    search_query = ' '.join(keywords)
    
    params = {"key": api_key, "searchQuery": search_query, "language": "en"}

    response = requests.get(url, params=params).json()
    
    if 'data' in response and response['data']:
        print(f"Based on your given input, these are the top 3 locations:")
        top_locations = []
        for location in response['data'][:3]:
            address_obj = location.get('address_obj', {})
            location_name = location['name']
            city = address_obj.get('city', '')
            top_locations.append((location_name, city))  # Store name and city
            print(f"    - {location_name}: {city}")
        return top_locations
    else:
        print("No locations found. Please try different keywords.")
        return []

# Function to fetch IATA code based on latitude and longitude
def fetch_iata_code(lat, lng):
    url = f"https://test.api.amadeus.com/v1/reference-data/locations/airports"
    headers = {
        "Authorization": f"Bearer {get_access_token()}"
    }
    params = {
        "latitude": lat,
        "longitude": lng,
        "radius": 50  # Search within 50 km
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if 'data' in data and len(data['data']) > 0:
        return data['data'][0]['iataCode']  # Return the first IATA code found
    else:
        return None

# Function to fetch latitude and longitude using OpenCage
def fetch_lat_long(city_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': city_name,
        'key': 'c50a386a9f994ecd975f75c8ef514517'  # Replace with your OpenCage API key
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return lat, lng
    else:
        print(f"Could not fetch latitude and longitude for {city_name}.")
        return None, None

# Main program flow
user_input = input("Enter keywords to find the perfect destination: ")
start_location = input("Where are you traveling from? (city): ")
num_adults = int(input("How many adults are going? "))
input_date_start = input("Date (start) (MM/DD/YYYY): ")
input_date_end = input("Date (end) (MM/DD/YYYY): ")

# Convert input dates
departure_date_start = convert_date_for_api(input_date_start)

# Get top locations based on user input
keywords = [keyword.strip() for keyword in user_input.split(",")]
top_locations = search_locations(keywords)

# Proceed if there are top locations
if top_locations:
    # Fetch latitude and longitude for the starting location
    start_lat, start_lng = fetch_lat_long(start_location)

    # Fetch IATA code for the starting location
    start_iata_code = fetch_iata_code(start_lat, start_lng)
    print(f"IATA code for your starting location ({start_location}): {start_iata_code}")  # Print IATA code

    # For simplicity, let's choose the first top location for the flight and weather data
    chosen_location_name, chosen_city = top_locations[0]
    print(f"\nChosen location for further analysis: {chosen_city}")

    # Fetch latitude and longitude for the chosen location
    destination_lat, destination_lng = fetch_lat_long(chosen_city)

    # Fetch IATA code for the chosen location
    destination_iata_code = fetch_iata_code(destination_lat, destination_lng)
    print(f"IATA code for {chosen_city}: {destination_iata_code}")  # Print the IATA code

    # Fetch weather data
    avg_temp_low_f, avg_temp_high_f = fetch_weather(chosen_city, departure_date_start)

    # Get flight price if both IATA codes are found
    if start_iata_code and destination_iata_code:
        token = get_access_token()
        avg_flight_price = get_average_flight_price(token, start_iata_code, destination_iata_code, departure_date_start, num_adults)
        
        # Output weather and flight price
        print(f"\nWeather forecast for {chosen_city} on {format_date(departure_date_start)}:")
        print(f"    Low Temp: {avg_temp_low_f}F")
        print(f"    High Temp: {avg_temp_high_f}F")
        print(f"\nAverage flight price from {start_location} to {chosen_city} on {format_date(departure_date_start)}: ${avg_flight_price:.2f}")
    else:
        print("Could not fetch IATA codes for the specified locations.")
