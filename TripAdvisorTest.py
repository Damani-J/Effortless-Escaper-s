import requests

def search_locations(keywords):
    api_key = "28DB21DB31E2437EA53EA73A21C31A25"
    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    
    search_query = ' '.join(keywords)
    
    params = {"key": api_key, "searchQuery": search_query, "language": "en"}

    response = requests.get(url, params=params).json()
    print(f"Based on your given input these are the top 3 locations:")

    for location in response['data'][:3]:
        address_obj = location.get('address_obj', {})
        print(f"    - {location['name']}: {address_obj.get('address_string', 'Address not available')}")

user_input = input("Enter keywords to find the perfect destination: ")

keywords = [keyword.strip() for keyword in user_input.split(",")]

search_locations(keywords)
