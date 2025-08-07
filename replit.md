# Overview

This is a Hydro-Climatic Spatio-Temporal Dengue Risk Prediction System built with Flask. The application predicts dengue outbreak risks using multiple assessment methods including weather analysis, symptom checking, location-based alerts, environmental risk calculation, and data visualization. The system integrates real-time weather data with historical dengue case patterns to provide comprehensive risk assessments and prevention guidance.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap CSS framework with Font Awesome icons
- **JavaScript Libraries**: Chart.js for visualizations, Leaflet for maps
- **Responsive Design**: Mobile-first approach with responsive grid system
- **Theme**: Dark theme implementation using Bootstrap's data-bs-theme attribute

## Backend Architecture
- **Web Framework**: Flask with modular architecture
- **Route Structure**: RESTful endpoints for each functional module
- **Session Management**: Flask sessions with configurable secret key
- **Error Handling**: Try-catch blocks with logging and user-friendly error messages
- **Logging**: Python logging module for debugging and monitoring

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