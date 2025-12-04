from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import logging

# Create a blueprint for doctor consultation
doctor_bp = Blueprint('doctor', __name__)

class DoctorConsultation:
    def __init__(self):
        # Karnataka doctors database with telemedicine options
        self.doctors = {
            'Bangalore': [
                {
                    'name': 'Dr. Rajesh Kumar',
                    'specialization': 'General Physician',
                    'hospital': 'Manipal Hospital',
                    'phone': '+91-8041234567',
                    'online_booking': 'https://www.practo.com/bangalore/doctor/dr-rajesh-kumar',
                    'availability': 'Mon-Sat 9AM-6PM',
                    'rating': 4.8
                },
                {
                    'name': 'Dr. Priya Sharma',
                    'specialization': 'Infectious Disease Specialist',
                    'hospital': 'Apollo Hospital',
                    'phone': '+91-8041234568',
                    'online_booking': 'https://www.apollo247.com/doctors/dr-priya-sharma',
                    'availability': 'Mon-Fri 10AM-5PM',
                    'rating': 4.9
                },
                {
                    'name': 'Dr. Amit Singh',
                    'specialization': 'Emergency Medicine',
                    'hospital': 'Fortis Hospital',
                    'phone': '+91-8041234569',
                    'online_booking': 'https://www.1mg.com/doctors/dr-amit-singh',
                    'availability': '24/7 Emergency',
                    'rating': 4.7
                }
            ],
            'Mysore': [
                {
                    'name': 'Dr. Kavya Reddy',
                    'specialization': 'General Physician',
                    'hospital': 'JSS Hospital',
                    'phone': '+91-8212345678',
                    'online_booking': 'https://www.practo.com/mysore/doctor/dr-kavya-reddy',
                    'availability': 'Mon-Sat 9AM-5PM',
                    'rating': 4.6
                },
                {
                    'name': 'Dr. Suresh Babu',
                    'specialization': 'Internal Medicine',
                    'hospital': 'Apollo BGS Hospital',
                    'phone': '+91-8212345679',
                    'online_booking': 'https://www.apollo247.com/doctors/dr-suresh-babu',
                    'availability': 'Tue-Sun 10AM-4PM',
                    'rating': 4.5
                }
            ],
            'Hubli': [
                {
                    'name': 'Dr. Manjunath Patil',
                    'specialization': 'General Physician',
                    'hospital': 'KIMS Hospital',
                    'phone': '+91-8363456789',
                    'online_booking': 'https://www.practo.com/hubli/doctor/dr-manjunath-patil',
                    'availability': 'Mon-Sat 8AM-6PM',
                    'rating': 4.4
                }
            ],
            'Mangalore': [
                {
                    'name': 'Dr. Deepa Shetty',
                    'specialization': 'Tropical Medicine',
                    'hospital': 'KMC Hospital',
                    'phone': '+91-8242567890',
                    'online_booking': 'https://www.apollo247.com/doctors/dr-deepa-shetty',
                    'availability': 'Mon-Fri 9AM-5PM',
                    'rating': 4.8
                }
            ]
        }
        
        # Emergency contacts
        self.emergency_contacts = {
            'Karnataka Health Emergency': '104',
            'National Health Helpline': '1075',
            'Dengue Control Room': '080-22867000',
            'Ambulance': '108'
        }
        
        # Telemedicine platforms
        self.telemedicine_platforms = [
            {
                'name': 'Practo',
                'url': 'https://www.practo.com/online-doctor-consultation',
                'description': 'Consult with verified doctors online',
                'available': '24/7'
            },
            {
                'name': 'Apollo 24/7',
                'url': 'https://www.apollo247.com/consult-online',
                'description': 'Apollo doctors available for consultation',
                'available': '24/7'
            },
            {
                'name': '1mg',
                'url': 'https://www.1mg.com/online-doctor-consultation',
                'description': 'Online doctor consultation and medicine delivery',
                'available': '24/7'
            }
        ]
    
    def get_doctors_by_city(self, city):
        """Get doctors list for a specific city"""
        return self.doctors.get(city, [])
    
    def get_emergency_contacts(self):
        """Get emergency contact numbers"""
        return self.emergency_contacts
    
    def get_telemedicine_options(self):
        """Get telemedicine platform options"""
        return self.telemedicine_platforms
    
    def should_show_consultation(self, risk_level, symptoms_count=0):
        """Determine if doctor consultation should be recommended"""
        high_risk_conditions = [
            risk_level in ['High', 'Very High', 'Critical'],
            symptoms_count >= 3,
        ]
        return any(high_risk_conditions)
    
    def get_consultation_urgency(self, risk_level, symptoms_count=0):
        """Determine consultation urgency level"""
        if risk_level in ['Critical', 'Very High'] or symptoms_count >= 4:
            return 'immediate'
        elif risk_level == 'High' or symptoms_count >= 2:
            return 'within_24_hours'
        else:
            return 'routine'
    
    def generate_consultation_recommendation(self, risk_level, city, symptoms_count=0):
        """Generate personalized consultation recommendation"""
        urgency = self.get_consultation_urgency(risk_level, symptoms_count)
        doctors = self.get_doctors_by_city(city)
        
        recommendation = {
            'show_consultation': self.should_show_consultation(risk_level, symptoms_count),
            'urgency': urgency,
            'doctors': doctors,
            'emergency_contacts': self.emergency_contacts,
            'telemedicine': self.telemedicine_platforms,
            'message': self._get_urgency_message(urgency),
            'next_steps': self._get_next_steps(urgency, symptoms_count)
        }
        
        return recommendation
    
    def _get_urgency_message(self, urgency):
        """Get appropriate message based on urgency"""
        messages = {
            'immediate': '🚨 Immediate medical attention required! Contact emergency services or visit nearest hospital.',
            'within_24_hours': '⚠️ Consult a doctor within 24 hours for proper evaluation and treatment.',
            'routine': '💡 Consider consulting a doctor for preventive care and health advice.'
        }
        return messages.get(urgency, '')
    
    def _get_next_steps(self, urgency, symptoms_count):
        """Get recommended next steps"""
        if urgency == 'immediate':
            return [
                'Call emergency services (108) immediately',
                'Visit nearest hospital emergency room',
                'Inform family members about your condition',
                'Carry ID and medical records if available'
            ]
        elif urgency == 'within_24_hours':
            return [
                'Book an appointment with a general physician',
                'Monitor symptoms and note any changes',
                'Stay hydrated and take rest',
                'Avoid self-medication',
                'Consider telemedicine consultation if unable to visit'
            ]
        else:
            return [
                'Schedule a routine health checkup',
                'Discuss prevention strategies with doctor',
                'Review your health profile and risk factors',
                'Consider vaccination if recommended'
            ]

