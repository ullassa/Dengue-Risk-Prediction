# DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
## PROJECT EXHIBITION AND COMPETITION - 2025

**Batch No.:** 50  
**Title:** HYDRO-CLIMATIC SPATIO-TEMPORAL DENGUE RISK PREDICTION SYSTEM

### Student Names:
1. **TEJA M S**
2. **TEJAS GOWDA H R**  
3. **ULLAS SA**
4. **TARUN D N**

---

## ABSTRACT

The **Hydro-Climatic Spatio-Temporal Dengue Risk Prediction System** is an innovative web-based platform that leverages advanced machine learning algorithms and real-time environmental data to predict dengue outbreak risks across Karnataka, India. The system integrates meteorological parameters, hydrological conditions, and historical dengue case data to provide accurate, location-specific risk assessments.

Our solution employs **Flask-based web architecture** with **SQLite database management**, incorporating multiple prediction modules including **AI-powered forecasting**, **weather-based risk analysis**, **environmental factor assessment**, and **symptom-based evaluation**. The system features a comprehensive **user profile management system** with personalized health insights, **real-time local alerts**, and **interactive data visualizations**.

The platform serves as a crucial tool for **public health officials**, **healthcare providers**, and **citizens** to make informed decisions regarding dengue prevention and response strategies. By combining **spatio-temporal analysis** with **predictive modeling**, the system achieves high accuracy in early warning systems, potentially reducing dengue transmission rates and improving community health outcomes.

**Key Technologies:** Python Flask, Machine Learning (Scikit-learn), Bootstrap Frontend, SQLite Database, Weather API Integration, Interactive Maps, Real-time Analytics

---

## SALIENT FEATURES

### 🎯 **Core Prediction Modules**
- **AI-Powered Outbreak Prediction**: Machine learning models trained on historical data for 1-6 week forecasts
- **Weather-Based Risk Analysis**: Real-time meteorological data integration for climate-driven predictions
- **Environmental Risk Calculator**: Score-based assessment using 10+ environmental factors
- **Symptom Checker**: Medical symptom analysis with risk stratification
- **Local Alert System**: Community-level risk monitoring with threshold-based alerts

### 🗺️ **Spatio-Temporal Analytics**
- **Interactive Heat Maps**: Geographic visualization of dengue risk distribution
- **Temporal Trend Analysis**: Historical pattern recognition and seasonal forecasting
- **Multi-city Comparison**: Comparative risk analysis across Karnataka cities
- **Real-time Data Integration**: Live weather and case data processing

### 👤 **User Management & Personalization**
- **Comprehensive User Profiles**: Age, medical history, location-based customization
- **Personalized Risk Assessment**: Individual risk scoring based on profile data
- **Health Tracking**: Medical conditions and emergency contact management
- **Activity Analytics**: User engagement and prediction history tracking

### 📊 **Data Visualization & Reporting**
- **Interactive Dashboards**: Real-time risk monitoring with dynamic charts
- **Trend Analysis**: Historical data patterns with predictive insights
- **Export Capabilities**: Data download for research and analysis
- **Mobile-Responsive Design**: Cross-platform accessibility

### 🔔 **Alert & Notification System**
- **Risk-Level Notifications**: Customizable alert preferences
- **Community Updates**: Local outbreak warnings and health tips
- **Prevention Guidance**: Personalized recommendations based on risk levels
- **Emergency Contact Integration**: Automated family/authority notifications

### 🏥 **Healthcare Integration**
- **Clinical Decision Support**: Healthcare provider tools and insights
- **Population Health Analytics**: Community-wide health monitoring
- **Prevention Resource Hub**: Educational materials and guidelines
- **Research Data Export**: Academic and policy research support

---

## SYSTEM ARCHITECTURE & WORKFLOW

### **BLOCK DIAGRAM**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  API Dashboard  │  Admin Panel   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER (Flask)                    │
├─────────────────────────────────────────────────────────────────┤
│ Authentication │ User Management │ Session Handling │ Security   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                    PREDICTION ENGINE                           │
├─────────────────────────────────────────────────────────────────┤
│  AI Predictor  │ Weather Module │ Risk Calculator │ Symptom AI   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│   SQLite DB   │  Weather API   │  Historical Data │  ML Models   │
└─────────────────────────────────────────────────────────────────┘
```

### **SYSTEM FLOWCHART**

```
                    ┌─────────────┐
                    │   START     │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │ User Login  │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │   Profile   │
                    │ Verification│
                    └─────┬───────┘
                          │
                ┌─────────▼─────────┐
                │  Select Prediction │
                │      Module       │
                └─────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │Weather  │       │   AI    │       │  Risk   │
   │Analysis │       │Predictor│       │Calculator│
   └────┬────┘       └────┬────┘       └────┬────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    ┌─────▼───────┐
                    │Data Process │
                    │& ML Analysis│
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │Risk Level   │
                    │Calculation  │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │Personalized │
                    │Recommendations│
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │ Alert &     │
                    │Notification │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │ Data Storage│
                    │& Tracking   │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │    END      │
                    └─────────────┘
```

### **DATA FLOW DIAGRAM**

```
External APIs          User Input           Historical Data
     │                     │                      │
     ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────┐
│              DATA COLLECTION LAYER                  │
├─────────────────────────────────────────────────────┤
│ Weather API │ User Forms │ Dengue Cases │ Census Data│
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│               DATA PROCESSING ENGINE                │
├─────────────────────────────────────────────────────┤
│Data Cleaning│Normalization│Feature Extraction│Validation│
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                PREDICTION MODULES                   │
├─────────────────────────────────────────────────────┤
│ ML Models │ Statistical Analysis │ Risk Algorithms   │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│               RESULT GENERATION                     │
├─────────────────────────────────────────────────────┤
│Risk Scores│Alerts│Recommendations│Visualizations    │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                USER INTERFACE                       │
├─────────────────────────────────────────────────────┤
│ Dashboards │ Reports │ Maps │ Mobile Views         │
└─────────────────────────────────────────────────────┘
```

---

## TECHNICAL SPECIFICATIONS

### **Technology Stack**
- **Backend**: Python Flask Framework
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **APIs**: Weather API, Geolocation Services
- **Deployment**: Flask Development Server, Production WSGI

### **System Requirements**
- **Python**: 3.8+
- **RAM**: Minimum 4GB
- **Storage**: 2GB for application and data
- **Network**: Internet connectivity for API services
- **Browser**: Modern web browser with JavaScript support

### **Security Features**
- User authentication and session management
- Password hashing with Werkzeug security
- Input validation and sanitization
- CSRF protection
- Secure data transmission protocols

---

## PROJECT IMPACT & OUTCOMES

### **Healthcare Benefits**
- **Early Warning System**: Reduced dengue transmission through timely alerts
- **Resource Optimization**: Efficient allocation of healthcare resources
- **Public Awareness**: Enhanced community knowledge about dengue prevention

### **Research Contributions**
- **Data Analytics**: Comprehensive dengue surveillance data
- **Predictive Modeling**: Advanced ML approaches for disease forecasting
- **Spatio-temporal Analysis**: Geographic and temporal pattern recognition

### **Social Impact**
- **Community Engagement**: User-friendly interface for public participation
- **Educational Value**: Comprehensive prevention and awareness materials
- **Accessibility**: Multi-device support for diverse user base

---

**Developed by:**  
**Team 50** - Department of Computer Science & Engineering  
**Academic Year**: 2024-2025

*This project represents a comprehensive approach to dengue risk prediction, combining cutting-edge technology with practical healthcare applications to serve the community's health and safety needs.*