import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DengueOutbreakPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.model_file = 'models/dengue_predictor.joblib'
        self.scaler_file = 'models/dengue_scaler.joblib'
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        # Load existing model if available
        self.load_model()
    
    def prepare_features(self, data):
        """Create features for machine learning from dengue and weather data"""
        features = []
        
        # Sort by city and date
        data = data.sort_values(['City', 'Date']).copy()
        
        for city in data['City'].unique():
            city_data = data[data['City'] == city].copy()
            city_data = city_data.sort_values('Date')
            
            for i in range(len(city_data)):
                row = city_data.iloc[i]
                feature_dict = {
                    'city': city,
                    'month': row['Date'].month,
                    'day_of_year': row['Date'].dayofyear,
                    'week_of_year': row['Date'].isocalendar().week,
                    'temperature': row.get('Temperature', 26.0),
                    'humidity': row.get('Humidity', 70.0),
                    'rainfall': row.get('Rainfall', 10.0)
                }
                
                # Add lagged features (previous weeks' cases)
                for lag in [1, 2, 3, 4]:  # 1-4 weeks ago
                    if i >= lag:
                        prev_cases = city_data.iloc[i-lag]['Cases']
                        feature_dict[f'cases_lag_{lag}w'] = prev_cases
                    else:
                        feature_dict[f'cases_lag_{lag}w'] = 0
                
                # Add moving averages
                if i >= 2:
                    feature_dict['cases_ma_3'] = city_data.iloc[max(0, i-2):i+1]['Cases'].mean()
                else:
                    feature_dict['cases_ma_3'] = row['Cases']
                
                if i >= 6:
                    feature_dict['cases_ma_7'] = city_data.iloc[max(0, i-6):i+1]['Cases'].mean()
                else:
                    feature_dict['cases_ma_7'] = row['Cases']
                
                # Add seasonal patterns
                feature_dict['is_monsoon'] = 1 if row['Date'].month in [6, 7, 8, 9] else 0
                feature_dict['is_post_monsoon'] = 1 if row['Date'].month in [10, 11] else 0
                
                # Target: cases in next 2-3 weeks
                target_weeks = []
                for future_week in [1, 2, 3]:
                    if i + future_week < len(city_data):
                        target_weeks.append(city_data.iloc[i + future_week]['Cases'])
                
                if target_weeks:
                    feature_dict['target_max_cases'] = max(target_weeks)
                    feature_dict['target_total_cases'] = sum(target_weeks)
                    feature_dict['date'] = row['Date']
                    features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def train_model(self):
        """Train the outbreak prediction model"""
        try:
            # Load dengue data
            dengue_data = pd.read_csv('datasets/dengue_cases.csv')
            dengue_data['Date'] = pd.to_datetime(dengue_data['Date'])
            
            # Add mock weather data for training
            dengue_data['Temperature'] = np.random.normal(26.5, 3, len(dengue_data))
            dengue_data['Humidity'] = np.random.normal(75, 10, len(dengue_data))
            dengue_data['Rainfall'] = np.random.exponential(8, len(dengue_data))
            
            # Prepare features
            features_df = self.prepare_features(dengue_data)
            
            if len(features_df) < 50:
                print("Not enough data for training. Need at least 50 samples.")
                return False
            
            # Prepare training data
            feature_cols = [col for col in features_df.columns if col not in ['target_max_cases', 'target_total_cases', 'date', 'city']]
            
            X = features_df[feature_cols].fillna(0)
            y_max = features_df['target_max_cases']
            y_total = features_df['target_total_cases']
            
            # Encode city names
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            city_encoded = le.fit_transform(features_df['city'])
            X['city_encoded'] = city_encoded
            feature_cols.append('city_encoded')
            
            self.feature_columns = feature_cols
            self.label_encoder = le
            
            # Split data
            X_train, X_test, y_train_max, y_test_max, y_train_total, y_test_total = train_test_split(
                X[feature_cols], y_max, y_total, test_size=0.3, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest for max cases prediction
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train_max)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test_max, y_pred)
            r2 = r2_score(y_test_max, y_pred)
            
            print(f"Model trained successfully!")
            print(f"Mean Absolute Error: {mae:.2f}")
            print(f"R² Score: {r2:.3f}")
            
            # Save model
            self.save_model()
            
            return True
            
        except Exception as e:
            logging.error(f"Model training error: {str(e)}")
            print(f"Training error: {str(e)}")
            return False
    
    def predict_outbreak(self, city, weeks_ahead=3):
        """Predict dengue outbreak risk for next 2-3 weeks"""
        if self.model is None:
            print("Model not trained. Training now...")
            if not self.train_model():
                return None
        
        try:
            # Get latest data for the city
            dengue_data = pd.read_csv('datasets/dengue_cases.csv')
            dengue_data['Date'] = pd.to_datetime(dengue_data['Date'])
            
            city_data = dengue_data[dengue_data['City'] == city].sort_values('Date')
            
            if len(city_data) == 0:
                return {'error': f'No data available for {city}'}
            
            # Get latest date
            latest_date = city_data['Date'].max()
            latest_row = city_data[city_data['Date'] == latest_date].iloc[0]
            
            # Create prediction features
            predictions = []
            
            for week in range(1, weeks_ahead + 1):
                pred_date = latest_date + timedelta(weeks=week)
                
                # Mock weather forecast (in real system, use weather API forecast)
                feature_dict = {
                    'month': pred_date.month,
                    'day_of_year': pred_date.dayofyear,
                    'week_of_year': pred_date.isocalendar().week,
                    'temperature': 26.0 + np.random.normal(0, 2),
                    'humidity': 70.0 + np.random.normal(0, 10),
                    'rainfall': max(0, 10.0 + np.random.normal(0, 5)),
                    'is_monsoon': 1 if pred_date.month in [6, 7, 8, 9] else 0,
                    'is_post_monsoon': 1 if pred_date.month in [10, 11] else 0
                }
                
                # Add historical cases as features
                recent_cases = city_data.tail(4)['Cases'].tolist()
                for i, lag in enumerate([1, 2, 3, 4]):
                    if i < len(recent_cases):
                        feature_dict[f'cases_lag_{lag}w'] = recent_cases[-(i+1)]
                    else:
                        feature_dict[f'cases_lag_{lag}w'] = 0
                
                feature_dict['cases_ma_3'] = np.mean(recent_cases[-3:]) if len(recent_cases) >= 3 else recent_cases[-1]
                feature_dict['cases_ma_7'] = np.mean(recent_cases) if len(recent_cases) > 0 else 0
                
                # Encode city
                try:
                    city_encoded = self.label_encoder.transform([city])[0]
                except:
                    city_encoded = 0
                feature_dict['city_encoded'] = city_encoded
                
                # Create feature vector
                feature_vector = [feature_dict.get(col, 0) for col in self.feature_columns]
                
                # Scale and predict
                feature_scaled = self.scaler.transform([feature_vector])
                predicted_cases = max(0, self.model.predict(feature_scaled)[0])
                
                # Determine risk level
                risk_level = self._get_risk_level(predicted_cases)
                
                predictions.append({
                    'week': week,
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'predicted_cases': int(round(predicted_cases)),  # Round to whole numbers
                    'risk_level': risk_level['level'],
                    'risk_color': risk_level['color'],
                    'confidence': min(100, 60 + np.random.randint(0, 30))  # Mock confidence
                })
            
            return {
                'city': city,
                'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'predictions': predictions,
                'recommendations': self._generate_smart_recommendations(predictions),
                'model_info': {
                    'algorithm': 'Random Forest',
                    'features': len(self.feature_columns),
                    'trained_on': f'{len(dengue_data)} data points',
                    'data_source': 'Historical sample data (Nov 2025)',
                    'limitations': 'Demo system using limited historical data'
                }
            }
            
        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            return {'error': f'Prediction failed: {str(e)}'}
    
    def _get_risk_level(self, cases):
        """Convert predicted cases to risk level"""
        if cases >= 40:
            return {'level': 'Very High', 'color': 'danger'}
        elif cases >= 30:
            return {'level': 'High', 'color': 'warning'}
        elif cases >= 20:
            return {'level': 'Moderate', 'color': 'info'}
        elif cases >= 10:
            return {'level': 'Low', 'color': 'success'}
        else:
            return {'level': 'Very Low', 'color': 'light'}
    
    def save_model(self):
        """Save trained model and scaler"""
        if self.model is not None:
            joblib.dump(self.model, self.model_file)
            joblib.dump(self.scaler, self.scaler_file)
            joblib.dump(self.feature_columns, 'models/feature_columns.joblib')
            if hasattr(self, 'label_encoder'):
                joblib.dump(self.label_encoder, 'models/label_encoder.joblib')
    
    def load_model(self):
        """Load saved model and scaler"""
        try:
            if os.path.exists(self.model_file):
                self.model = joblib.load(self.model_file)
                self.scaler = joblib.load(self.scaler_file)
                self.feature_columns = joblib.load('models/feature_columns.joblib')
                if os.path.exists('models/label_encoder.joblib'):
                    self.label_encoder = joblib.load('models/label_encoder.joblib')
                print("Model loaded successfully!")
        except Exception as e:
            print(f"Could not load model: {str(e)}")
            self.model = None
    
    def _generate_smart_recommendations(self, predictions):
        """Generate smart recommendations based on prediction patterns"""
        recommendations = []
        
        # Analyze risk pattern across weeks
        high_risk_weeks = [p for p in predictions if p['risk_level'] in ['High', 'Very High']]
        moderate_weeks = [p for p in predictions if p['risk_level'] == 'Moderate']
        
        if len(high_risk_weeks) >= 3:
            recommendations.extend([
                {'title': 'Urgent Outbreak Response', 'description': 'Sustained high risk predicted - Deploy emergency response teams'},
                {'title': 'Hospital Capacity', 'description': 'Scale up medical facilities and supplies immediately'},
                {'title': 'Community Awareness', 'description': 'Launch intensive public health campaigns'}
            ])
        elif len(high_risk_weeks) >= 2:
            recommendations.extend([
                {'title': 'Enhanced Surveillance', 'description': 'Multiple high-risk weeks detected - Strengthen monitoring systems'},
                {'title': 'Vector Control', 'description': 'Increase mosquito control activities in hotspot areas'}
            ])
        elif len(high_risk_weeks) >= 1:
            recommendations.extend([
                {'title': f'Week {high_risk_weeks[0]["week"]} Alert', 'description': 'Prepare for increased cases and intervention measures'},
                {'title': 'Close Monitoring', 'description': 'Maintain vigilant surveillance and response readiness'}
            ])
        
        if len(moderate_weeks) > 0:
            recommendations.append({'title': 'Standard Protocols', 'description': 'Maintain routine prevention and monitoring measures'})
        
        # Always include general recommendations
        recommendations.extend([
            {'title': 'Weather Monitoring', 'description': 'Track rainfall and temperature patterns for breeding sites'},
            {'title': 'Community Alerts', 'description': 'Keep public notification systems active and updated'}
        ])
        
        return recommendations