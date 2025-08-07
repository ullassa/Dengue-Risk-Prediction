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
                # Check for direct location match
                location_matches = dengue_data[
                    dengue_data['location'].str.lower().str.contains(location_lower, na=False) |
                    dengue_data['state'].str.lower().str.contains(location_lower, na=False)
                ]
                
                # Get recent cases (last 30 days)
                current_date = datetime.now()
                thirty_days_ago = current_date - timedelta(days=30)
                
                if not location_matches.empty:
                    # Convert date column to datetime if it exists
                    if 'date' in location_matches.columns:
                        location_matches['date'] = pd.to_datetime(location_matches['date'], errors='coerce')
                        recent_cases = location_matches[location_matches['date'] >= thirty_days_ago]
                    else:
                        recent_cases = location_matches
                    
                    total_cases = recent_cases['cases'].sum() if 'cases' in recent_cases.columns else len(recent_cases)
                    
                    # Determine risk level based on case count
                    if total_cases >= 50:
                        risk_level = "High"
                        risk_color = "danger"
                        alert_message = f"⚠️ HIGH ALERT: {total_cases} dengue cases reported in {location} in the last 30 days"
                    elif total_cases >= 20:
                        risk_level = "Medium"
                        risk_color = "warning"
                        alert_message = f"⚠️ MODERATE ALERT: {total_cases} dengue cases reported in {location} in the last 30 days"
                    elif total_cases >= 5:
                        risk_level = "Low-Medium"
                        risk_color = "info"
                        alert_message = f"ℹ️ WATCH: {total_cases} dengue cases reported in {location} in the last 30 days"
                    else:
                        risk_level = "Low"
                        risk_color = "success"
                        alert_message = f"✓ LOW RISK: Few or no recent dengue cases in {location}"
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
            
            # Generate location-specific recommendations
            if risk_level == "High":
                recommendations = [
                    "🚨 URGENT: Take immediate preventive action",
                    "Remove ALL stagnant water sources",
                    "Use mosquito nets and repellents consistently",
                    "Avoid outdoor activities during dawn and dusk",
                    "Seek immediate medical attention for any fever",
                    "Alert neighbors about the dengue situation",
                    "Report suspected cases to health authorities"
                ]
            elif risk_level == "Medium":
                recommendations = [
                    "⚠️ CAUTION: Increase preventive measures",
                    "Weekly inspection for stagnant water",
                    "Use mosquito repellents regularly",
                    "Keep windows and doors screened",
                    "Monitor for dengue symptoms daily",
                    "Educate family about dengue prevention"
                ]
            elif risk_level in ["Low-Medium", "Low"]:
                recommendations = [
                    "✓ PREVENTION: Continue protective measures",
                    "Regular cleaning of water storage",
                    "Proper waste management",
                    "Community awareness participation",
                    "Stay updated on local health bulletins"
                ]
            else:
                recommendations = [
                    "Stay informed about dengue in your area",
                    "Follow general dengue prevention guidelines",
                    "Report any dengue-like symptoms to authorities",
                    "Maintain good sanitation practices"
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
                'location': location,
                'total_cases': total_cases,
                'alert_message': alert_message,
                'recommendations': recommendations,
                'local_info': local_info,
                'data_period': "Last 30 days",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logging.error(f"Local alert error: {str(e)}")
            raise e
