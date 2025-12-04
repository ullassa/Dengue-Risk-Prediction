import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from modules.weather_prediction import WeatherPredictor
from modules.symptom_checker import SymptomChecker
from modules.local_alert import LocalAlert
from modules.risk_calculator import RiskCalculator
from modules.ai_predictor import DengueOutbreakPredictor
from modules.visualizer import Visualizer
from modules.doctor_consultation import doctor_bp, doctor_consultation

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
    # Handle Render PostgreSQL URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"Using PostgreSQL: {database_url}")
else:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dengue_users.db'
    print("Using SQLite for development")
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Register blueprints
app.register_blueprint(doctor_bp, url_prefix='/doctor')

# Custom Jinja2 filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    if not value:
        return []
    try:
        import json
        return json.loads(value)
    except:
        return []

# Template context processors
@app.context_processor
def inject_template_vars():
    """Inject common template variables"""
    from datetime import date
    return {
        'today': date.today().strftime('%Y-%m-%d'),
        'current_year': date.today().year
    }

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Profile Information
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True, default='Karnataka')
    occupation = db.Column(db.String(100), nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)  # JSON string for storing conditions
    emergency_contact = db.Column(db.String(100), nullable=True)
    emergency_phone = db.Column(db.String(20), nullable=True)
    
    # Profile Settings
    notification_preferences = db.Column(db.Text, nullable=True)  # JSON string
    profile_visibility = db.Column(db.String(20), default='private', nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    histories = db.relationship('History', backref='user', lazy=True, cascade='all, delete-orphan')
    experiences = db.relationship('DengueExperience', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def get_age_group(self):
        """Return age group category"""
        if not self.age:
            return 'Unknown'
        if self.age < 18:
            return 'Minor (Under 18)'
        elif self.age < 30:
            return 'Young Adult (18-29)'
        elif self.age < 50:
            return 'Adult (30-49)'
        elif self.age < 65:
            return 'Middle Age (50-64)'
        else:
            return 'Senior (65+)'
    
    def get_medical_conditions_list(self):
        """Return medical conditions as a list"""
        if not self.medical_conditions:
            return []
        try:
            import json
            return json.loads(self.medical_conditions)
        except:
            return []
    
    def set_medical_conditions(self, conditions_list):
        """Set medical conditions from a list"""
        import json
        self.medical_conditions = json.dumps(conditions_list) if conditions_list else None
    
    def get_medical_conditions(self):
        """Get medical conditions as a list"""
        return self.get_medical_conditions_list()
    
    def get_emergency_contact(self):
        """Get emergency contact information as a dictionary"""
        if self.emergency_contact:
            return {
                'name': self.emergency_contact,
                'phone': self.emergency_phone or ''
            }
        return {'name': '', 'phone': ''}
    
    def get_notification_preferences(self):
        """Get notification preferences as a dictionary"""
        if self.notification_preferences:
            try:
                import json
                return json.loads(self.notification_preferences)
            except json.JSONDecodeError:
                return {}
        return {
            'dengue_alerts': True,
            'risk_updates': True,
            'health_tips': False,
            'weekly_reports': False,
            'profile_visibility': True,
            'anonymous_data': True
        }
    
    def get_days_active(self):
        """Calculate days since user joined"""
        if self.date_joined:
            return (datetime.utcnow() - self.date_joined).days
        return 0

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    """Model to track user activities for analytics and export"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for anonymous users
    activity_type = db.Column(db.String(50), nullable=False)  # 'prediction', 'risk_calc', 'symptom_check', etc.
    page_visited = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)  # JSON string with activity details
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.String(200))
    session_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON export"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Anonymous',
            'activity_type': self.activity_type,
            'page_visited': self.page_visited,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat()
        }

class DengueExperience(db.Model):
    """Model to track user's dengue experiences - infection, recovery, treatments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic Information
    experience_type = db.Column(db.String(20), nullable=False)  # 'infection', 'recovery', 'update'
    status = db.Column(db.String(20), default='active')  # 'active', 'recovered', 'ongoing'
    
    # Dates
    infection_date = db.Column(db.Date, nullable=True)
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    recovery_date = db.Column(db.Date, nullable=True)
    
    # Symptoms and Severity
    symptoms = db.Column(db.Text)  # JSON array of symptoms
    severity_level = db.Column(db.String(20))  # 'mild', 'moderate', 'severe', 'critical'
    max_fever_temp = db.Column(db.Float, nullable=True)
    
    # Location and Circumstances
    location_infected = db.Column(db.String(100))  # Where they think they got infected
    circumstances = db.Column(db.Text)  # What they think led to infection
    prevention_used = db.Column(db.Text)  # What prevention they were using
    
    # Treatment and Care
    treatments_used = db.Column(db.Text)  # JSON array of treatments
    medications = db.Column(db.Text)  # Medications taken
    home_remedies = db.Column(db.Text)  # Home remedies used
    doctor_visits = db.Column(db.Integer, default=0)
    hospitalization = db.Column(db.Boolean, default=False)
    hospitalization_days = db.Column(db.Integer, nullable=True)
    
    # Recovery Progress
    recovery_notes = db.Column(db.Text)  # Updates on recovery progress
    lessons_learned = db.Column(db.Text)  # What they learned from the experience
    advice_for_others = db.Column(db.Text)  # Advice they'd give to others
    
    # Privacy and Sharing
    share_anonymously = db.Column(db.Boolean, default=True)  # Share data anonymously for research
    public_story = db.Column(db.Boolean, default=False)  # Make story public (anonymized)
    
    # Metadata
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON export"""
        import json
        return {
            'id': self.id,
            'user_name': self.user.name if not self.share_anonymously else 'Anonymous',
            'experience_type': self.experience_type,
            'status': self.status,
            'infection_date': self.infection_date.isoformat() if self.infection_date else None,
            'report_date': self.report_date.isoformat(),
            'recovery_date': self.recovery_date.isoformat() if self.recovery_date else None,
            'symptoms': json.loads(self.symptoms) if self.symptoms else [],
            'severity_level': self.severity_level,
            'max_fever_temp': self.max_fever_temp,
            'location_infected': self.location_infected,
            'circumstances': self.circumstances,
            'treatments_used': json.loads(self.treatments_used) if self.treatments_used else [],
            'medications': self.medications,
            'home_remedies': self.home_remedies,
            'doctor_visits': self.doctor_visits,
            'hospitalization': self.hospitalization,
            'hospitalization_days': self.hospitalization_days,
            'recovery_notes': self.recovery_notes,
            'lessons_learned': self.lessons_learned,
            'advice_for_others': self.advice_for_others,
            'last_updated': self.last_updated.isoformat()
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Activity tracking helper
def track_activity(activity_type, page_visited, details=None):
    """Track user activity in the database"""
    try:
        import json
        activity = UserActivity(
            user_id=current_user.id if current_user.is_authenticated else None,
            activity_type=activity_type,
            page_visited=page_visited,
            details=json.dumps(details) if details else None,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:200] if request.user_agent else None,
            session_id=session.get('_id', 'unknown')
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error tracking activity: {str(e)}")
        db.session.rollback()

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
ai_predictor = DengueOutbreakPredictor()

# Helper function to track user activities
def track_activity(activity_type, page_visited, details=None):
    """Track user activity in the database"""
    try:
        import json
        activity = UserActivity(
            user_id=current_user.id if current_user.is_authenticated else None,
            activity_type=activity_type,
            page_visited=page_visited,
            details=json.dumps(details) if details else None,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:200],
            session_id=session.get('_id', 'unknown')
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error tracking activity: {str(e)}")
        db.session.rollback()

# Create database tables
with app.app_context():
    db.create_all()

# Data Export API Routes
@app.route('/api/export/activities')
@login_required
def export_activities():
    """Export user activities with date filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        activity_type = request.args.get('activity_type')
        export_format = request.args.get('format', 'json')
        
        # Track the export activity
        track_activity('export', 'export_activities', f'Activities exported in {export_format} format, date range: {start_date} to {end_date}')
        
        # Build query with User join
        query = UserActivity.query.join(User, UserActivity.user_id == User.id)
        
        # Date filtering
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(UserActivity.timestamp >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(UserActivity.timestamp <= end_dt)
            
        # Activity type filtering
        if activity_type and activity_type != 'all':
            query = query.filter(UserActivity.activity_type == activity_type)
            
        # Admin can see all, regular users only their own
        if not current_user.is_admin:
            query = query.filter(UserActivity.user_id == current_user.id)
            
        activities = query.order_by(UserActivity.timestamp.desc()).all()
        
        if export_format == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            
            # CSV headers
            writer.writerow(['ID', 'User', 'Activity Type', 'Page', 'Details', 'IP Address', 'Timestamp'])
            
            for activity in activities:
                writer.writerow([
                    activity.id,
                    activity.user.name if activity.user else 'Anonymous',
                    activity.activity_type,
                    activity.page_visited,
                    activity.details or '',
                    activity.ip_address or '',
                    activity.timestamp.isoformat()
                ])
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=user_activities_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
            
        else:  # JSON format
            return jsonify({
                'success': True,
                'total_count': len(activities),
                'data': [activity.to_dict() for activity in activities],
                'filters_applied': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'activity_type': activity_type
                }
            })
            
    except Exception as e:
        logging.error(f"Export activities error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/history')
@login_required
def export_history():
    """Export user prediction history with date filtering"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export_format = request.args.get('format', 'json')
        
        # Track the export activity
        track_activity('export', 'export_history', f'History exported in {export_format} format, date range: {start_date} to {end_date}')
        
        query = History.query.join(User, History.user_id == User.id)
        
        # Date filtering
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(History.date_time >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(History.date_time <= end_dt)
            
        # Admin can see all, regular users only their own
        if not current_user.is_admin:
            query = query.filter(History.user_id == current_user.id)
            
        history = query.order_by(History.date_time.desc()).all()
        
        if export_format == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            
            writer.writerow(['ID', 'User', 'City', 'Risk Level', 'Temperature', 'Humidity', 'Date Time'])
            
            for record in history:
                writer.writerow([
                    record.id,
                    record.user.name,
                    record.city_name,
                    record.risk_level,
                    record.temperature or '',
                    record.humidity or '',
                    record.date_time.isoformat()
                ])
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=prediction_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
            
        else:  # JSON format
            return jsonify({
                'success': True,
                'total_count': len(history),
                'data': [{
                    'id': record.id,
                    'user_name': record.user.name,
                    'city_name': record.city_name,
                    'risk_level': record.risk_level,
                    'temperature': record.temperature,
                    'humidity': record.humidity,
                    'date_time': record.date_time.isoformat()
                } for record in history]
            })
            
    except Exception as e:
        logging.error(f"Export history error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration with comprehensive profile"""
    if request.method == 'POST':
        try:
            # Basic required fields
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Extended profile fields
            age = request.form.get('age')
            gender = request.form.get('gender', '').strip()
            phone = request.form.get('phone', '').strip()
            city = request.form.get('city', '').strip()
            occupation = request.form.get('occupation', '').strip()
            emergency_contact = request.form.get('emergency_contact', '').strip()
            emergency_phone = request.form.get('emergency_phone', '').strip()
            medical_conditions = request.form.getlist('medical_conditions')
            
            # Validation
            if not name or not email or not password:
                flash('Name, email, and password are required', 'error')
                return render_template('auth/signup.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('auth/signup.html')
            
            # Age validation
            if age:
                try:
                    age = int(age)
                    if age < 5 or age > 120:
                        flash('Please enter a valid age between 5 and 120', 'error')
                        return render_template('auth/signup.html')
                except ValueError:
                    flash('Please enter a valid age', 'error')
                    return render_template('auth/signup.html')
            else:
                age = None
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already registered', 'error')
                return render_template('auth/signup.html')
            
            # Create new user with extended profile
            password_hash = generate_password_hash(password)
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                age=age,
                gender=gender if gender else None,
                phone=phone if phone else None,
                city=city if city else None,
                occupation=occupation if occupation else None,
                emergency_contact=emergency_contact if emergency_contact else None,
                emergency_phone=emergency_phone if emergency_phone else None
            )
            
            # Set medical conditions
            if medical_conditions:
                user.set_medical_conditions([condition for condition in medical_conditions if condition.strip()])
            
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Your profile has been set up. Please log in.', 'success')
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

@app.route('/clear-messages')
def clear_messages():
    """Clear all flash messages"""
    from flask import session
    session.pop('_flashes', None)
    flash('Messages cleared', 'success')
    return redirect(url_for('index'))

@app.route('/test-route')
def test_route():
    """Test route to verify app is working"""
    return jsonify({
        'status': 'success',
        'message': 'App is working properly',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Landing page - redirects to dashboard if logged in"""
    track_activity('page_visit', 'index', 'Homepage visited')
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with risk check history"""
    track_activity('page_visit', 'dashboard', f'Dashboard accessed by {current_user.name}')
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

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    track_activity('page_visit', 'profile', f'Profile viewed by {current_user.name}')
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        try:
            # Update basic information
            current_user.name = request.form.get('name', '').strip()
            current_user.phone = request.form.get('phone', '').strip() or None
            current_user.city = request.form.get('city', '').strip() or None
            current_user.occupation = request.form.get('occupation', '').strip() or None
            current_user.emergency_contact = request.form.get('emergency_contact', '').strip() or None
            current_user.emergency_phone = request.form.get('emergency_phone', '').strip() or None
            
            # Update age
            age = request.form.get('age')
            if age:
                try:
                    age = int(age)
                    if 5 <= age <= 120:
                        current_user.age = age
                    else:
                        flash('Please enter a valid age between 5 and 120', 'error')
                        return render_template('edit_profile.html', user=current_user)
                except ValueError:
                    flash('Please enter a valid age', 'error')
                    return render_template('edit_profile.html', user=current_user)
            else:
                current_user.age = None
            
            # Update gender
            gender = request.form.get('gender', '').strip()
            current_user.gender = gender if gender else None
            
            # Update medical conditions
            medical_conditions = request.form.getlist('medical_conditions')
            current_user.set_medical_conditions([condition.strip() for condition in medical_conditions if condition.strip()])
            
            # Update notification preferences
            notification_prefs = {
                'email_alerts': 'email_alerts' in request.form,
                'dengue_alerts': 'dengue_alerts' in request.form,
                'weekly_summary': 'weekly_summary' in request.form
            }
            import json
            current_user.notification_preferences = json.dumps(notification_prefs)
            
            # Update profile visibility
            current_user.profile_visibility = request.form.get('profile_visibility', 'private')
            
            # Update timestamp
            current_user.last_updated = datetime.utcnow()
            
            db.session.commit()
            track_activity('profile_update', 'profile', f'Profile updated by {current_user.name}')
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            logging.error(f"Profile update error: {str(e)}")
            flash('Error updating profile. Please try again.', 'error')
            return render_template('edit_profile.html', user=current_user)
    
    return render_template('edit_profile.html', user=current_user)

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

def update_user_activity_counter(user_id, activity_type):
    """Update user activity counters"""
    try:
        user = User.query.get(user_id)
        if user:
            if activity_type == 'prediction':
                if user.total_predictions is None:
                    user.total_predictions = 0
                user.total_predictions += 1
            elif activity_type == 'risk_assessment':
                if user.risk_assessments is None:
                    user.risk_assessments = 0
                user.risk_assessments += 1
            elif activity_type == 'alert':
                if user.alerts_received is None:
                    user.alerts_received = 0
                user.alerts_received += 1
            
            user.last_updated = datetime.utcnow()
            db.session.commit()
    except Exception as e:
        logging.error(f"Error updating user activity: {str(e)}")

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
            
            # Update user activity counter
            update_user_activity_counter(current_user.id, 'prediction')
            
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
            
            # Track symptom check activity
            active_symptoms = [k for k, v in symptoms.items() if v]
            track_activity('symptom_check', 'symptom_checker', f'Symptom check with {len(active_symptoms)} symptoms: {", ".join(active_symptoms)}')
            
            # Update user activity counter
            update_user_activity_counter(current_user.id, 'risk_assessment')
            
            result = symptom_checker.check_symptoms(symptoms)
            return render_template('result.html', 
                                 result=result, 
                                 module='Symptom Checker',
                                 back_url='symptom-checker')
        except Exception as e:
            logging.error(f"Symptom checker error: {str(e)}")
            flash(f'Error processing symptoms: {str(e)}', 'error')
            return render_template('symptom_checker.html')
    else:
        track_activity('page_visit', 'symptom_checker', 'Symptom Checker page accessed')
    
    return render_template('symptom_checker.html')

@app.route('/local-alert', methods=['GET', 'POST'])
# @login_required  # Temporarily commented out for testing
def local_alert_route():
    """Local dengue alert system"""
    if request.method == 'POST':
        try:
            location = request.form.get('location', '').strip()
            if not location:
                flash('Please enter a location', 'error')
                return render_template('local_alert.html')
            
            result = local_alert.check_local_risk(location)
            
            # Update user activity counter
            update_user_activity_counter(current_user.id, 'alert')
            
            return render_template('local_alert_result.html', 
                                 result=result, 
                                 module='Local Alert',
                                 back_url='local-alert')
        except Exception as e:
            logging.error(f"Local alert error: {str(e)}")
            flash(f'Error checking local alerts: {str(e)}', 'error')
            return render_template('local_alert.html')
    
    return render_template('local_alert.html')

@app.route('/test-local-alert', methods=['GET', 'POST'])
def test_local_alert_route():
    """Test local dengue alert system without authentication"""
    if request.method == 'POST':
        try:
            location = request.form.get('location', '').strip()
            if not location:
                return f"<h2>Please enter a location</h2><a href='/test-local-alert'>Go back</a>"
            
            result = local_alert.check_local_risk(location)
            return f"""
            <h2>Local Alert Test Result for {location}</h2>
            <p><strong>Risk Level:</strong> {result['risk_level']}</p>
            <p><strong>Total Cases:</strong> {result['total_cases']}</p>
            <p><strong>Alert Message:</strong> {result['alert_message']}</p>
            <p><strong>Risk Description:</strong> {result['risk_description']}</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
            {''.join([f'<li>{rec}</li>' for rec in result['recommendations']])}
            </ul>
            <a href='/test-local-alert'>Test another location</a>
            """
        except Exception as e:
            logging.error(f"Test local alert error: {str(e)}")
            return f"<h2>Error: {str(e)}</h2><a href='/test-local-alert'>Go back</a>"
    
    return """
    <h2>Test Local Alert System - Karnataka Cities Only</h2>
    <form method='POST'>
        <label>Enter Karnataka Location:</label><br>
        <input type='text' name='location' placeholder='e.g., Bangalore, Mysore, Mangalore, Hubli' required><br><br>
        <input type='submit' value='Check Risk'>
    </form>
    <p><em>This system is designed for Karnataka cities only</em></p>
    <p><strong>Available cities:</strong> Bangalore (Bengaluru), Mysore (Mysuru), Mangalore (Mangaluru), Hubli (Hubballi), Belgaum (Belagavi), Tumkur, Shimoga, Davangere, Bellary, Bijapur, Gulbarga, Raichur</p>
    """

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
            
            # Update user activity counter
            update_user_activity_counter(current_user.id, 'risk_assessment')
            
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
# @login_required  # Temporarily removed for testing
def visualization():
    """Spatio-temporal visualization of dengue data"""
    track_activity('page_visit', 'visualization', f'Visualization page accessed by {current_user.name if current_user.is_authenticated else "Anonymous"}')
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

# Legal Pages
@app.route('/terms-of-service')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms_of_service.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy_policy.html')

@app.route('/copyright')
def copyright():
    """Copyright information page"""
    return render_template('copyright.html')

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

@app.route('/ai-prediction', methods=['GET', 'POST'])
@login_required
def ai_prediction():
    """AI-powered dengue outbreak prediction"""
    if request.method == 'POST':
        try:
            city = request.form.get('city', '').strip()
            weeks_ahead = int(request.form.get('weeks_ahead', 3))
            
            if not city:
                flash('Please enter a city name', 'error')
                return render_template('ai_prediction.html')
            
            if weeks_ahead < 1 or weeks_ahead > 6:
                flash('Prediction weeks must be between 1 and 6', 'error')
                return render_template('ai_prediction.html')
            
            # Get AI prediction
            prediction = ai_predictor.predict_outbreak(city, weeks_ahead)
            
            if 'error' in prediction:
                flash(f'Prediction error: {prediction["error"]}', 'error')
                return render_template('ai_prediction.html')
            
            # Update user activity counter
            update_user_activity_counter(current_user.id, 'prediction')
            
            return render_template('ai_prediction.html', prediction=prediction)
            
        except Exception as e:
            logging.error(f"AI prediction error: {str(e)}")
            flash(f'Error generating prediction: {str(e)}', 'error')
            return render_template('ai_prediction.html')
    
    return render_template('ai_prediction.html')

@app.route('/api/ai-prediction/<city>')
@login_required
def api_ai_prediction(city):
    """API endpoint for AI predictions"""
    try:
        weeks_ahead = int(request.args.get('weeks', 3))
        prediction = ai_predictor.predict_outbreak(city, weeks_ahead)
        return jsonify(prediction)
    except Exception as e:
        logging.error(f"API AI prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/live-dashboard')
@login_required
def live_dashboard():
    """Real-time outbreak monitoring dashboard"""
    return render_template('live_dashboard.html')

@app.route('/data-export')
@login_required
def data_export():
    """Data export and report generation page"""
    track_activity('page_visit', 'data_export', f'Data Export page accessed by {current_user.name}')
    return render_template('data_export.html')



@app.route('/api/cases')
@login_required
def api_cases():
    """API endpoint for case data"""
    try:
        city = request.args.get('city')
        
        if city:
            # In a real implementation, you'd query from your dengue_cases table
            # For demo purposes, return sample data
            cases_data = [
                {
                    'id': 1,
                    'city': city,
                    'cases': 45,
                    'date': '2025-12-04',
                    'latitude': 12.9716,
                    'longitude': 77.5946
                }
            ]
        else:
            # Sample data for multiple cities
            cases_data = [
                {'id': 1, 'city': 'Bangalore', 'cases': 45, 'date': '2025-12-04', 'latitude': 12.9716, 'longitude': 77.5946},
                {'id': 2, 'city': 'Mangalore', 'cases': 67, 'date': '2025-12-04', 'latitude': 12.9141, 'longitude': 74.8560},
                {'id': 3, 'city': 'Mysore', 'cases': 23, 'date': '2025-12-04', 'latitude': 12.2958, 'longitude': 76.6394}
            ]
        
        return jsonify(cases_data)
    except Exception as e:
        logging.error(f"API cases error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions')
@login_required  
def api_predictions():
    """API endpoint for predictions"""
    try:
        cities = ['Bangalore', 'Mangalore', 'Mysore', 'Hubli', 'Belgaum']
        predictions = []
        
        for city in cities:
            prediction = ai_predictor.predict_outbreak(city, 2)
            if 'error' not in prediction:
                predictions.append({
                    'city': city,
                    'predicted_cases': prediction.get('predicted_cases', 0),
                    'risk_level': prediction.get('risk_level', 'Unknown')
                })
        
        return jsonify(predictions)
    except Exception as e:
        logging.error(f"API predictions error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather')
@login_required
def api_weather():
    """API endpoint for weather data"""
    try:
        city = request.args.get('city', 'Bangalore')
        # This would integrate with actual weather API
        weather_data = {
            'city': city,
            'temperature': 28.5,
            'humidity': 75,
            'rainfall': 12.3,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(weather_data)
    except Exception as e:
        logging.error(f"API weather error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
@login_required
def api_alerts():
    """API endpoint for active alerts"""
    try:
        alerts = [
            {
                'id': 1,
                'type': 'outbreak',
                'city': 'Mangalore',
                'message': 'High dengue activity detected',
                'severity': 'high',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'id': 2,
                'type': 'weather',
                'city': 'Bangalore',
                'message': 'Favorable conditions for mosquito breeding',
                'severity': 'medium',
                'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        return jsonify(alerts)
    except Exception as e:
        logging.error(f"API alerts error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Dengue Experience Tracking Routes
@app.route('/dengue-experience')
@login_required
def dengue_experience():
    """Main dengue experience tracker page"""
    track_activity('page_visit', 'dengue_experience', f'Experience tracker accessed by {current_user.name}')
    
    # Get user's existing experiences
    experiences = DengueExperience.query.filter_by(user_id=current_user.id)\
                                      .order_by(DengueExperience.report_date.desc())\
                                      .all()
    
    return render_template('dengue_experience.html', experiences=experiences)

@app.route('/add-experience', methods=['GET', 'POST'])
@login_required
def add_experience():
    """Add new dengue experience"""
    if request.method == 'POST':
        try:
            import json
            from datetime import date
            
            # Parse form data
            experience_type = request.form.get('experience_type', 'infection')
            infection_date_str = request.form.get('infection_date')
            recovery_date_str = request.form.get('recovery_date')
            
            # Parse dates
            infection_date = None
            recovery_date = None
            if infection_date_str:
                infection_date = datetime.strptime(infection_date_str, '%Y-%m-%d').date()
            if recovery_date_str:
                recovery_date = datetime.strptime(recovery_date_str, '%Y-%m-%d').date()
            
            # Parse symptoms (checkboxes)
            symptoms = []
            symptom_list = ['fever', 'headache', 'joint_pain', 'muscle_pain', 'rash', 'nausea', 'vomiting', 'bleeding', 'fatigue', 'dizziness']
            for symptom in symptom_list:
                if symptom in request.form:
                    symptoms.append(symptom)
            
            # Parse treatments (checkboxes)
            treatments = []
            treatment_list = ['paracetamol', 'rest', 'fluids', 'hospital_care', 'traditional_medicine', 'iv_fluids', 'blood_transfusion']
            for treatment in treatment_list:
                if treatment in request.form:
                    treatments.append(treatment)
            
            # Create new experience record
            experience = DengueExperience(
                user_id=current_user.id,
                experience_type=experience_type,
                status=request.form.get('status', 'active'),
                infection_date=infection_date,
                recovery_date=recovery_date,
                symptoms=json.dumps(symptoms),
                severity_level=request.form.get('severity_level'),
                max_fever_temp=float(request.form.get('max_fever_temp')) if request.form.get('max_fever_temp') else None,
                location_infected=request.form.get('location_infected'),
                circumstances=request.form.get('circumstances'),
                prevention_used=request.form.get('prevention_used'),
                treatments_used=json.dumps(treatments),
                medications=request.form.get('medications'),
                home_remedies=request.form.get('home_remedies'),
                doctor_visits=int(request.form.get('doctor_visits', 0)),
                hospitalization='hospitalization' in request.form,
                hospitalization_days=int(request.form.get('hospitalization_days', 0)) if request.form.get('hospitalization_days') else None,
                recovery_notes=request.form.get('recovery_notes'),
                lessons_learned=request.form.get('lessons_learned'),
                advice_for_others=request.form.get('advice_for_others'),
                share_anonymously='share_anonymously' in request.form,
                public_story='public_story' in request.form
            )
            
            db.session.add(experience)
            db.session.commit()
            
            track_activity('experience_add', 'add_experience', f'New {experience_type} experience added')
            flash('Experience added successfully! Thank you for sharing.', 'success')
            return redirect(url_for('dengue_experience'))
            
        except Exception as e:
            logging.error(f"Add experience error: {str(e)}")
            flash('Error saving experience. Please try again.', 'error')
    
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    return render_template('add_experience.html', today=today)

@app.route('/experience/<int:experience_id>')
@login_required
def view_experience(experience_id):
    """View specific dengue experience"""
    experience = DengueExperience.query.filter_by(id=experience_id, user_id=current_user.id).first_or_404()
    return render_template('view_experience.html', experience=experience)

@app.route('/update-experience/<int:experience_id>', methods=['GET', 'POST'])
@login_required
def update_experience(experience_id):
    """Update existing dengue experience"""
    experience = DengueExperience.query.filter_by(id=experience_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            import json
            
            # Update status
            experience.status = request.form.get('status', experience.status)
            
            # Update recovery date if provided
            recovery_date_str = request.form.get('recovery_date')
            if recovery_date_str:
                experience.recovery_date = datetime.strptime(recovery_date_str, '%Y-%m-%d').date()
            
            # Update recovery notes
            experience.recovery_notes = request.form.get('recovery_notes', experience.recovery_notes)
            experience.lessons_learned = request.form.get('lessons_learned', experience.lessons_learned)
            experience.advice_for_others = request.form.get('advice_for_others', experience.advice_for_others)
            
            # Update treatments if provided
            treatments = []
            treatment_list = ['paracetamol', 'rest', 'fluids', 'hospital_care', 'traditional_medicine', 'iv_fluids', 'blood_transfusion']
            for treatment in treatment_list:
                if treatment in request.form:
                    treatments.append(treatment)
            
            if treatments:
                experience.treatments_used = json.dumps(treatments)
            
            # Update other fields
            experience.medications = request.form.get('medications', experience.medications)
            experience.home_remedies = request.form.get('home_remedies', experience.home_remedies)
            
            if request.form.get('doctor_visits'):
                experience.doctor_visits = int(request.form.get('doctor_visits'))
            
            experience.hospitalization = 'hospitalization' in request.form
            if request.form.get('hospitalization_days'):
                experience.hospitalization_days = int(request.form.get('hospitalization_days'))
            
            # Update sharing preferences
            experience.share_anonymously = 'share_anonymously' in request.form
            experience.public_story = 'public_story' in request.form
            
            db.session.commit()
            
            track_activity('experience_update', 'update_experience', f'Experience {experience_id} updated')
            flash('Experience updated successfully!', 'success')
            return redirect(url_for('view_experience', experience_id=experience_id))
            
        except Exception as e:
            logging.error(f"Update experience error: {str(e)}")
            flash('Error updating experience. Please try again.', 'error')
    
    return render_template('update_experience.html', experience=experience)

@app.route('/community-experiences')
def community_experiences():
    """View anonymized community experiences"""
    track_activity('page_visit', 'community_experiences', 'Community experiences viewed')
    
    # Get public experiences (anonymized)
    experiences = DengueExperience.query.filter_by(public_story=True)\
                                      .order_by(DengueExperience.report_date.desc())\
                                      .limit(50)\
                                      .all()
    
    return render_template('community_experiences.html', experiences=experiences)

@app.route('/api/experiences/stats')
def api_experience_stats():
    """API endpoint for experience statistics"""
    try:
        stats = {
            'total_experiences': DengueExperience.query.count(),
            'recoveries': DengueExperience.query.filter_by(status='recovered').count(),
            'active_cases': DengueExperience.query.filter_by(status='active').count(),
            'severity_breakdown': {
                'mild': DengueExperience.query.filter_by(severity_level='mild').count(),
                'moderate': DengueExperience.query.filter_by(severity_level='moderate').count(),
                'severe': DengueExperience.query.filter_by(severity_level='severe').count(),
                'critical': DengueExperience.query.filter_by(severity_level='critical').count()
            },
            'avg_recovery_days': 0,  # Calculate if needed
            'hospitalization_rate': 0  # Calculate if needed
        }
        
        # Calculate hospitalization rate
        total_with_data = DengueExperience.query.filter(DengueExperience.hospitalization.isnot(None)).count()
        if total_with_data > 0:
            hospitalized = DengueExperience.query.filter_by(hospitalization=True).count()
            stats['hospitalization_rate'] = round((hospitalized / total_with_data) * 100, 1)
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sw.js')
def service_worker():
    """Serve the service worker"""
    return app.send_static_file('sw.js'), 200, {'Content-Type': 'application/javascript'}

@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest"""
    return app.send_static_file('manifest.json'), 200, {'Content-Type': 'application/json'}

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('error.html', 
                         error_code=403, 
                         error_message="Access forbidden"), 403

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all other exceptions"""
    db.session.rollback()
    logging.error(f"Unhandled exception: {str(e)}")
    
    # Return JSON for API requests
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'An unexpected error occurred',
            'message': str(e) if app.debug else 'Internal server error'
        }), 500
    
    # Return HTML for regular requests
    return render_template('error.html', 
                         error_code=500, 
                         error_message="An unexpected error occurred"), 500

@app.route('/consultation')
def consultation_redirect():
    """Redirect to doctor consultation with default parameters"""
    # Get parameters from URL or use defaults
    city = request.args.get('city', 'Bangalore')
    risk_level = request.args.get('risk_level', 'Medium')
    symptoms_count = request.args.get('symptoms_count', 0)
    
    return redirect(f'/doctor/book-consultation?city={city}&risk_level={risk_level}&symptoms_count={symptoms_count}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
