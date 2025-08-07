import logging
from datetime import datetime

class SymptomChecker:
    def __init__(self):
        # WHO-based symptom weights for dengue
        self.symptom_weights = {
            'fever': 4,          # Most important symptom
            'headache': 2,       # Common symptom
            'joint_pain': 3,     # Characteristic symptom
            'muscle_pain': 2,    # Common symptom
            'rash': 2,           # Characteristic symptom
            'nausea': 1,         # Mild symptom
            'vomiting': 2,       # More serious
            'bleeding': 4        # Warning sign
        }
        
    def check_symptoms(self, symptoms):
        """Assess dengue risk based on symptoms according to WHO guidelines"""
        try:
            total_score = 0
            present_symptoms = []
            warning_signs = []
            
            # Calculate symptom score
            for symptom, present in symptoms.items():
                if present:
                    total_score += self.symptom_weights.get(symptom, 0)
                    present_symptoms.append(symptom.replace('_', ' ').title())
                    
                    # Check for warning signs
                    if symptom in ['bleeding', 'vomiting'] and present:
                        warning_signs.append(symptom.replace('_', ' ').title())
            
            # Determine risk level based on WHO criteria
            if total_score >= 8 or 'bleeding' in [s.lower() for s in present_symptoms]:
                risk_level = "High"
                risk_color = "danger"
                urgency = "Immediate medical attention required"
                recommendations = [
                    "🚨 SEEK IMMEDIATE MEDICAL ATTENTION",
                    "Go to the nearest hospital or healthcare center",
                    "Do not take aspirin or ibuprofen",
                    "Monitor for signs of shock or severe bleeding",
                    "Stay hydrated with oral rehydration solution"
                ]
            elif total_score >= 5 or len(present_symptoms) >= 3:
                risk_level = "Medium"
                risk_color = "warning"
                urgency = "Medical consultation recommended"
                recommendations = [
                    "Consult a healthcare provider within 24 hours",
                    "Monitor symptoms closely",
                    "Rest and maintain fluid intake",
                    "Avoid aspirin and NSAIDs",
                    "Use paracetamol for fever if needed"
                ]
            elif total_score >= 2:
                risk_level = "Low-Medium"
                risk_color = "info"
                urgency = "Monitor symptoms and consider medical advice"
                recommendations = [
                    "Monitor symptoms for 24-48 hours",
                    "Rest and stay hydrated",
                    "Avoid mosquito bites",
                    "Seek medical advice if symptoms worsen",
                    "Maintain fever diary if present"
                ]
            else:
                risk_level = "Low"
                risk_color = "success"
                urgency = "Continue preventive measures"
                recommendations = [
                    "Continue dengue prevention measures",
                    "Stay alert for symptom development",
                    "Maintain good hygiene",
                    "Avoid mosquito breeding sites"
                ]
            
            # Generate WHO-based assessment
            who_notes = []
            if 'fever' in [s.lower() for s in present_symptoms]:
                who_notes.append("Fever is the most common symptom of dengue")
            if any(symptom in ['joint_pain', 'muscle_pain'] for symptom in [s.lower().replace(' ', '_') for s in present_symptoms]):
                who_notes.append("Body aches are characteristic of dengue fever")
            if warning_signs:
                who_notes.append("⚠️ Warning signs detected - immediate medical care needed")
            
            return {
                'risk_level': risk_level,
                'risk_color': risk_color,
                'total_score': total_score,
                'present_symptoms': present_symptoms,
                'warning_signs': warning_signs,
                'urgency': urgency,
                'recommendations': recommendations,
                'who_notes': who_notes,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logging.error(f"Symptom check error: {str(e)}")
            raise e
