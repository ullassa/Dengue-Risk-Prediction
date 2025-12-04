from modules.weather_prediction import WeatherPredictor

print('Testing weather-based dengue prediction...')
wp = WeatherPredictor()
result = wp.predict_risk('Bangalore')

print('\nWeather-based prediction result:')
print(f"City: {result['city']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['risk_score']}")
print(f"Temperature: {result['temperature']}°C")
print(f"Humidity: {result['humidity']}%")
print(f"Rainfall: {result['rainfall']}mm")
print(f"Data Source: {result['data_source']}")

print('\nRisk Factors:')
for factor in result['risk_factors']:
    print(f'  - {factor}')

print('\nRecommendations:')
for rec in result['recommendations']:
    print(f'  - {rec}')