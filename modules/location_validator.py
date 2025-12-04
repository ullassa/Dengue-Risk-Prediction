import os
import pandas as pd
import logging
from typing import List, Dict, Tuple, Optional

class KarnatakaLocationValidator:
    """Validates and manages Karnataka location data for the Dengue Risk Prediction System"""
    
    def __init__(self):
        # Get the directory of the current file and build absolute paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # Go up one level from modules/
        self.cities_file = os.path.join(project_root, 'datasets', 'cities.csv')
        
        # Load Karnataka cities data
        self.karnataka_cities = self._load_karnataka_cities()
        
        # Extended city name variations for better matching
        self.city_variations = {
            'bangalore': ['bangalore', 'bengaluru', 'blr', 'bangaluru'],
            'mysore': ['mysore', 'mysuru', 'mysooru'],
            'hubli': ['hubli', 'hubali', 'hubballi', 'dharwad'],
            'mangalore': ['mangalore', 'mangaluru', 'mangalur', 'dakshina kannada'],
            'belgaum': ['belgaum', 'belagavi', 'belgavi'],
            'tumkur': ['tumkur', 'tumakuru', 'tumakur'],
            'shimoga': ['shimoga', 'shivamogga', 'shivamoga'],
            'davangere': ['davangere', 'davanagere'],
            'bellary': ['bellary', 'ballari', 'balari'],
            'bijapur': ['bijapur', 'vijayapura', 'vijayapur'],
            'gulbarga': ['gulbarga', 'kalaburagi', 'kalburgi'],
            'raichur': ['raichur', 'raychur']
        }
        
    def _load_karnataka_cities(self) -> pd.DataFrame:
        """Load Karnataka cities from CSV file"""
        try:
            if os.path.exists(self.cities_file):
                df = pd.read_csv(self.cities_file)
                # Filter only Karnataka cities (should already be Karnataka-only)
                karnataka_df = df[df['state'].str.lower() == 'karnataka'].copy()
                logging.info(f"Loaded {len(karnataka_df)} Karnataka cities from {self.cities_file}")
                return karnataka_df
            else:
                logging.error(f"Cities file not found at {self.cities_file}")
                return pd.DataFrame(columns=['city', 'state', 'district'])
        except Exception as e:
            logging.error(f"Error loading Karnataka cities data: {str(e)}")
            return pd.DataFrame(columns=['city', 'state', 'district'])
    
    def is_valid_karnataka_location(self, location: str) -> bool:
        """Check if the given location is a valid Karnataka city"""
        try:
            normalized_location = self.normalize_location_name(location)
            if normalized_location is None:
                return False
            
            # Check if normalized location exists in our Karnataka cities
            city_match = self.karnataka_cities[
                self.karnataka_cities['city'].str.lower() == normalized_location.lower()
            ]
            
            return not city_match.empty
        except Exception as e:
            logging.error(f"Error validating location {location}: {str(e)}")
            return False
    
    def normalize_location_name(self, location: str) -> Optional[str]:
        """Normalize location name to match dataset entries"""
        location_lower = location.lower().strip()
        
        # Check direct mapping
        for canonical_name, variations in self.city_variations.items():
            if location_lower in variations:
                return canonical_name.title()  # Return with proper case (Bangalore, Mysore, etc.)
        
        # Check if it's already a valid Karnataka city name
        city_match = self.karnataka_cities[
            self.karnataka_cities['city'].str.lower() == location_lower
        ]
        
        if not city_match.empty:
            return city_match.iloc[0]['city']  # Return the canonical name from dataset
        
        return None
    
    def get_karnataka_cities_list(self) -> List[str]:
        """Get list of all Karnataka cities"""
        if not self.karnataka_cities.empty:
            return sorted(self.karnataka_cities['city'].tolist())
        return []
    
    def get_city_details(self, location: str) -> Optional[Dict[str, str]]:
        """Get detailed information about a Karnataka city"""
        normalized_location = self.normalize_location_name(location)
        if normalized_location is None:
            return None
        
        city_match = self.karnataka_cities[
            self.karnataka_cities['city'].str.lower() == normalized_location.lower()
        ]
        
        if not city_match.empty:
            row = city_match.iloc[0]
            return {
                'city': row['city'],
                'state': row['state'], 
                'district': row['district']
            }
        
        return None
    
    def suggest_similar_karnataka_cities(self, location: str, max_suggestions: int = 3) -> List[str]:
        """Suggest similar Karnataka cities if the entered location is invalid"""
        location_lower = location.lower()
        suggestions = []
        
        # Look for partial matches
        for city in self.karnataka_cities['city']:
            city_lower = city.lower()
            if (location_lower in city_lower or 
                city_lower in location_lower or 
                any(variation in city_lower for variation in location_lower.split())):
                suggestions.append(city)
        
        # If no partial matches, suggest popular cities
        if not suggestions:
            popular_cities = ['Bangalore', 'Mysore', 'Mangalore', 'Hubli', 'Belgaum']
            suggestions = [city for city in popular_cities if city in self.get_karnataka_cities_list()]
        
        return suggestions[:max_suggestions]
    
    def validate_and_normalize(self, location: str) -> Tuple[bool, Optional[str], List[str]]:
        """
        Comprehensive validation that returns:
        - is_valid: boolean indicating if location is valid
        - normalized_name: the correct Karnataka city name if valid
        - suggestions: list of suggested Karnataka cities if invalid
        """
        try:
            # Try to normalize the location
            normalized = self.normalize_location_name(location)
            
            if normalized and self.is_valid_karnataka_location(normalized):
                return True, normalized, []
            else:
                # Invalid location - provide suggestions
                suggestions = self.suggest_similar_karnataka_cities(location)
                return False, None, suggestions
        except Exception as e:
            logging.error(f"Error in validate_and_normalize for {location}: {str(e)}")
            return False, None, ['Bangalore', 'Mysore', 'Mangalore']