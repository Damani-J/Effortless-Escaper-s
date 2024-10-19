import requests
import pandas as pd
from datetime import datetime

# API keys
WEATHER_API_KEY = 'cd429d175aba4e43af731417242009'
AMADEUS_API_KEY = 'NMPtPNqSeWRp3G7iqmvA2lBTU5GA14er'
AMADEUS_API_SECRET = 'VZmM4osAyKc2KUGY'
TRIPADVISOR_API_KEY = '28DB21DB31E2437EA53EA73A21C31A25'
OPENCAGE_API_KEY = 'c50a386a9f994ecd975f75c8ef514517'

def c_to_f(celsius):
    return round((celsius * 9/5) + 32, 1)

def format_date(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    month = date_obj.strftime('%m').lstrip('0')
    day = date_obj.strftime('%d').lstrip('0')
    year = date_obj.strftime('%y')
    return f"{month}/{day}/{year}"

def convert_date_for_api(input_date):
    date_obj = datetime.strptime(input_date, '%m/%d/%Y')
    return date_obj.strftime('%Y-%m-%d')

def fetch_weather(city, date):
    url = f"http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    data = response.json()
    avg_temp_low_c = data['forecast']['forecastday'][0]['day']['mintemp_c']
    avg_temp_high_c = data['forecast']['forecastday'][0]['day']['maxtemp_c']
    avg_temp_low_f = c_to_f(avg_temp_low_c)
    avg_temp_high_f = c_to_f(avg_temp_high_c)
    return avg_temp_low_f, avg_temp_high_f

def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': AMADEUS_API_KEY,
        'client_secret': AMADEUS_API_SECRET
    }
    response = requests.post(url, data=data)
    return response.json()['access_token']

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
    total_price = sum(float(offer['price']['total']) for offer in flight_offers)
    average_price = total_price / len(flight_offers)
    return average_price * num_adults

def search_locations(keywords):
    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    search_query = ' '.join(keywords)
    params = {"key": TRIPADVISOR_API_KEY, "searchQuery": search_query, "language": "en"}
    response = requests.get(url, params=params).json()
    top_locations = []
    for location in response['data'][:3]:
        address_obj = location.get('address_obj', {})
        location_name = location['name']
        city = address_obj.get('city', '')
        top_locations.append((location_name, city))
    return top_locations

def fetch_iata_code(lat, lng):
    url = f"https://test.api.amadeus.com/v1/reference-data/locations/airports"
    headers = {
        "Authorization": f"Bearer {get_access_token()}"
    }
    params = {
        "latitude": lat,
        "longitude": lng,
        "radius": 50
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data['data'][0]['iataCode']

def fetch_lat_long(city_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': city_name,
        'key': OPENCAGE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    lat = data['results'][0]['geometry']['lat']
    lng = data['results'][0]['geometry']['lng']
    return lat, lng

user_input = input("Enter keywords to find the perfect destination: ")
start_location = input("Where are you traveling from? (city): ")
num_adults = int(input("How many adults are going? "))
input_date_start = input("Date (start) (MM/DD/YYYY): ")
input_date_end = input("Date (end) (MM/DD/YYYY): ")

departure_date_start = convert_date_for_api(input_date_start)
keywords = [keyword.strip() for keyword in user_input.split(",")]
top_locations = search_locations(keywords)

start_lat, start_lng = fetch_lat_long(start_location)
start_iata_code = fetch_iata_code(start_lat, start_lng)
chosen_location_name, chosen_city = top_locations[0]
destination_lat, destination_lng = fetch_lat_long(chosen_city)
destination_iata_code = fetch_iata_code(destination_lat, destination_lng)

avg_temp_low_f, avg_temp_high_f = fetch_weather(chosen_city, departure_date_start)
token = get_access_token()
avg_flight_price = get_average_flight_price(token, start_iata_code, destination_iata_code, departure_date_start, num_adults)

print(f"\nWeather forecast for {chosen_city} on {format_date(departure_date_start)}:")
print(f"    Low Temp: {avg_temp_low_f}F")
print(f"    High Temp: {avg_temp_high_f}F")
print(f"\nAverage flight price from {start_location} to {chosen_city} on {format_date(departure_date_start)}: ${avg_flight_price:.2f}")
