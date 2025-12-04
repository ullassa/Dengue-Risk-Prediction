import requests

print('Testing new OpenWeatherMap API key...')

# Test direct API call
api_key = "c627de2557cfd02f7cc3c5035b800065"
url = f"http://api.openweathermap.org/data/2.5/weather?q=Bangalore&appid={api_key}&units=metric"

try:
    response = requests.get(url, timeout=10)
    print(f"API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Working! Live weather in {data['name']}:")
        print(f"   Temperature: {data['main']['temp']}°C")
        print(f"   Humidity: {data['main']['humidity']}%")
        print(f"   Description: {data['weather'][0]['description']}")
        print(f"   Feels like: {data['main']['feels_like']}°C")
        print(f"   Country: {data['sys']['country']}")
    elif response.status_code == 401:
        print("❌ Invalid or expired API key")
    elif response.status_code == 429:
        print("⚠️ API rate limit exceeded")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection error: {e}")