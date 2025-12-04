from modules.weather_prediction import WeatherPredictor
import requests

print('Testing OpenWeatherMap API...')
wp = WeatherPredictor()

# Test direct API call
api_key = "60f371cbc32bb1b9e2af04677dd6b654"
url = f"http://api.openweathermap.org/data/2.5/weather?q=Bangalore&appid={api_key}&units=metric"

try:
    response = requests.get(url, timeout=10)
    print(f"API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Working! Current weather in {data['name']}:")
        print(f"   Temperature: {data['main']['temp']}°C")
        print(f"   Humidity: {data['main']['humidity']}%")
        print(f"   Description: {data['weather'][0]['description']}")
    elif response.status_code == 401:
        print("❌ Invalid or expired API key")
    elif response.status_code == 429:
        print("⚠️ API rate limit exceeded")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection error: {e}")

# Test weather prediction
print("\nTesting weather prediction...")
result = wp.predict_risk('Bangalore')
print(f"Risk Level: {result['risk_level']}")
print(f"Weather Data Source: {'Live API' if result['weather_data'].get('country') == 'IN' else 'Mock Data'}")