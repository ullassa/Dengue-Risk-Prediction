import pandas as pd
import logging
from datetime import datetime, timedelta
import os
from .location_validator import KarnatakaLocationValidator

class LocalAlert:
    def __init__(self):
        # Get the directory of the current file and build absolute paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # Go up one level from modules/
        self.dengue_cases_file = os.path.join(project_root, 'datasets', 'dengue_cases.csv')
        self.cities_file = os.path.join(project_root, 'datasets', 'cities.csv')
        logging.info(f"LocalAlert initialized - Dengue file: {self.dengue_cases_file}")
        logging.info(f"LocalAlert initialized - Cities file: {self.cities_file}")
        
        # Initialize Karnataka location validator
        self.location_validator = KarnatakaLocationValidator()
        
        # City name variations mapping (kept for backward compatibility)
        self.city_variations = {
            'bangalore': ['bangalore', 'bengaluru', 'blr'],
            'mysore': ['mysore', 'mysuru', 'mysooru'],
            'hubli': ['hubli', 'hubali', 'hubballi'],
            'mangalore': ['mangalore', 'mangaluru', 'mangalur'],
            'belgaum': ['belgaum', 'belagavi', 'belgavi'],
            'tumkur': ['tumkur', 'tumakuru', 'tumakur']
        }
    
    def normalize_location(self, location):
        """Normalize location name to match dataset entries"""
        location_lower = location.lower().strip()
        
        # Check direct mapping
        for canonical_name, variations in self.city_variations.items():
            if location_lower in variations:
                return canonical_name.title()  # Return with proper case
        
        # Return original if no mapping found
        return location.title()
        
    def load_dengue_data(self):
        """Load dengue cases data from CSV"""
        try:
            if os.path.exists(self.dengue_cases_file):
                df = pd.read_csv(self.dengue_cases_file)
                logging.info(f"Loaded {len(df)} dengue case records from {self.dengue_cases_file}")
                return df
            else:
                logging.warning(f"Dengue cases file not found at {self.dengue_cases_file}, using empty dataset")
                return pd.DataFrame(columns=['Date', 'City', 'District', 'State', 'Cases', 'Latitude', 'Longitude'])
        except Exception as e:
            logging.error(f"Error loading dengue data: {str(e)}")
            return pd.DataFrame(columns=['Date', 'City', 'District', 'State', 'Cases', 'Latitude', 'Longitude'])
    
    def load_cities_data(self):
        """Load cities reference data"""
        try:
            if os.path.exists(self.cities_file):
                df = pd.read_csv(self.cities_file)
                logging.info(f"Loaded {len(df)} city records from {self.cities_file}")
                return df
            else:
                logging.warning(f"Cities file not found at {self.cities_file}, using empty dataset")
                return pd.DataFrame(columns=['city', 'state', 'district'])
        except Exception as e:
            logging.error(f"Error loading cities data: {str(e)}")
            return pd.DataFrame(columns=['city', 'state', 'district'])
    
    def check_local_risk(self, location, days_window=30):
        """Check dengue risk for a specific location (Karnataka only)"""
        try:
            logging.info(f"Checking dengue risk for location: {location}")
            
            # Validate that the location is in Karnataka
            is_valid, normalized_location, suggestions = self.location_validator.validate_and_normalize(location)
            
            if not is_valid:
                logging.warning(f"Invalid Karnataka location: {location}")
                return {
                    'risk_level': 'Invalid Location',
                    'risk_color': 'secondary',
                    'alert_message': f"'{location}' is not a valid Karnataka city",
                    'risk_description': 'This system only provides alerts for Karnataka cities',
                    'total_cases': 0,
                    'analytics': {
                        'daily_average': 0,
                        'max_single_day': 0,
                        'min_single_day': 0,
                        'trend_change': 0,
                        'trend_status': 'No data',
                        'trend_icon': 'no-data',
                        'peak_day': 'Unknown',
                        'data_points': 0,
                        'date_range': 'No data'
                    },
                    'recent_data': [],
                    'recommendations': [
                        f"📍 This system is designed for Karnataka cities only",
                        f"🏠 Suggested Karnataka cities: {', '.join(suggestions)}" if suggestions else "🏠 Try cities like Bangalore, Mysore, Mangalore, Hubli",
                        f"📋 Available cities: {', '.join(self.location_validator.get_karnataka_cities_list()[:6])}...",
                        f"🔍 Please enter a Karnataka city name for dengue risk assessment"
                    ],
                    'local_info': [],
                    'data_source': 'Karnataka dengue surveillance data only',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'suggestions': suggestions
                }
            
            logging.info(f"Valid Karnataka location - Normalized: {location} -> {normalized_location}")
            
            dengue_data = self.load_dengue_data()
            cities_data = self.load_cities_data()
            
            location_lower = location.lower().strip()
            normalized_lower = normalized_location.lower().strip()
            
            # Find matching location using both original and normalized names
            if not dengue_data.empty:
                # Check for direct location match using correct column names from CSV
                # Try exact match first, then partial match
                exact_matches = dengue_data[
                    (dengue_data['City'].str.lower() == location_lower) |
                    (dengue_data['District'].str.lower() == location_lower) |
                    (dengue_data['City'].str.lower() == normalized_lower) |
                    (dengue_data['District'].str.lower() == normalized_lower)
                ]
                
                # If no exact match, try partial matching
                if exact_matches.empty:
                    location_matches = dengue_data[
                        dengue_data['City'].str.lower().str.contains(location_lower, na=False) |
                        dengue_data['District'].str.lower().str.contains(location_lower, na=False) |
                        dengue_data['State'].str.lower().str.contains(location_lower, na=False) |
                        dengue_data['City'].str.lower().str.contains(normalized_lower, na=False) |
                        dengue_data['District'].str.lower().str.contains(normalized_lower, na=False) |
                        dengue_data['State'].str.lower().str.contains(normalized_lower, na=False)
                    ]
                else:
                    location_matches = exact_matches
                
                logging.info(f"Found {len(location_matches)} records matching location: {location}")
                
                if not location_matches.empty:
                    # Convert date column to datetime if it exists
                    location_matches = location_matches.copy()
                    if 'Date' in location_matches.columns:
                        location_matches['Date'] = pd.to_datetime(location_matches['Date'], errors='coerce')
                        
                        # Try to get recent cases (last 30 days)
                        current_date = datetime.now()
                        thirty_days_ago = current_date - timedelta(days=days_window)
                        recent_cases = location_matches[location_matches['Date'] >= thirty_days_ago]
                        
                        # If no recent data, use the most recent available data (last 30 records)
                        if recent_cases.empty:
                            logging.info(f"No data in last {days_window} days for {location}, using most recent available data")
                            location_matches_sorted = location_matches.sort_values('Date', ascending=False)
                            recent_cases = location_matches_sorted.head(30)  # Get last 30 records
                            data_period = "recent available data"
                        else:
                            data_period = f"last {days_window} days"
                            logging.info(f"Using data from {data_period} for {location}")
                    else:
                        recent_cases = location_matches
                        data_period = "available data"
                    
                    # Calculate comprehensive analytics
                    total_cases = int(recent_cases['Cases'].sum()) if 'Cases' in recent_cases.columns else len(recent_cases)
                    logging.info(f"Total cases found for {location}: {total_cases}")
                    
                    # Additional analytics for interesting insights
                    daily_avg = float(total_cases / len(recent_cases)) if len(recent_cases) > 0 else 0.0
                    max_single_day = int(recent_cases['Cases'].max()) if 'Cases' in recent_cases.columns else 0
                    min_single_day = int(recent_cases['Cases'].min()) if 'Cases' in recent_cases.columns else 0
                    
                    # Calculate trend (last 7 days vs previous 7 days)
                    trend_change = 0.0
                    trend_status = "INSUFFICIENT DATA"
                    trend_icon = "no-data"
                    
                    if len(recent_cases) >= 14:
                        try:
                            recent_7_days = int(recent_cases.head(7)['Cases'].sum())
                            previous_7_days = int(recent_cases.iloc[7:14]['Cases'].sum())
                            if previous_7_days > 0:
                                trend_change = float((recent_7_days - previous_7_days) / previous_7_days * 100)
                            
                            if trend_change > 20:
                                trend_status = "RAPIDLY INCREASING"
                                trend_icon = "up-fast"
                            elif trend_change > 5:
                                trend_status = "INCREASING"
                                trend_icon = "up"
                            elif trend_change < -20:
                                trend_status = "RAPIDLY DECREASING"
                                trend_icon = "down-fast"
                            elif trend_change < -5:
                                trend_status = "DECREASING"
                                trend_icon = "down"
                            else:
                                trend_status = "STABLE"
                                trend_icon = "stable"
                        except Exception:
                            trend_change = 0.0
                            trend_status = "CALCULATION ERROR"
                            trend_icon = "error"
                    
                    # Calculate weekly pattern analysis
                    try:
                        recent_cases_copy = recent_cases.copy()
                        recent_cases_copy['DayOfWeek'] = pd.to_datetime(recent_cases_copy['Date']).dt.day_name()
                        weekly_pattern = recent_cases_copy.groupby('DayOfWeek')['Cases'].mean().to_dict()
                        if weekly_pattern:
                            peak_day = max(weekly_pattern.keys(), key=lambda k: weekly_pattern[k])
                        else:
                            peak_day = "Unknown"
                    except Exception as e:
                        logging.error(f"Weekly pattern calculation error: {str(e)}")
                        peak_day = "Unknown"
                    
                    # Determine risk level with enhanced criteria
                    if total_cases >= 300:
                        risk_level = "CRITICAL OUTBREAK"
                        risk_color = "danger"
                        alert_message = f"CRITICAL OUTBREAK: {total_cases} dengue cases reported in {location} (300+ cases - Critical threshold)"
                        risk_description = f"Emergency response required - major outbreak conditions ({data_period})"
                    elif total_cases >= 150:
                        risk_level = "HIGH ALERT"
                        risk_color = "danger"
                        alert_message = f"HIGH ALERT: {total_cases} dengue cases reported in {location} (150-299 cases threshold)"
                        risk_description = f"Immediate action required - outbreak conditions ({data_period})"
                    elif total_cases >= 50:
                        risk_level = "MODERATE"
                        risk_color = "warning"
                        alert_message = f"⚠️ MODERATE RISK: {total_cases} dengue cases reported in {location} (50-149 cases)"
                        risk_description = f"Enhanced surveillance and prevention needed ({data_period})"
                    elif total_cases >= 20:
                        risk_level = "WATCH"
                        risk_color = "info"
                        alert_message = f"👀 WATCH LEVEL: {total_cases} dengue cases reported in {location} (20-49 cases)"
                        risk_description = f"Monitor closely and maintain preventive measures ({data_period})"
                    else:
                        risk_level = "LOW"
                        risk_color = "success"
                        alert_message = f"✅ LOW RISK: {total_cases} dengue cases reported in {location} (<20 cases)"
                        risk_description = f"Continue normal preventive measures ({data_period})"
                    
                    # Create enhanced analytics data
                    analytics = {
                        'daily_average': round(daily_avg, 1),
                        'max_single_day': max_single_day,
                        'min_single_day': min_single_day,
                        'trend_change': round(trend_change, 1),
                        'trend_status': trend_status,
                        'trend_icon': trend_icon,
                        'peak_day': peak_day,
                        'data_points': len(recent_cases),
                        'date_range': f"{str(recent_cases['Date'].min())} to {str(recent_cases['Date'].max())}"
                    }
                    
                    # Recent daily data for display
                    recent_data = []
                    if not recent_cases.empty:
                        try:
                            for idx, row in recent_cases.head(7).iterrows():
                                recent_data.append({
                                    'date': str(row['Date']),
                                    'cases': int(row['Cases']),
                                    'day': pd.to_datetime(row['Date']).strftime('%A')
                                })
                        except Exception as e:
                            logging.error(f"Error creating recent_data: {str(e)}")
                            recent_data = []
                    
                    # Use helper method for recommendations
                    try:
                        recommendations = self._get_recommendations(risk_level, total_cases, trend_change)
                    except Exception as e:
                        logging.error(f"Error getting recommendations: {str(e)}")
                        recommendations = ['Contact local health authorities for current dengue information']
                    
                    try:
                        local_info = self._get_local_info(location_matches.iloc[0])
                    except Exception as e:
                        logging.error(f"Error getting local_info: {str(e)}")
                        local_info = []
                    
                    return {
                        'risk_level': risk_level,
                        'risk_color': risk_color,
                        'alert_message': alert_message,
                        'risk_description': risk_description,
                        'total_cases': total_cases,
                        'analytics': analytics,
                        'recent_data': recent_data,
                        'recommendations': recommendations,
                        'local_info': local_info,
                        'data_source': 'Karnataka dengue surveillance data',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            else:
                # No dengue data available
                risk_level = "Unknown"
                risk_color = "secondary"
                alert_message = "No dengue surveillance data available"
                risk_description = "Data unavailable"
                total_cases = 0
                data_period = "no data"
                
                # Create empty analytics for unknown cases
                analytics = {
                    'daily_average': 0,
                    'max_single_day': 0,
                    'min_single_day': 0,
                    'trend_change': 0,
                    'trend_status': "NO DATA",
                    'trend_icon': "no-data",
                    'peak_day': "Unknown",
                    'data_points': 0,
                    'date_range': "No data available"
                }
                recent_data = []
            
            # Use helper methods for all cases
            recommendations = self._get_recommendations(risk_level, total_cases, 0)
            local_info = self._get_local_info_by_location(location)
            
            return {
                'risk_level': risk_level,
                'risk_color': risk_color,
                'alert_message': alert_message,
                'risk_description': risk_description,
                'total_cases': total_cases,
                'analytics': analytics if 'analytics' in locals() else {'daily_average': 0, 'trend_status': 'No data'},
                'recent_data': recent_data if 'recent_data' in locals() else [],
                'recommendations': recommendations,
                'local_info': local_info,
                'data_source': 'Karnataka dengue surveillance data',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logging.error(f"Local alert error: {str(e)}")
            return {
                'risk_level': 'Unknown',
                'risk_color': 'secondary',
                'alert_message': f'Error retrieving dengue data for {location}',
                'risk_description': 'Data unavailable',
                'total_cases': 0,
                'analytics': {
                    'daily_average': 0,
                    'max_single_day': 0,
                    'min_single_day': 0,
                    'trend_change': 0,
                    'trend_status': 'Error',
                    'trend_icon': 'error',
                    'peak_day': 'Unknown',
                    'data_points': 0,
                    'date_range': 'No data'
                },
                'recent_data': [],
                'recommendations': ['Contact local health authorities for current dengue information'],
                'local_info': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _get_recommendations(self, risk_level, total_cases, trend_change=0):
        """Generate risk-appropriate recommendations with trend considerations"""
        base_recommendations = []
        
        if risk_level in ["CRITICAL OUTBREAK", "HIGH ALERT"]:
            base_recommendations = [
                "URGENT: Take immediate preventive action",
                "Contact local health authorities immediately",
                "Remove ALL stagnant water sources within 24 hours",
                "Use mosquito nets and repellents consistently",
                "Avoid outdoor activities during dawn and dusk",
                "Seek immediate medical attention for any fever",
                "Alert neighbors and community about outbreak risk"
            ]
        elif risk_level == "MODERATE":
            base_recommendations = [
                "CAUTION: Enhanced preventive measures required",
                "Daily inspection for stagnant water sources",
                "Use mosquito repellents during peak hours",
                "Keep windows and doors screened",
                "Monitor family for dengue symptoms daily",
                "Educate household about dengue prevention"
            ]
        elif risk_level == "WATCH":
            base_recommendations = [
                "MONITORING: Stay vigilant and prepared",
                "Weekly cleaning of water storage areas",
                "Use mosquito repellents as needed",
                "Stay updated on local dengue alerts",
                "Know early dengue symptoms",
                "Participate in community prevention activities"
            ]
        elif risk_level == "LOW":
            base_recommendations = [
                "PREVENTION: Continue protective measures",
                "Regular cleaning of water storage containers",
                "Proper waste management practices",
                "Stay informed through health bulletins",
                "Support community dengue awareness"
            ]
        else:
            base_recommendations = [
                "Limited data available for your area",
                "Follow general dengue prevention guidelines", 
                "Report any dengue-like symptoms to health authorities",
                "Maintain good sanitation practices"
            ]
        
        # Add trend-specific recommendations
        if trend_change > 20:
            base_recommendations.insert(1, "TREND ALERT: Cases are rapidly increasing - Extra vigilance required")
        elif trend_change > 5:
            base_recommendations.insert(1, "TREND NOTICE: Cases are rising - Increase prevention efforts")
        elif trend_change < -10:
            base_recommendations.append("POSITIVE TREND: Cases are decreasing but maintain vigilance")
            
        return base_recommendations
    
    def _get_local_info(self, location_data):
        """Extract local information from location data"""
        local_info = []
        try:
            if location_data is not None:
                if isinstance(location_data, pd.Series):
                    if 'District' in location_data.index:
                        district = str(location_data['District'])
                        state = str(location_data['State'])
                        local_info.append(f"District: {district}, State: {state}")
                    elif 'district' in location_data.index:
                        district = str(location_data['district'])
                        state = str(location_data['state'])
                        local_info.append(f"District: {district}, State: {state}")
                elif hasattr(location_data, 'empty') and not location_data.empty:
                    # Handle DataFrame case
                    if 'District' in location_data.columns:
                        district = str(location_data.iloc[0]['District'])
                        state = str(location_data.iloc[0]['State'])
                        local_info.append(f"District: {district}, State: {state}")
        except Exception as e:
            logging.error(f"Error in _get_local_info: {str(e)}")
        return local_info
    
    def _get_local_info_by_location(self, location):
        """Get local info by location name lookup"""
        local_info = []
        try:
            cities_data = self.load_cities_data()
            if not cities_data.empty:
                location_lower = location.lower().strip()
                city_match = cities_data[cities_data['city'].str.lower() == location_lower]
                if not city_match.empty:
                    state = city_match.iloc[0]['state']
                    district = city_match.iloc[0]['district']
                    local_info.append(f"District: {district}, State: {state}")
        except Exception as e:
            logging.warning(f"Could not get local info for {location}: {str(e)}")
        return local_info
