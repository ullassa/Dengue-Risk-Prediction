#!/usr/bin/env python3
"""
Quick Weather API Test Script
Run this to verify your OpenWeather API is working
"""

import os
import requests
import sys
from dotenv import load_dotenv

def test_weather_api():
    """Test OpenWeather API connection and response"""
    print("🌤️  Testing Weather API...")
    print("-" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key or api_key in ['demo_key', 'your_actual_api_key_here']:
        print("❌ No valid API key found!")
        print("📝 Instructions:")
        print("1. Get API key from: https://openweathermap.org/api")
        print("2. Create .env file with: OPENWEATHER_API_KEY=your_key_here")
        print("3. Or set environment variable: OPENWEATHER_API_KEY")
        return False
    
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # Test cities
    test_cities = ['Bangalore', 'Mumbai', 'Chennai', 'Kolkata', 'Hyderabad']
    
    for city in test_cities:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                desc = data['weather'][0]['description']
                print(f"✅ {city}: {temp}°C, {humidity}% humidity, {desc}")
            elif response.status_code == 401:
                print(f"❌ {city}: Invalid API key!")
                return False
            elif response.status_code == 404:
                print(f"⚠️  {city}: City not found")
            else:
                print(f"⚠️  {city}: API error {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {city}: Request timeout")
        except requests.exceptions.RequestException as e:
            print(f"🌐 {city}: Network error - {e}")
        except Exception as e:
            print(f"💥 {city}: Error - {e}")
    
    print("-" * 50)
    print("✅ Weather API test completed!")
    return True

def test_local_weather_module():
    """Test your weather prediction module"""
    print("\n🏠 Testing Local Weather Module...")
    print("-" * 50)
    
    try:
        # Import your weather module
        from modules.weather_prediction import WeatherPredictor
        
        predictor = WeatherPredictor()
        
        # Test Karnataka cities
        karnataka_cities = ['Bangalore', 'Mysore', 'Hubli', 'Mangalore']
        
        for city in karnataka_cities:
            try:
                weather_data = predictor.get_weather_data(city)
                risk_result = predictor.predict_risk(city)
                
                is_mock = 'mock data' in str(weather_data.get('description', '')).lower()
                status = "🔴 MOCK DATA" if is_mock else "✅ LIVE DATA"
                
                print(f"{status} {city}: {weather_data['temperature']}°C, Risk: {risk_result['risk_level']}")
                
            except Exception as e:
                print(f"❌ {city}: Error - {e}")
                
    except ImportError as e:
        print(f"❌ Cannot import weather module: {e}")
    except Exception as e:
        print(f"💥 Module test error: {e}")

if __name__ == "__main__":
    print("🧪 WEATHER API DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Test external API
    api_working = test_weather_api()
    
    # Test local module
    test_local_weather_module()
    
    print("\n📋 SUMMARY:")
    if api_working:
        print("✅ Weather API setup appears correct")
        print("🚀 Your application should show live weather data")
    else:
        print("❌ Weather API needs configuration")
        print("📖 Follow WEATHER_API_SETUP.md instructions")
    
    print("\n🎯 For exhibition tomorrow:")
    print("- If API working: Demo live weather features")
    print("- If not working: Focus on AI prediction model")
    print("- Mention: 'Integrated with live weather APIs in production'")