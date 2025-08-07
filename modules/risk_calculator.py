import logging
from datetime import datetime

class RiskCalculator:
    def __init__(self):
        # Environmental and behavioral risk factors with weights
        self.risk_factors = {
            'stagnant_water': {
                'weight': 3,
                'description': 'Stagnant water near home'
            },
            'mosquito_increase': {
                'weight': 2,
                'description': 'Noticed increase in mosquitoes'
            },
            'recent_travel': {
                'weight': 2,
                'description': 'Recent travel to dengue-affected areas'
            },
            'sick_contacts': {
                'weight': 2,
                'description': 'Contact with dengue patients'
            },
            'poor_drainage': {
                'weight': 2,
                'description': 'Poor drainage in your area'
            },
            'water_storage': {
                'weight': 2,
                'description': 'Uncovered water storage containers'
            },
            'garden_plants': {
                'weight': 1,
                'description': 'Many potted plants or garden'
            },
            'construction_nearby': {
                'weight': 1,
                'description': 'Construction activity nearby'
            },
            'ac_cooler': {
                'weight': 1,
                'description': 'Air cooler or AC with water collection'
            },
            'garbage_collection': {
                'weight': 1,
                'description': 'Irregular garbage collection'
            }
        }
        
    def calculate_risk(self, factors):
        """Calculate dengue risk score based on environmental factors"""
        try:
            total_score = 0
            present_factors = []
            
            # Calculate total risk score
            for factor, present in factors.items():
                if present and factor in self.risk_factors:
                    weight = self.risk_factors[factor]['weight']
                    description = self.risk_factors[factor]['description']
                    total_score += weight
                    present_factors.append({
                        'factor': factor,
                        'description': description,
                        'weight': weight
                    })
            
            # Determine risk level based on score
            max_possible_score = sum(factor['weight'] for factor in self.risk_factors.values())
            risk_percentage = (total_score / max_possible_score) * 100
            
            if total_score >= 12:
                risk_level = "Very High"
                risk_color = "danger"
                urgency = "Immediate action required"
                priority_actions = [
                    "🚨 URGENT: Remove all stagnant water immediately",
                    "Apply mosquito control measures today",
                    "Use personal protection consistently",
                    "Consider professional pest control"
                ]
            elif total_score >= 8:
                risk_level = "High"
                risk_color = "warning"
                urgency = "Take action within 24 hours"
                priority_actions = [
                    "⚠️ Remove stagnant water sources",
                    "Increase mosquito control measures",
                    "Use repellents and protective clothing",
                    "Improve drainage around property"
                ]
            elif total_score >= 5:
                risk_level = "Medium"
                risk_color = "info"
                urgency = "Take preventive action this week"
                priority_actions = [
                    "ℹ️ Weekly inspection for breeding sites",
                    "Cover water storage containers",
                    "Use mosquito nets and repellents",
                    "Maintain clean surroundings"
                ]
            elif total_score >= 2:
                risk_level = "Low-Medium"
                risk_color = "primary"
                urgency = "Continue preventive measures"
                priority_actions = [
                    "✓ Regular cleaning and maintenance",
                    "Monitor for mosquito activity",
                    "Keep water containers covered",
                    "Maintain good sanitation"
                ]
            else:
                risk_level = "Low"
                risk_color = "success"
                urgency = "Maintain current practices"
                priority_actions = [
                    "✅ Continue good practices",
                    "Stay vigilant for changes",
                    "Regular property maintenance",
                    "Community awareness"
                ]
            
            # Generate detailed recommendations
            detailed_recommendations = self._generate_detailed_recommendations(present_factors, risk_level)
            
            # Risk factor analysis
            high_risk_factors = [f for f in present_factors if f['weight'] >= 3]
            medium_risk_factors = [f for f in present_factors if f['weight'] == 2]
            low_risk_factors = [f for f in present_factors if f['weight'] == 1]
            
            return {
                'risk_level': risk_level,
                'risk_color': risk_color,
                'total_score': total_score,
                'max_score': max_possible_score,
                'risk_percentage': round(risk_percentage, 1),
                'urgency': urgency,
                'present_factors': present_factors,
                'high_risk_factors': high_risk_factors,
                'medium_risk_factors': medium_risk_factors,
                'low_risk_factors': low_risk_factors,
                'priority_actions': priority_actions,
                'detailed_recommendations': detailed_recommendations,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logging.error(f"Risk calculation error: {str(e)}")
            raise e
    
    def _generate_detailed_recommendations(self, present_factors, risk_level):
        """Generate detailed recommendations based on identified factors"""
        recommendations = []
        
        factor_names = [f['factor'] for f in present_factors]
        
        if 'stagnant_water' in factor_names:
            recommendations.extend([
                "🌊 WATER MANAGEMENT:",
                "• Check and empty water from flower pots, buckets, containers",
                "• Clean bird baths and pet water dishes weekly",
                "• Fix leaky pipes and faucets immediately",
                "• Ensure proper drainage in garden areas"
            ])
        
        if 'mosquito_increase' in factor_names:
            recommendations.extend([
                "🦟 MOSQUITO CONTROL:",
                "• Use mosquito nets while sleeping",
                "• Apply EPA-approved repellents",
                "• Install screens on windows and doors",
                "• Use fans to create air circulation"
            ])
        
        if 'water_storage' in factor_names:
            recommendations.extend([
                "💧 WATER STORAGE:",
                "• Cover all water storage tanks and containers",
                "• Clean storage containers weekly",
                "• Use tight-fitting lids on water containers",
                "• Add mosquito dunks to permanent water features"
            ])
        
        if 'garden_plants' in factor_names:
            recommendations.extend([
                "🌱 GARDEN MANAGEMENT:",
                "• Remove water from plant saucers daily",
                "• Trim overgrown vegetation",
                "• Use sand instead of water in plant saucers",
                "• Maintain proper plant spacing for air circulation"
            ])
        
        if 'poor_drainage' in factor_names:
            recommendations.extend([
                "🏠 PROPERTY MAINTENANCE:",
                "• Clear blocked drains and gutters",
                "• Level uneven ground to prevent water pooling",
                "• Install proper drainage systems",
                "• Contact local authorities about public drainage issues"
            ])
        
        # Add general recommendations based on risk level
        if risk_level in ["Very High", "High"]:
            recommendations.extend([
                "⚡ IMMEDIATE ACTIONS:",
                "• Conduct daily property inspections",
                "• Coordinate with neighbors for area-wide prevention",
                "• Contact local health authorities if needed",
                "• Consider professional pest control consultation"
            ])
        
        return recommendations
