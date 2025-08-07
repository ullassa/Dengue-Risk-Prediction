import os
import requests
import logging
from datetime import datetime
import pandas as pd

class WeatherPredictor:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather_data(self, city):
        """Fetch current weather data from OpenWeatherMap API"""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                raise Exception("Invalid API key. Please check your OpenWeatherMap API key.")
            elif response.status_code == 404:
                raise Exception(f"City '{city}' not found. Please check the city name.")
            elif response.status_code != 200:
                raise Exception(f"Weather API error: {response.status_code}")
            
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
            raise Exception("Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Weather data error: {str(e)}")
    
    def predict_risk(self, city):
        """Predict dengue risk based on weather conditions using your specific rules"""
        try:
            weather_data = self.get_weather_data(city)
            
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
