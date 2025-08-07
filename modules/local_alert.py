import pandas as pd
import logging
from datetime import datetime, timedelta
import os

class LocalAlert:
    def __init__(self):
        self.dengue_cases_file = 'datasets/dengue_cases.csv'
        self.cities_file = 'datasets/cities.csv'
        
    def load_dengue_data(self):
        """Load dengue cases data from CSV"""
        try:
            if os.path.exists(self.dengue_cases_file):
                return pd.read_csv(self.dengue_cases_file)
            else:
                logging.warning("Dengue cases file not found, using empty dataset")
                return pd.DataFrame(columns=['location', 'state', 'cases', 'date', 'severity'])
        except Exception as e:
            logging.error(f"Error loading dengue data: {str(e)}")
            return pd.DataFrame(columns=['location', 'state', 'cases', 'date', 'severity'])
    
    def load_cities_data(self):
        """Load cities reference data"""
        try:
            if os.path.exists(self.cities_file):
                return pd.read_csv(self.cities_file)
            else:
                logging.warning("Cities file not found, using empty dataset")
                return pd.DataFrame(columns=['city', 'state', 'district'])
        except Exception as e:
            logging.error(f"Error loading cities data: {str(e)}")
            return pd.DataFrame(columns=['city', 'state', 'district'])
    
    def check_local_risk(self, location):
        """Check dengue risk for a specific location"""
        try:
            dengue_data = self.load_dengue_data()
            cities_data = self.load_cities_data()
            
            location_lower = location.lower().strip()
            
            # Find matching location
            if not dengue_data.empty:
                # Check for direct location match using correct column names
                location_matches = dengue_data[
                    dengue_data['City'].str.lower().str.contains(location_lower, na=False) |
                    dengue_data['District'].str.lower().str.contains(location_lower, na=False) |
                    dengue_data['State'].str.lower().str.contains(location_lower, na=False)
                ]
                
                # Get recent cases (last 30 days)
                current_date = datetime.now()
                thirty_days_ago = current_date - timedelta(days=30)
                
                if not location_matches.empty:
                    # Convert date column to datetime if it exists
                    if 'Date' in location_matches.columns:
                        location_matches = location_matches.copy()
                        location_matches['Date'] = pd.to_datetime(location_matches['Date'], errors='coerce')
                        recent_cases = location_matches[location_matches['Date'] >= thirty_days_ago]
                    else:
                        recent_cases = location_matches
                    
                    total_cases = recent_cases['Cases'].sum() if 'Cases' in recent_cases.columns else len(recent_cases)
                    
                    # Determine risk level based on your specific case count thresholds
                    if total_cases >= 50:
                        risk_level = "HIGH ALERT"
                        risk_color = "danger"
                        alert_message = f"🚨 HIGH ALERT: {total_cases} dengue cases reported in {location} (50+ cases threshold)"
                        risk_description = "Immediate action required - outbreak conditions"
                    elif total_cases >= 20:
                        risk_level = "MODERATE"
                        risk_color = "warning"
                        alert_message = f"⚠️ MODERATE RISK: {total_cases} dengue cases reported in {location} (20-49 cases)"
                        risk_description = "Enhanced surveillance and prevention needed"
                    elif total_cases >= 5:
                        risk_level = "WATCH"
                        risk_color = "info"
                        alert_message = f"👀 WATCH LEVEL: {total_cases} dengue cases reported in {location} (5-19 cases)"
                        risk_description = "Monitor closely and maintain preventive measures"
                    else:
                        risk_level = "LOW"
                        risk_color = "success"
                        alert_message = f"✅ LOW RISK: {total_cases} dengue cases reported in {location} (<5 cases)"
                        risk_description = "Continue normal preventive measures"
                else:
                    # No data available for this location
                    risk_level = "Unknown"
                    risk_color = "secondary"
                    alert_message = f"No recent dengue data available for {location}"
                    total_cases = 0
            else:
                # No dengue data available
                risk_level = "Unknown"
                risk_color = "secondary"
                alert_message = "No dengue surveillance data available"
                total_cases = 0
            
            # Generate location-specific recommendations based on your case thresholds
            if risk_level == "HIGH ALERT":
                recommendations = [
                    "🚨 URGENT: Take immediate preventive action",
                    "🏥 Contact local health authorities immediately",
                    "🚫 Remove ALL stagnant water sources within 24 hours",
                    "🦟 Use mosquito nets and repellents consistently",
                    "🌅 Avoid outdoor activities during dawn and dusk",
                    "🤒 Seek immediate medical attention for any fever",
                    "📢 Alert neighbors and community about outbreak risk"
                ]
            elif risk_level == "MODERATE":
                recommendations = [
                    "⚠️ CAUTION: Enhanced preventive measures required",
                    "🔍 Daily inspection for stagnant water sources",
                    "🦟 Use mosquito repellents during peak hours",
                    "🏠 Keep windows and doors screened",
                    "🌡️ Monitor family for dengue symptoms daily",
                    "📚 Educate household about dengue prevention"
                ]
            elif risk_level == "WATCH":
                recommendations = [
                    "👀 MONITORING: Stay vigilant and prepared",
                    "🧹 Weekly cleaning of water storage areas",
                    "🦟 Use mosquito repellents as needed",
                    "📰 Stay updated on local dengue alerts",
                    "🏥 Know early dengue symptoms",
                    "🤝 Participate in community prevention activities"
                ]
            elif risk_level == "LOW":
                recommendations = [
                    "✅ PREVENTION: Continue protective measures",
                    "🧹 Regular cleaning of water storage containers",
                    "🗑️ Proper waste management practices",
                    "📱 Stay informed through health bulletins",
                    "🤝 Support community dengue awareness"
                ]
            else:
                recommendations = [
                    "📊 Limited data available for your area",
                    "📋 Follow general dengue prevention guidelines",
                    "🏥 Report any dengue-like symptoms to health authorities",
                    "🧹 Maintain good sanitation practices"
                ]
            
            # Additional local information
            local_info = []
            if not cities_data.empty:
                city_match = cities_data[cities_data['city'].str.lower() == location_lower]
                if not city_match.empty:
                    state = city_match.iloc[0]['state']
                    district = city_match.iloc[0]['district']
                    local_info.append(f"District: {district}, State: {state}")
            
            return {
                'risk_level': risk_level,
                'risk_color': risk_color,
                'alert_message': alert_message,
                'risk_description': risk_description,
                'total_cases': total_cases,
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
                'recommendations': ['Contact local health authorities for current dengue information'],
                'local_info': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
