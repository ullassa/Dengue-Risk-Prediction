import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server deployment
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import base64
import io
import json
import logging
from datetime import datetime, timedelta
import os

# Set matplotlib font to prevent font cache issues on server
plt.rcParams['font.family'] = 'DejaVu Sans'

class Visualizer:
    def __init__(self):
        self.dengue_cases_file = 'datasets/dengue_cases.csv'
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def load_data(self):
        """Load datasets for visualization"""
        try:
            dengue_data = pd.DataFrame()
            
            if os.path.exists(self.dengue_cases_file):
                dengue_data = pd.read_csv(self.dengue_cases_file)
                print(f"Loaded dengue data: {len(dengue_data)} rows")
                print(f"Dengue data columns: {dengue_data.columns.tolist()}")
                
                if 'Date' in dengue_data.columns:
                    dengue_data['Date'] = pd.to_datetime(dengue_data['Date'], errors='coerce')
                
                # Ensure we have the required data
                if len(dengue_data) > 0:
                    print(f"Date range: {dengue_data['Date'].min()} to {dengue_data['Date'].max()}")
                    print(f"Total cases: {dengue_data['Cases'].sum()}")
                    print(f"Cities: {dengue_data['City'].unique()}")
            
            return dengue_data
        except Exception as e:
            logging.error(f"Data loading error: {str(e)}")
            print(f"Error loading data: {str(e)}")
            return pd.DataFrame()
    
    def create_time_series_chart(self, dengue_data):
        """Create time series chart of dengue cases"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            print(f"Creating time series chart with {len(dengue_data)} rows")
            
            if not dengue_data.empty and 'Date' in dengue_data.columns and 'Cases' in dengue_data.columns:
                # Group by date and sum cases
                daily_cases = dengue_data.groupby('Date')['Cases'].sum().reset_index()
                daily_cases = daily_cases.sort_values('Date')
                
                print(f"Daily cases data: {len(daily_cases)} points")
                print(f"Date range: {daily_cases['Date'].min()} to {daily_cases['Date'].max()}")
                
                # Create the plot with vibrant colors
                ax.plot(daily_cases['Date'], daily_cases['Cases'], 
                       marker='o', linewidth=3, markersize=6, color='#dc2626', markerfacecolor='#ef4444')
                ax.fill_between(daily_cases['Date'], daily_cases['Cases'], 
                              alpha=0.4, color='#ef4444')
                
                ax.set_title('Dengue Cases Over Time', fontsize=16, fontweight='bold', color='#1f2937')
                ax.text(0.5, 0.95, 'Across 12 Karnataka Cities', transform=ax.transAxes, 
                       ha='center', fontsize=10, style='italic', color='#6b7280')
                ax.set_xlabel('Date', fontsize=12, fontweight='600')
                ax.set_ylabel('Number of Cases', fontsize=12, fontweight='600')
                ax.grid(True, alpha=0.3, color='#6b7280')
                
                # Format x-axis
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Add some styling
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#6b7280')
                ax.spines['bottom'].set_color('#6b7280')
            else:
                print("No valid dengue data for time series chart")
                ax.text(0.5, 0.5, 'No dengue cases data available\nPlease check data files', 
                       horizontalalignment='center', verticalalignment='center',
                       fontsize=14, transform=ax.transAxes, color='#ef4444')
                ax.set_title('Dengue Cases Over Time', fontsize=16, fontweight='bold')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            logging.error(f"Time series chart error: {str(e)}")
            print(f"Time series chart error: {str(e)}")
            return None
    
    def create_location_chart(self, dengue_data):
        """Create bar chart of cases by location"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            print(f"Creating location chart with {len(dengue_data)} rows")
            
            if not dengue_data.empty and 'City' in dengue_data.columns and 'Cases' in dengue_data.columns:
                # Group by city and sum cases
                location_cases = dengue_data.groupby('City')['Cases'].sum().sort_values(ascending=False).head(10)
                
                print(f"Location cases data: {location_cases.to_dict()}")
                
                # Create colorful bars
                colors = ['#dc2626', '#ea580c', '#f59e0b', '#eab308', '#84cc16', 
                         '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9']
                
                try:
                    bars = ax.bar(range(len(location_cases)), location_cases.values, 
                                color=colors[:len(location_cases)], alpha=0.8, edgecolor='white', linewidth=2)
                    
                    # Add value labels on bars
                    max_value = float(max(location_cases.values))
                    for i, bar in enumerate(bars):
                        height = float(bar.get_height())
                        x_pos = float(bar.get_x() + bar.get_width()/2.0)
                        y_pos = height + max_value * 0.01
                        ax.text(x_pos, y_pos, f'{int(height)}', 
                               ha='center', va='bottom', fontsize=11, fontweight='bold')
                except Exception as bar_error:
                    print(f"Bar chart error: {bar_error}")
                    # Fallback to simple bars without labels
                    ax.bar(range(len(location_cases)), location_cases.values, 
                           color=colors[:len(location_cases)], alpha=0.8)
                
                ax.set_title('Cases by Location (Karnataka Cities)', fontsize=16, fontweight='bold', color='#1f2937')
                ax.set_xlabel('City', fontsize=12, fontweight='600')
                ax.set_ylabel('Number of Cases', fontsize=12, fontweight='600')
                ax.set_xticks(range(len(location_cases)))
                ax.set_xticklabels(location_cases.index, rotation=45, ha='right', fontweight='500')
                ax.grid(True, alpha=0.3, axis='y', color='#6b7280')
                
                # Style the plot
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#6b7280')
                ax.spines['bottom'].set_color('#6b7280')
                
                plt.tight_layout()
            else:
                print("No valid location data for chart")
                ax.text(0.5, 0.5, 'No location data available\nPlease check data files', 
                       horizontalalignment='center', verticalalignment='center',
                       fontsize=14, transform=ax.transAxes, color='#ef4444')
                ax.set_title('Cases by Location', fontsize=16, fontweight='bold')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            logging.error(f"Location chart error: {str(e)}")
            print(f"Location chart error: {str(e)}")
            return None

    
    def generate_charts(self):
        """Generate all visualization charts"""
        try:
            print("Starting chart generation...")
            dengue_data = self.load_data()
            
            print(f"Loaded data - Dengue: {len(dengue_data)} rows")
            
            charts = {}
            generated_count = 0
            
            # Generate time series chart
            print("Generating time series chart...")
            try:
                charts['time_series'] = self.create_time_series_chart(dengue_data)
                if charts['time_series']:
                    generated_count += 1
                    print("Time series chart: Generated successfully")
                else:
                    print("Time series chart: Failed to generate")
            except Exception as e:
                print(f"Time series chart error: {str(e)}")
                charts['time_series'] = None
            
            # Generate location chart  
            print("Generating location chart...")
            try:
                charts['location'] = self.create_location_chart(dengue_data)
                if charts['location']:
                    generated_count += 1
                    print("Location chart: Generated successfully")
                else:
                    print("Location chart: Failed to generate")
            except Exception as e:
                print(f"Location chart error: {str(e)}")
                charts['location'] = None
            
            print(f"Chart generation complete. Generated: {generated_count} out of 2 charts")
            
            # Add statistics data
            charts['statistics'] = self.get_statistics(dengue_data)
            
            return charts
        except Exception as e:
            logging.error(f"Chart generation error: {str(e)}")
            print(f"Chart generation error: {str(e)}")
            return {'time_series': None, 'location': None, 'statistics': None}
    
    def get_map_data(self):
        """Get data for map visualization - shows all Karnataka cities"""
        try:
            dengue_data = self.load_data()
            
            # Karnataka cities with coordinates (all 12 cities from our dataset)
            karnataka_cities = {
                'Bangalore': [12.9716, 77.5946],
                'Mysore': [12.2958, 76.6394],
                'Hubli': [15.3647, 75.1240],
                'Mangalore': [12.9141, 74.8560],
                'Belgaum': [15.8497, 74.4977],
                'Tumkur': [13.3379, 77.1022],
                'Davangere': [14.4644, 75.9218],
                'Bellary': [15.1394, 76.9214],
                'Bijapur': [16.8302, 75.7100],
                'Shimoga': [13.9299, 75.5681],
                'Gulbarga': [17.3297, 76.8343],
                'Hassan': [13.0033, 76.1004]
            }
            
            location_data = []
            
            # Get case data if available
            case_data = {}
            if not dengue_data.empty and 'City' in dengue_data.columns and 'Cases' in dengue_data.columns:
                case_summary = dengue_data.groupby('City')['Cases'].sum()
                case_data = case_summary.to_dict()
                print(f"Case data loaded: {case_data}")
            
            # Create markers for ALL Karnataka cities
            for city, coordinates in karnataka_cities.items():
                cases = case_data.get(city, 0)  # Default to 0 if no cases found
                
                location_data.append({
                    'name': city,
                    'cases': int(cases),
                    'lat': coordinates[0],
                    'lng': coordinates[1],
                    'state': 'Karnataka'
                })
            
            return {
                'locations': location_data,
                'message': f'Showing {len(location_data)} locations with dengue cases'
            }
            
        except Exception as e:
            logging.error(f"Map data error: {str(e)}")
            return {'locations': [], 'message': 'Error loading map data'}
    
    def get_statistics(self, dengue_data):
        """Get statistical summary of the data"""
        try:
            if dengue_data.empty:
                return {
                    'total_cases': 0,
                    'total_cities': 0,
                    'date_range': 'No data available',
                    'avg_daily_cases': 0,
                    'highest_risk_city': 'N/A'
                }
            
            total_cases = int(dengue_data['Cases'].sum()) if 'Cases' in dengue_data.columns else 0
            total_cities = len(dengue_data['City'].unique()) if 'City' in dengue_data.columns else 0
            
            # Date range
            if 'Date' in dengue_data.columns:
                min_date = dengue_data['Date'].min()
                max_date = dengue_data['Date'].max()
                date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
                
                # Average daily cases
                date_range_days = (max_date - min_date).days + 1
                avg_daily_cases = round(total_cases / max(date_range_days, 1), 1)
            else:
                date_range = 'Date information not available'
                avg_daily_cases = 0
            
            # Highest risk city
            if 'City' in dengue_data.columns and 'Cases' in dengue_data.columns:
                city_totals = dengue_data.groupby('City')['Cases'].sum()
                highest_risk_city = city_totals.idxmax() if not city_totals.empty else 'N/A'
            else:
                highest_risk_city = 'N/A'
            
            return {
                'total_cases': total_cases,
                'total_cities': total_cities,
                'date_range': date_range,
                'avg_daily_cases': avg_daily_cases,
                'highest_risk_city': highest_risk_city
            }
        except Exception as e:
            logging.error(f"Statistics calculation error: {str(e)}")
            return {
                'total_cases': 0,
                'total_cities': 0,
                'date_range': 'Error calculating statistics',
                'avg_daily_cases': 0,
                'highest_risk_city': 'Error'
            }
