# Dengue Detection & Risk Prediction System

A comprehensive Flask web application for predicting dengue outbreak risks using weather data, symptom analysis, and location-based alerts with full admin management capabilities.

**Latest Update (Aug 7, 2025)**: Added PostgreSQL database support, comprehensive admin interface, and production deployment configuration for Render.
.
## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/ullassa/Dengue-Risk-Prediction.git
cd Dengue-Risk-Prediction

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run the application
python app.py
```

### 🎯 Admin Access
- **URL**: http://localhost:5000/admin
- **Default Credentials**: admin@dengue.com / admin123 (change in production)

## 🌐 Deploy to Render

1. **Fork this repository**
2. **Create Render account** at https://dashboard.render.com
3. **Create PostgreSQL database** in Render
4. **Create Web Service** with these settings:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. **Set environment variables** (see RENDER_DEPLOYMENT.md)

## 📊 Features

### For Users
- Weather-based dengue risk prediction
- Symptom checker with risk assessment
- Location-based alerts and warnings
- Historical data visualization
- Prevention guidelines and tips

### For Administrators
- Complete user management dashboard
- Real-time analytics and statistics
- Database monitoring and health checks
- User prediction history tracking
- System performance metrics

## 🛡️ Security Features
- User authentication with Flask-Login
- Admin-only access controls
- Environment variable management
- PostgreSQL with SSL support
- Session security and CSRF protection

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 dark theme,
- **UI Framework**: Bootstrap CSS framework with Font Awesome icons
- **JavaScript Libraries**: Chart.js for visualizations, Leaflet for maps
- **Responsive Design**: Mobile-first approach with responsive grid system
- **Theme**: Dark theme implementation using Bootstrap's data-bs-theme attribute

## Backend Architecture
- **Web Framework**: Flask with modular architecture
- **Authentication**: Flask-Login with session-based user management
- **Database**: SQLite with SQLAlchemy ORM for user accounts and history tracking
- **Route Structure**: RESTful endpoints for each functional module with access control
- **Session Management**: Flask-Login sessions with Werkzeug password hashing
- **Error Handling**: Try-catch blocks with logging and user-friendly error messages
- **Logging**: Python logging module for debugging and monitoring

## User Management System
- **User Registration**: Secure signup with email uniqueness validation
- **User Authentication**: Login/logout with password verification
- **Access Control**: All prediction modules protected with @login_required decorator
- **Personalized Dashboard**: User-specific welcome message and quick stats
- **History Tracking**: Automatic saving of weather risk assessments per user

## Modular Component Design
The system uses a modular architecture with separate Python modules:

- **WeatherPredictor**: Fetches and analyzes weather data from OpenWeatherMap API
- **SymptomChecker**: WHO-guideline based symptom assessment with weighted scoring
- **LocalAlert**: Location-based dengue case tracking and community alerts
- **RiskCalculator**: Environmental and behavioral risk factor assessment
- **Visualizer**: Data visualization using matplotlib and seaborn

## Data Processing Architecture
- **Weather Analysis**: Rule-based risk assessment using temperature, humidity, and rainfall thresholds
- **Symptom Scoring**: Weighted symptom analysis based on WHO dengue guidelines
- **Risk Calculation**: Point-based scoring system for environmental factors
- **Data Visualization**: Chart generation with base64 encoding for web display

## File Organization
- **Static Assets**: CSS, JavaScript, and images in `/static` directory
- **Templates**: HTML templates with inheritance pattern in `/templates` directory
- **Datasets**: CSV files for historical data storage in `/datasets` directory
- **Modules**: Separate Python files for each functional component in `/modules` directory

## Security Considerations
- **Environment Variables**: API keys stored as environment variables
- **Form Validation**: Client-side and server-side validation
- **Error Sanitization**: Safe error message display without exposing system details
- **Session Security**: Configurable session secret key

# External Dependencies

## APIs and Services
- **OpenWeatherMap API**: Real-time weather data for temperature, humidity, and rainfall analysis
- **Bootstrap CDN**: CSS framework and components via Replit's custom dark theme
- **Font Awesome CDN**: Icon library for UI elements
- **Chart.js CDN**: JavaScript charting library for data visualization
- **Leaflet CDN**: Open-source mapping library for location-based features

## Python Libraries
- **Flask**: Web application framework and routing
- **Requests**: HTTP client for API calls to weather services
- **Pandas**: Data manipulation and analysis for CSV datasets
- **Matplotlib**: Static chart generation for visualization module
- **Seaborn**: Statistical data visualization enhancement

## Data Sources
- **Historical Dengue Cases**: CSV datasets containing location, date, and case count data
- **Weather History**: Historical weather pattern data for trend analysis
- **Geographic Data**: City and state reference data for location matching

## Frontend Dependencies
- **Bootstrap JavaScript**: Interactive components and responsive behavior
- **Vanilla JavaScript**: Custom form validation and user interaction handling
- **CSS Grid/Flexbox**: Layout and responsive design implementation

  If you have any doubts DM
