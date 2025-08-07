import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from modules.weather_prediction import WeatherPredictor
from modules.symptom_checker import SymptomChecker
from modules.local_alert import LocalAlert
from modules.risk_calculator import RiskCalculator
from modules.visualizer import Visualizer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dengue_prediction_secret_key")

# Initialize modules
weather_predictor = WeatherPredictor()
symptom_checker = SymptomChecker()
local_alert = LocalAlert()
risk_calculator = RiskCalculator()
visualizer = Visualizer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/weather-prediction', methods=['GET', 'POST'])
def weather_prediction():
    """Weather-based dengue risk prediction"""
    if request.method == 'POST':
        try:
            city = request.form.get('city', '').strip()
            if not city:
                flash('Please enter a city name', 'error')
                return render_template('weather_prediction.html')
            
            result = weather_predictor.predict_risk(city)
            return render_template('result.html', 
                                 result=result, 
                                 module='Weather Prediction',
                                 back_url=url_for('weather_prediction'))
        except Exception as e:
            logging.error(f"Weather prediction error: {str(e)}")
            flash(f'Error getting weather data: {str(e)}', 'error')
            return render_template('weather_prediction.html')
    
    return render_template('weather_prediction.html')

@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker_route():
    """Symptom-based dengue risk assessment"""
    if request.method == 'POST':
        try:
            symptoms = {
                'fever': 'fever' in request.form,
                'headache': 'headache' in request.form,
                'joint_pain': 'joint_pain' in request.form,
                'muscle_pain': 'muscle_pain' in request.form,
                'rash': 'rash' in request.form,
                'nausea': 'nausea' in request.form,
                'vomiting': 'vomiting' in request.form,
                'bleeding': 'bleeding' in request.form
            }
            
            result = symptom_checker.check_symptoms(symptoms)
            return render_template('result.html', 
                                 result=result, 
                                 module='Symptom Checker',
                                 back_url=url_for('symptom_checker_route'))
        except Exception as e:
            logging.error(f"Symptom checker error: {str(e)}")
            flash(f'Error processing symptoms: {str(e)}', 'error')
            return render_template('symptom_checker.html')
    
    return render_template('symptom_checker.html')

@app.route('/local-alert', methods=['GET', 'POST'])
def local_alert_route():
    """Local dengue alert system"""
    if request.method == 'POST':
        try:
            location = request.form.get('location', '').strip()
            if not location:
                flash('Please enter a location', 'error')
                return render_template('local_alert.html')
            
            result = local_alert.check_local_risk(location)
            return render_template('result.html', 
                                 result=result, 
                                 module='Local Alert',
                                 back_url=url_for('local_alert_route'))
        except Exception as e:
            logging.error(f"Local alert error: {str(e)}")
            flash(f'Error checking local alerts: {str(e)}', 'error')
            return render_template('local_alert.html')
    
    return render_template('local_alert.html')

@app.route('/risk-calculator', methods=['GET', 'POST'])
def risk_calculator_route():
    """Score-based dengue risk calculator"""
    if request.method == 'POST':
        try:
            factors = {
                'stagnant_water': 'stagnant_water' in request.form,
                'mosquito_increase': 'mosquito_increase' in request.form,
                'recent_travel': 'recent_travel' in request.form,
                'sick_contacts': 'sick_contacts' in request.form,
                'poor_drainage': 'poor_drainage' in request.form,
                'water_storage': 'water_storage' in request.form,
                'garden_plants': 'garden_plants' in request.form,
                'construction_nearby': 'construction_nearby' in request.form,
                'ac_cooler': 'ac_cooler' in request.form,
                'garbage_collection': 'garbage_collection' in request.form
            }
            
            result = risk_calculator.calculate_risk(factors)
            return render_template('result.html', 
                                 result=result, 
                                 module='Risk Calculator',
                                 back_url=url_for('risk_calculator_route'))
        except Exception as e:
            logging.error(f"Risk calculator error: {str(e)}")
            flash(f'Error calculating risk: {str(e)}', 'error')
            return render_template('risk_calculator.html')
    
    return render_template('risk_calculator.html')

@app.route('/visualization')
def visualization():
    """Spatio-temporal visualization of dengue data"""
    try:
        # Generate visualization data
        charts_data = visualizer.generate_charts()
        return render_template('visualization.html', charts_data=charts_data)
    except Exception as e:
        logging.error(f"Visualization error: {str(e)}")
        flash(f'Error generating visualizations: {str(e)}', 'error')
        return render_template('visualization.html', charts_data=None)

@app.route('/prevention')
def prevention():
    """Prevention and awareness hub"""
    return render_template('prevention.html')

@app.route('/api/map-data')
def map_data():
    """API endpoint for map data"""
    try:
        data = visualizer.get_map_data()
        return jsonify(data)
    except Exception as e:
        logging.error(f"Map data error: {str(e)}")
        return jsonify({'error': 'Failed to load map data'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
