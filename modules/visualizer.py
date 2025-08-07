import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import json
import logging
from datetime import datetime, timedelta
import os

class Visualizer:
    def __init__(self):
        self.dengue_cases_file = 'datasets/dengue_cases.csv'
        self.weather_history_file = 'datasets/weather_history.csv'
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def load_data(self):
        """Load datasets for visualization"""
        try:
            dengue_data = pd.DataFrame()
            weather_data = pd.DataFrame()
            
            if os.path.exists(self.dengue_cases_file):
                dengue_data = pd.read_csv(self.dengue_cases_file)
                if 'date' in dengue_data.columns:
                    dengue_data['date'] = pd.to_datetime(dengue_data['date'], errors='coerce')
            
            if os.path.exists(self.weather_history_file):
                weather_data = pd.read_csv(self.weather_history_file)
                if 'date' in weather_data.columns:
                    weather_data['date'] = pd.to_datetime(weather_data['date'], errors='coerce')
            
            return dengue_data, weather_data
        except Exception as e:
            logging.error(f"Data loading error: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()
    
    def create_time_series_chart(self, dengue_data):
        """Create time series chart of dengue cases"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if not dengue_data.empty and 'date' in dengue_data.columns and 'cases' in dengue_data.columns:
                # Group by date and sum cases
                daily_cases = dengue_data.groupby('date')['cases'].sum().reset_index()
                daily_cases = daily_cases.sort_values('date')
                
                ax.plot(daily_cases['date'], daily_cases['cases'], 
                       marker='o', linewidth=2, markersize=4, color='#e74c3c')
                ax.fill_between(daily_cases['date'], daily_cases['cases'], 
                              alpha=0.3, color='#e74c3c')
                
                ax.set_title('Dengue Cases Over Time', fontsize=16, fontweight='bold')
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Number of Cases', fontsize=12)
                ax.grid(True, alpha=0.3)
                
                # Format x-axis
                plt.xticks(rotation=45)
                plt.tight_layout()
            else:
                ax.text(0.5, 0.5, 'No dengue cases data available', 
                       horizontalalignment='center', verticalalignment='center',
                       fontsize=14, transform=ax.transAxes)
                ax.set_title('Dengue Cases Over Time', fontsize=16, fontweight='bold')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            logging.error(f"Time series chart error: {str(e)}")
            return None
    
    def create_location_chart(self, dengue_data):
        """Create bar chart of cases by location"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if not dengue_data.empty and 'location' in dengue_data.columns and 'cases' in dengue_data.columns:
                # Group by location and sum cases
                location_cases = dengue_data.groupby('location')['cases'].sum().sort_values(ascending=False).head(10)
                
                bars = ax.bar(range(len(location_cases)), location_cases.values, 
                            color='#3498db', alpha=0.8)
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{int(height)}', ha='center', va='bottom', fontsize=10)
                
                ax.set_title('Top 10 Locations by Dengue Cases', fontsize=16, fontweight='bold')
                ax.set_xlabel('Location', fontsize=12)
                ax.set_ylabel('Number of Cases', fontsize=12)
                ax.set_xticks(range(len(location_cases)))
                ax.set_xticklabels(location_cases.index, rotation=45, ha='right')
                ax.grid(True, alpha=0.3, axis='y')
                
                plt.tight_layout()
            else:
                ax.text(0.5, 0.5, 'No location data available', 
                       horizontalalignment='center', verticalalignment='center',
                       fontsize=14, transform=ax.transAxes)
                ax.set_title('Cases by Location', fontsize=16, fontweight='bold')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            logging.error(f"Location chart error: {str(e)}")
            return None
    
    def create_weather_correlation_chart(self, dengue_data, weather_data):
        """Create correlation chart between weather and dengue cases"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            if not dengue_data.empty and not weather_data.empty:
                # Merge data by date
                if 'date' in dengue_data.columns and 'date' in weather_data.columns:
                    daily_dengue = dengue_data.groupby('date')['cases'].sum().reset_index()
                    merged_data = pd.merge(daily_dengue, weather_data, on='date', how='inner')
                    
                    if not merged_data.empty and len(merged_data) > 1:
                        # Temperature vs Cases
                        if 'temperature' in merged_data.columns:
                            ax1.scatter(merged_data['temperature'], merged_data['cases'], 
                                      alpha=0.6, color='#e74c3c')
                            ax1.set_xlabel('Temperature (°C)')
                            ax1.set_ylabel('Dengue Cases')
                            ax1.set_title('Temperature vs Dengue Cases')
                            ax1.grid(True, alpha=0.3)
                        
                        # Humidity vs Cases
                        if 'humidity' in merged_data.columns:
                            ax2.scatter(merged_data['humidity'], merged_data['cases'], 
                                      alpha=0.6, color='#3498db')
                            ax2.set_xlabel('Humidity (%)')
                            ax2.set_ylabel('Dengue Cases')
                            ax2.set_title('Humidity vs Dengue Cases')
                            ax2.grid(True, alpha=0.3)
                        
                        # Rainfall vs Cases
                        if 'rainfall' in merged_data.columns:
                            ax3.scatter(merged_data['rainfall'], merged_data['cases'], 
                                      alpha=0.6, color='#2ecc71')
                            ax3.set_xlabel('Rainfall (mm)')
                            ax3.set_ylabel('Dengue Cases')
                            ax3.set_title('Rainfall vs Dengue Cases')
                            ax3.grid(True, alpha=0.3)
                        
                        # Monthly trend
                        if 'date' in merged_data.columns:
                            merged_data['month'] = merged_data['date'].dt.month
                            monthly_cases = merged_data.groupby('month')['cases'].mean()
                            ax4.bar(monthly_cases.index, monthly_cases.values, 
                                   color='#f39c12', alpha=0.8)
                            ax4.set_xlabel('Month')
                            ax4.set_ylabel('Average Cases')
                            ax4.set_title('Monthly Dengue Pattern')
                            ax4.set_xticks(range(1, 13))
                            ax4.grid(True, alpha=0.3, axis='y')
            
            # Fill empty subplots with messages
            for ax in [ax1, ax2, ax3, ax4]:
                if not ax.has_data():
                    ax.text(0.5, 0.5, 'Insufficient data for correlation analysis', 
                           horizontalalignment='center', verticalalignment='center',
                           fontsize=12, transform=ax.transAxes)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            logging.error(f"Weather correlation chart error: {str(e)}")
            return None
    
    def generate_charts(self):
        """Generate all visualization charts"""
        try:
            dengue_data, weather_data = self.load_data()
            
            charts = {
                'time_series': self.create_time_series_chart(dengue_data),
                'location': self.create_location_chart(dengue_data),
                'weather_correlation': self.create_weather_correlation_chart(dengue_data, weather_data)
            }
            
            return charts
        except Exception as e:
            logging.error(f"Chart generation error: {str(e)}")
            return {'time_series': None, 'location': None, 'weather_correlation': None}
    
    def get_map_data(self):
        """Get data for map visualization"""
        try:
            dengue_data, _ = self.load_data()
            
            if dengue_data.empty:
                return {'locations': [], 'message': 'No dengue data available for mapping'}
            
            # Group by location and get coordinates (mock data for demonstration)
            location_data = []
            
            if 'location' in dengue_data.columns and 'cases' in dengue_data.columns:
                location_summary = dengue_data.groupby('location').agg({
                    'cases': 'sum',
                    'state': 'first'
                }).reset_index()
                
                # Mock coordinates for demonstration (in a real app, you'd have a geocoding service)
                mock_coordinates = {
                    'mumbai': [19.0760, 72.8777],
                    'delhi': [28.7041, 77.1025],
                    'bangalore': [12.9716, 77.5946],
                    'chennai': [13.0827, 80.2707],
                    'kolkata': [22.5726, 88.3639],
                    'hyderabad': [17.3850, 78.4867],
                    'pune': [18.5204, 73.8567],
                    'ahmedabad': [23.0225, 72.5714]
                }
                
                for _, row in location_summary.iterrows():
                    location = row['location'].lower()
                    cases = row['cases']
                    
                    # Try to find coordinates
                    coords = None
                    for city, coord in mock_coordinates.items():
                        if city in location:
                            coords = coord
                            break
                    
                    if coords:
                        location_data.append({
                            'name': row['location'],
                            'cases': int(cases),
                            'lat': coords[0],
                            'lng': coords[1],
                            'state': row.get('state', 'Unknown')
                        })
            
            return {
                'locations': location_data,
                'message': f'Showing {len(location_data)} locations with dengue cases'
            }
            
        except Exception as e:
            logging.error(f"Map data error: {str(e)}")
            return {'locations': [], 'message': 'Error loading map data'}
