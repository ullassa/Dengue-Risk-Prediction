import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from modules.weather_prediction import WeatherPredictor
from modules.symptom_checker import SymptomChecker
from modules.local_alert import LocalAlert
from modules.risk_calculator import RiskCalculator
from modules.visualizer import Visualizer

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dengue_prediction_secret_key")

# Database configuration
# Try PostgreSQL first, fallback to SQLite
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dengue_users.db'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    histories = db.relationship('History', backref='user', lazy=True, cascade='all, delete-orphan')

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin-only decorator
def admin_required(f):
    """Decorator to require admin privileges for accessing a route"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Initialize modules
weather_predictor = WeatherPredictor()
symptom_checker = SymptomChecker()
local_alert = LocalAlert()
risk_calculator = RiskCalculator()
visualizer = Visualizer()

# Create database tables
with app.app_context():
    db.create_all()

# Authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Validation
            if not name or not email or not password:
                flash('All fields are required', 'error')
                return render_template('auth/signup.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('auth/signup.html')
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already registered', 'error')
                return render_template('auth/signup.html')
            
            # Create new user
            password_hash = generate_password_hash(password)
            user = User(name=name, email=email, password_hash=password_hash)
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            logging.error(f"Signup error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/signup.html')
    
    return render_template('auth/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Email and password are required', 'error')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash(f'Welcome back, {user.name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
                return render_template('auth/login.html')
                
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Landing page - redirects to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with risk check history"""
    try:
        # Get user's recent risk check history (last 10)
        history = History.query.filter_by(user_id=current_user.id)\
                               .order_by(History.date_time.desc())\
                               .limit(10)\
                               .all()
        
        # Get some stats
        total_checks = History.query.filter_by(user_id=current_user.id).count()
        recent_cities = db.session.query(History.city_name)\
                                  .filter_by(user_id=current_user.id)\
                                  .distinct()\
                                  .limit(5)\
                                  .all()
        recent_cities = [city[0] for city in recent_cities]
        
        return render_template('dashboard.html', 
                             history=history, 
                             total_checks=total_checks,
                             recent_cities=recent_cities)
    except Exception as e:
        logging.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard data', 'error')
        return render_template('dashboard.html', history=[], total_checks=0, recent_cities=[])

def save_weather_history(user_id, city, result):
    """Save weather prediction to user's history"""
    try:
        history = History(
            user_id=user_id,
            city_name=city,
            risk_level=result.get('risk_level', 'Unknown'),
            temperature=result.get('weather_data', {}).get('temperature', None),
            humidity=result.get('weather_data', {}).get('humidity', None),
            date_time=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error saving weather history: {str(e)}")

@app.route('/weather-prediction', methods=['GET', 'POST'])
@login_required
def weather_prediction():
    """Weather-based dengue risk prediction"""
    if request.method == 'POST':
        try:
            city = request.form.get('city', '').strip()
            if not city:
                flash('Please enter a city name', 'error')
                return render_template('weather_prediction.html')
            
            result = weather_predictor.predict_risk(city)
            
            # Save to user's history
            save_weather_history(current_user.id, city, result)
            
            return render_template('result.html', 
                                 result=result, 
                                 module='Weather Prediction',
                                 back_url='weather-prediction')
        except Exception as e:
            logging.error(f"Weather prediction error: {str(e)}")
            flash(f'Error getting weather data: {str(e)}', 'error')
            return render_template('weather_prediction.html')
    
    return render_template('weather_prediction.html')

@app.route('/symptom-checker', methods=['GET', 'POST'])
@login_required
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
                                 back_url='symptom-checker')
        except Exception as e:
            logging.error(f"Symptom checker error: {str(e)}")
            flash(f'Error processing symptoms: {str(e)}', 'error')
            return render_template('symptom_checker.html')
    
    return render_template('symptom_checker.html')

@app.route('/local-alert', methods=['GET', 'POST'])
@login_required
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
                                 back_url='local-alert')
        except Exception as e:
            logging.error(f"Local alert error: {str(e)}")
            flash(f'Error checking local alerts: {str(e)}', 'error')
            return render_template('local_alert.html')
    
    return render_template('local_alert.html')

@app.route('/risk-calculator', methods=['GET', 'POST'])
@login_required
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
                                 back_url='risk-calculator')
        except Exception as e:
            logging.error(f"Risk calculator error: {str(e)}")
            flash(f'Error calculating risk: {str(e)}', 'error')
            return render_template('risk_calculator.html')
    
    return render_template('risk_calculator.html')

@app.route('/visualization')
@login_required
def visualization():
    """Spatio-temporal visualization of dengue data"""
    try:
        # Generate visualization data
        charts_data = visualizer.generate_charts()
        map_data = visualizer.get_map_data()
        return render_template('visualization.html', charts_data=charts_data, map_data=map_data)
    except Exception as e:
        logging.error(f"Visualization error: {str(e)}")
        flash(f'Error generating visualizations: {str(e)}', 'error')
        return render_template('visualization.html', charts_data=None, map_data=None)

@app.route('/api/map-data')
def map_data_api():
    """API endpoint for map data"""
    try:
        map_data = visualizer.get_map_data()
        return jsonify(map_data)
    except Exception as e:
        logging.error(f"Map data API error: {str(e)}")
        return jsonify({'locations': [], 'message': 'Error loading map data'})

@app.route('/prevention')
@login_required
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

# Database Admin Interface
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard to view and manage user data"""
    try:
        # Get all users with their history counts
        users = db.session.query(User).all()
        user_data = []
        
        for user in users:
            user_info = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_admin': user.is_admin,
                'history_count': len(user.histories),
                'latest_activity': max([h.date_time for h in user.histories]) if user.histories else None
            }
            user_data.append(user_info)
        
        # Get total statistics
        total_users = len(users)
        total_predictions = db.session.query(History).count()
        
        return render_template('admin_dashboard.html', 
                             users=user_data, 
                             total_users=total_users,
                             total_predictions=total_predictions)
    except Exception as e:
        logging.error(f"Admin dashboard error: {str(e)}")
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    """View detailed information for a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        histories = History.query.filter_by(user_id=user_id).order_by(History.date_time.desc()).all()
        
        return render_template('admin_user_detail.html', 
                             user=user, 
                             histories=histories)
    except Exception as e:
        logging.error(f"Admin user detail error: {str(e)}")
        flash(f'Error loading user details: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/database-info')
@admin_required
def database_info():
    """Display database connection and table information"""
    try:
        # Get database connection info
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_type = "PostgreSQL" if "postgresql" in db_uri else "SQLite"
        
        # Get table information
        tables_info = []
        
        # User table info
        user_count = User.query.count()
        admin_count = User.query.filter_by(is_admin=True).count()
        tables_info.append({
            'name': 'Users',
            'count': user_count,
            'admin_count': admin_count,
            'columns': ['id', 'name', 'email', 'password_hash', 'is_admin']
        })
        
        # History table info  
        history_count = History.query.count()
        tables_info.append({
            'name': 'History',
            'count': history_count,
            'columns': ['id', 'user_id', 'city_name', 'risk_level', 'temperature', 'humidity', 'date_time']
        })
        
        return render_template('database_info.html', 
                             db_type=db_type,
                             db_uri=db_uri,
                             tables=tables_info)
    except Exception as e:
        logging.error(f"Database info error: {str(e)}")
        flash(f'Error loading database information: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
