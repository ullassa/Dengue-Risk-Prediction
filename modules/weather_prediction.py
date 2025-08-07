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
            
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max']
            }
        except requests.exceptions.Timeout:
            raise Exception("Request timeout. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Weather data error: {str(e)}")
    
    def predict_risk(self, city):
        """Predict dengue risk based on weather conditions"""
        try:
            weather_data = self.get_weather_data(city)
            
            temperature = weather_data['temperature']
            humidity = weather_data['humidity']
            
            # Rule-based dengue risk prediction
            risk_score = 0
            risk_factors = []
            
            # Temperature factor (optimal range: 25-30°C)
            if 25 <= temperature <= 30:
                risk_score += 3
                risk_factors.append(f"Optimal temperature for mosquito breeding ({temperature}°C)")
            elif 20 <= temperature < 25 or 30 < temperature <= 35:
                risk_score += 2
                risk_factors.append(f"Moderate temperature for mosquito activity ({temperature}°C)")
            elif temperature > 35:
                risk_score += 1
                risk_factors.append(f"High temperature may reduce mosquito activity ({temperature}°C)")
            
            # Humidity factor (high humidity increases risk)
            if humidity >= 70:
                risk_score += 3
                risk_factors.append(f"High humidity favorable for mosquitoes ({humidity}%)")
            elif humidity >= 50:
                risk_score += 2
                risk_factors.append(f"Moderate humidity ({humidity}%)")
            else:
                risk_score += 1
                risk_factors.append(f"Low humidity may reduce mosquito survival ({humidity}%)")
            
            # Determine risk level
            if risk_score >= 5:
                risk_level = "High"
                risk_color = "danger"
                recommendations = [
                    "Remove all stagnant water sources immediately",
                    "Use mosquito repellents and nets",
                    "Wear long-sleeved clothing",
                    "Seek medical attention if you develop fever",
                    "Increase community awareness about dengue prevention"
                ]
            elif risk_score >= 3:
                risk_level = "Medium"
                risk_color = "warning"
                recommendations = [
                    "Check for and remove stagnant water weekly",
                    "Use mosquito repellents during peak hours",
                    "Keep surroundings clean",
                    "Monitor for dengue symptoms",
                    "Maintain good ventilation"
                ]
            else:
                risk_level = "Low"
                risk_color = "success"
                recommendations = [
                    "Continue regular preventive measures",
                    "Stay alert for changing weather conditions",
                    "Maintain clean surroundings",
                    "Keep water storage containers covered"
                ]
            
            return {
                'risk_level': risk_level,
                'risk_color': risk_color,
                'risk_score': risk_score,
                'weather_data': weather_data,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logging.error(f"Risk prediction error: {str(e)}")
            raise e
