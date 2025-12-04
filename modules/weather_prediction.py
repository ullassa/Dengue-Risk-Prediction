import os
import requests
import logging
from datetime import datetime
import pandas as pd
from .location_validator import KarnatakaLocationValidator

class WeatherPredictor:
    def __init__(self):
        # Try to load from environment variable or config file
        self.api_key = self._load_api_key()
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Initialize Karnataka location validator
        self.location_validator = KarnatakaLocationValidator()
        
        # Check if API key is properly configured
        if self.api_key in ['demo_key', 'your_actual_api_key_here', None]:
            logging.warning("OpenWeatherMap API key not configured. Using mock data.")
    
    def _load_api_key(self):
        """Load API key from environment variable or .env file"""
        # First try environment variable
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if api_key:
            return api_key
            
        # Try to read from .env file
        try:
            env_path = '.env'
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('OPENWEATHER_API_KEY='):
                            return line.split('=', 1)[1].strip()
        except Exception as e:
            logging.warning(f"Could not read .env file: {e}")
        
        # Default fallback
        return 'demo_key'
        
    def get_weather_data(self, city):
        """Fetch current weather data from OpenWeatherMap API or use mock data"""
        try:
            # If API key is not properly configured, use mock data
            if self.api_key == 'demo_key' or self.api_key == 'your_actual_api_key_here':
                return self.get_mock_weather_data(city)
            
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                logging.warning("Invalid API key. Using mock data instead.")
                return self.get_mock_weather_data(city)
            elif response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the city name.")
            elif response.status_code != 200:
                logging.warning(f"Weather API error: {response.status_code}. Using mock data.")
                return self.get_mock_weather_data(city)
            
            data = response.json()
            
            # Get rainfall data if available (from recent weather)
            rainfall = 0
            if 'rain' in data:
                rainfall = data['rain'].get('1h', 0)  # 1-hour rainfall
            
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'rainfall': rainfall
            }
        except requests.exceptions.Timeout:
            logging.warning("Request timeout. Using mock data.")
            return self.get_mock_weather_data(city)
        except requests.exceptions.RequestException as e:
            logging.warning(f"Network error: {str(e)}. Using mock data.")
            return self.get_mock_weather_data(city)
        except Exception as e:
            logging.warning(f"Weather data error: {str(e)}. Using mock data.")
            return self.get_mock_weather_data(city)
    
    def get_mock_weather_data(self, city):
        """Provide mock weather data when API is not available"""
        # Use data from your weather_history.csv for realistic mock data
        try:
            import random
            weather_file = 'datasets/weather_history.csv'
            if os.path.exists(weather_file):
                df = pd.read_csv(weather_file)
                city_data = df[df['City'].str.lower() == city.lower()]
                
                if not city_data.empty:
                    # Use the latest record for this city
                    latest = city_data.iloc[-1]
                    return {
                        'city': latest['City'],
                        'country': 'IN',
                        'temperature': float(latest['Temperature(C)']),
                        'humidity': float(latest['Humidity(%)']),
                        'pressure': 1013.25,  # Standard pressure
                        'description': 'partly cloudy',
                        'feels_like': float(latest['Temperature(C)']) + random.uniform(-2, 3),
                        'temp_min': float(latest['Temperature(C)']) - 2,
                        'temp_max': float(latest['Temperature(C)']) + 3,
                        'rainfall': float(latest['Rainfall(mm)'])
                    }
        except Exception as e:
            logging.error(f"Error reading local weather data: {str(e)}")
        
        # Fallback mock data based on typical Bangalore weather
        mock_data = {
            'Bangalore': {'temp': 26, 'humidity': 75, 'rainfall': 5},
            'Mysore': {'temp': 25, 'humidity': 80, 'rainfall': 8},
            'Hubli': {'temp': 28, 'humidity': 70, 'rainfall': 3},
            'Mangalore': {'temp': 29, 'humidity': 85, 'rainfall': 12},
            'Belgaum': {'temp': 25, 'humidity': 83, 'rainfall': 10}
        }
        
        city_key = next((k for k in mock_data.keys() if k.lower() == city.lower()), 'Bangalore')
        base_data = mock_data[city_key]
        
        return {
            'city': city.title(),
            'country': 'IN',
            'temperature': base_data['temp'],
            'humidity': base_data['humidity'],
            'pressure': 1013.25,
            'description': 'mock data - partly cloudy',
            'feels_like': base_data['temp'] + 2,
            'temp_min': base_data['temp'] - 2,
            'temp_max': base_data['temp'] + 3,
            'rainfall': base_data['rainfall']
        }
    
    def predict_risk(self, city):
        """Predict dengue risk based on weather conditions (Karnataka cities only)"""
        try:
            # Validate that the city is in Karnataka
            is_valid, normalized_city, suggestions = self.location_validator.validate_and_normalize(city)
            
            if not is_valid:
                logging.warning(f"Invalid Karnataka city: {city}")
                return {
                    'city': city,
                    'risk_level': 'Invalid Location',
                    'risk_color': 'secondary', 
                    'risk_score': 0,
                    'temperature': 0,
                    'humidity': 0,
                    'rainfall': 0,
                    'risk_factors': [],
                    'recommendations': [
                        f"📍 This system only provides weather-based dengue risk for Karnataka cities",
                        f"🏠 Suggested Karnataka cities: {', '.join(suggestions)}" if suggestions else "🏠 Try cities like Bangalore, Mysore, Mangalore",
                        f"📋 Available cities: {', '.join(self.location_validator.get_karnataka_cities_list()[:6])}...",
                        f"🔍 Please enter a valid Karnataka city name"
                    ],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data_source': 'Karnataka weather data only',
                    'suggestions': suggestions
                }
            
            weather_data = self.get_weather_data(normalized_city)
            
            temperature = weather_data['temperature']
            humidity = weather_data['humidity']
            rainfall = weather_data['rainfall']
            
            # Rule-based dengue risk prediction with your specific thresholds
            risk_factors = []
            risk_explanations = []
            
            # Temperature: Optimal for dengue = 25°C to 30°C
            temp_risk = "Low"
            if 25 <= temperature <= 30:
                temp_risk = "High"
                risk_factors.append("temperature")
                risk_explanations.append(f"🌡️ Optimal temperature for dengue mosquito breeding: {temperature}°C (25-30°C range)")
            elif 20 <= temperature < 25 or 30 < temperature <= 35:
                temp_risk = "Moderate"
                risk_explanations.append(f"🌡️ Moderate temperature for mosquito activity: {temperature}°C")
            else:
                risk_explanations.append(f"🌡️ Temperature not ideal for dengue transmission: {temperature}°C")
            
            # Humidity: > 70% increases risk
            humidity_risk = "Low"
            if humidity > 70:
                humidity_risk = "High"
                risk_factors.append("humidity")
                risk_explanations.append(f"💧 High humidity increases dengue risk: {humidity}% (>70% threshold)")
            else:
                risk_explanations.append(f"💧 Humidity level acceptable: {humidity}%")
            
            # Rainfall: More than 10mm = high breeding condition
            rainfall_risk = "Low"
            if rainfall > 10:
                rainfall_risk = "High"
                risk_factors.append("rainfall")
                risk_explanations.append(f"🌧️ High rainfall creates breeding sites: {rainfall}mm (>10mm threshold)")
            elif rainfall > 0:
                risk_explanations.append(f"🌧️ Light rainfall detected: {rainfall}mm")
            else:
                risk_explanations.append("🌧️ No recent rainfall detected")
            
            # Determine overall risk level
            high_risk_factors = len(risk_factors)
            if high_risk_factors >= 2:
                overall_risk = "High"
                risk_color = "danger"
                alert_message = "⚠️ HIGH DENGUE RISK - Multiple favorable conditions for mosquito breeding detected!"
            elif high_risk_factors == 1:
                overall_risk = "Moderate"
                risk_color = "warning"  
                alert_message = "⚠️ MODERATE DENGUE RISK - Some conditions favor mosquito activity"
            else:
                overall_risk = "Low"
                risk_color = "success"
                alert_message = "✅ LOW DENGUE RISK - Weather conditions not optimal for mosquito breeding"
            
            # Safety recommendations based on risk level
            if overall_risk == "High":
                recommendations = [
                    "🚨 Remove all stagnant water sources immediately",
                    "🦟 Use mosquito repellents and nets consistently", 
                    "👕 Wear long-sleeved clothing, especially during dawn and dusk",
                    "🏥 Seek medical attention immediately if fever develops",
                    "🏘️ Alert neighbors and community about high risk conditions"
                ]
            elif overall_risk == "Moderate":
                recommendations = [
                    "🔍 Check for and remove stagnant water weekly",
                    "🦟 Use mosquito repellents during peak mosquito hours",
                    "🏠 Keep surroundings clean and well-ventilated",
                    "🌡️ Monitor for dengue symptoms (fever, headache, body pain)",
                    "💡 Maintain awareness of local dengue alerts"
                ]
            else:
                recommendations = [
                    "✅ Continue regular dengue prevention measures",
                    "🧹 Maintain clean surroundings",
                    "👀 Stay alert for weather changes",
                    "📰 Keep updated with local health advisories"
                ]
            
            return {
                'risk_level': overall_risk,
                'risk_color': risk_color,
                'alert_message': alert_message,
                'weather_data': weather_data,
                'risk_explanations': risk_explanations,
                'recommendations': recommendations,
                'temperature_risk': temp_risk,
                'humidity_risk': humidity_risk,
                'rainfall_risk': rainfall_risk,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logging.error(f"Risk prediction error: {str(e)}")
            raise e
