import requests

api_key = '830EAF02FED34ECA84AE468CFDC2423E'
location_id = '616578'  # Replace with a valid TripAdvisor location ID
url = f'https://api.tripadvisor.com/api/partner/2.0/location/{location_id}'

headers = {
    'X-TripAdvisor-API-Key': api_key
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())  # Successful API call
else:
    print(f"Error: {response.status_code}, {response.text}")