# Global instance
doctor_consultation = DoctorConsultation()

@doctor_bp.route('/test')
def test_consultation():
    """Simple test route"""
    return "<h1>Doctor Consultation Module Working!</h1><p>Blueprint is properly registered.</p>"

@doctor_bp.route('/consultation-data')
def get_consultation_data():
    """API endpoint to get consultation data"""
    city = request.args.get('city', 'Bangalore')
    risk_level = request.args.get('risk_level', 'Moderate')
    symptoms_count = int(request.args.get('symptoms_count', 0))
    
    recommendation = doctor_consultation.generate_consultation_recommendation(
        risk_level, city, symptoms_count
    )
    
    return jsonify(recommendation)

@doctor_bp.route('/book-consultation')
def book_consultation():
    """Render consultation booking page"""
    try:
        city = request.args.get('city', 'Bangalore')
        risk_level = request.args.get('risk_level', 'High')
        symptoms_count = int(request.args.get('symptoms_count', 0))
        
        recommendation = doctor_consultation.generate_consultation_recommendation(
            risk_level, city, symptoms_count
        )
        
        return render_template('book_consultation.html', 
                             recommendation=recommendation,
                             city=city,
                             risk_level=risk_level)
    except Exception as e:
        logging.error(f"Doctor consultation error: {str(e)}")
        # Fallback to a simple page if there's an error
        return f"""
        <html><body style="font-family: Arial; padding: 20px; background: #1a1a2e;">
            <div style="background: white; padding: 20px; border-radius: 10px;">
                <h2>🩺 Doctor Consultation</h2>
                <p><strong>City:</strong> {city}</p>
                <p><strong>Risk Level:</strong> {risk_level}</p>
                <h3>Quick Options:</h3>
                <a href="https://www.practo.com" target="_blank" style="display:inline-block; background:#007bff; color:white; padding:10px; text-decoration:none; margin:5px;">Practo Online</a>
                <a href="https://www.apollo247.com" target="_blank" style="display:inline-block; background:#28a745; color:white; padding:10px; text-decoration:none; margin:5px;">Apollo 24/7</a>
                <a href="tel:108" style="display:inline-block; background:#dc3545; color:white; padding:10px; text-decoration:none; margin:5px;">Emergency: 108</a>
                <br><br>
                <a href="/" style="display:inline-block; background:#6c757d; color:white; padding:10px; text-decoration:none;">Back to Dashboard</a>
            </div>
        </body></html>
        """