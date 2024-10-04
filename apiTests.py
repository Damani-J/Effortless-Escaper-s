import requests
import pandas as pd
from datetime import datetime

WEATHER_API_KEY = 'cd429d175aba4e43af731417242009'
AMADEUS_API_KEY = 'NMPtPNqSeWRp3G7iqmvA2lBTU5GA14er'
AMADEUS_API_SECRET = 'VZmM4osAyKc2KUGY'
#TRIPADVISOR_API = '830EAF02FED34ECA84AE468CFDC2423E'

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
    
    if 'forecast' not in data:
        return None, None
    
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

def get_average_flight_price(access_token, origin, destination, departure_date):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': departure_date,
        'adults': 1,
        'max': 5
    }
    response = requests.get(url, headers=headers, params=params)
    flight_offers = response.json().get('data', [])
    
    if not flight_offers:
        return 0
    
    total_price = 0
    count = len(flight_offers)
    for offer in flight_offers:
        total_price += float(offer['price']['total'])
    
    average_price = total_price / count if count > 0 else 0
    return average_price

start_location = input("Starting location (city): ")
start_airport_code = input(f"Airport code for {start_location}: ")
destination_location = input("Destination location (city): ")
destination_airport_code = input(f"Airport code for {destination_location}: ")
input_date = input("Date of your trip (MM/DD/YYYY): ")

departure_date = convert_date_for_api(input_date)

formatted_date = format_date(departure_date)

token = get_access_token()

avg_temp_low_f, avg_temp_high_f = fetch_weather(destination_location, departure_date)
avg_flight_price = get_average_flight_price(token, start_airport_code, destination_airport_code, departure_date)

if avg_temp_low_f is None or avg_temp_high_f is None:
    print(f"Could not retrieve weather data for {destination_location} on {formatted_date}.")
else:
    print(f"Weather forecast for {destination_location} on {formatted_date}:")
    print(f"    Low Temp: {avg_temp_low_f}F")
    print(f"    High Temp: {avg_temp_high_f}F")

if avg_flight_price == 0:
    print(f"Could not find any flight offers from {start_location} ({start_airport_code}) to {destination_location} ({destination_airport_code}) on {formatted_date}.")
else:
    print(f"Average flight price from {start_location} ({start_airport_code}) to {destination_location} ({destination_airport_code}) on {formatted_date}: ${avg_flight_price:.2f}")
