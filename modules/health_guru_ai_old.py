import os
import requests
import json
from datetime import datetime
import logging

class HealthGuruAI:
    def __init__(self):
        # Try multiple free API options
        self.huggingface_token = os.getenv('HUGGINGFACE_API_TOKEN', 'demo_mode')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'demo_mode')
        
        # Use Hugging Face free inference API as primary
        self.use_huggingface = self.huggingface_token != 'demo_mode'
        self.use_openai = self.openai_api_key != 'demo_mode'
        
        # Free model endpoints (no API key required for public models)
        self.hf_models = [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill", 
            "microsoft/DialoGPT-large"
        ]
        
        # Health Guru personality and knowledge base
        self.system_prompt = """You are HealthGuru, an AI assistant specialized in dengue fever prevention and healthcare guidance for Karnataka, India. 

PERSONALITY:
- Friendly, professional, and empathetic
- Use simple language that everyone can understand
- Always provide actionable advice
- Show concern for user's health and wellbeing

EXPERTISE AREAS:
- Dengue fever symptoms, prevention, and treatment
- Weather-related health risks (temperature, humidity, rainfall effects)
- Mosquito control and breeding prevention
- Karnataka-specific health information
- General wellness and prevention tips
- When to seek medical help

GUIDELINES:
1. Always emphasize consulting healthcare professionals for serious symptoms
2. Provide practical, actionable prevention advice
3. Explain weather-health connections clearly
4. Mention local Karnataka hospitals when relevant
5. Stay positive but realistic about health risks
6. Use emojis sparingly but effectively
7. Keep responses concise (2-3 paragraphs max)

MEDICAL DISCLAIMER: Always remind users that you provide general information only, not medical diagnosis or treatment. Emergency cases should call 108 or visit nearest hospital.

Sample topics you excel at:
- "How to prevent dengue during monsoon?"
- "What symptoms should worry me?"
- "Best mosquito control for my home"
- "Is it safe to travel during dengue season?"
- "How does weather affect dengue risk?"
"""

        # Demo responses for when API is not available
        self.demo_responses = {
            'greeting': "Hello! I'm HealthGuru, your AI healthcare assistant. I'm here to help you with dengue prevention, symptom guidance, and health advice specific to Karnataka. How can I help you stay healthy today? 🌟",
            
            'dengue_symptoms': "Common dengue symptoms include sudden high fever (40°C/104°F), severe headache, pain behind eyes, muscle and joint pain, and skin rash. ⚠️ Warning signs: severe abdominal pain, persistent vomiting, difficulty breathing, or bleeding. If you experience these, please visit a hospital immediately or call 108. Early detection saves lives! 🏥",
            
            'prevention': "Great question! Here are key dengue prevention steps: 1) Remove stagnant water from containers, flower pots, and coolers 2) Use mosquito nets and repellents 3) Wear long-sleeved clothes during dawn/dusk 4) Keep your surroundings clean. Remember: Aedes mosquitoes breed in clean, stagnant water and bite during daytime! 🦟",
            
            'weather': "Weather plays a huge role in dengue risk! Temperature 25-30°C + humidity 70%+ creates perfect breeding conditions. During Karnataka's monsoon, risk increases due to water collection. Check our weather prediction feature for your city's current risk level. Stay extra vigilant during rainy seasons! 🌧️",
            
            'when_doctor': "Consult a doctor if you have: fever above 38.5°C for 2+ days, severe headache, body pain, nausea, or skin rash. Don't wait for all symptoms! Early medical care prevents complications. Use our doctor consultation feature to find nearby healthcare providers or book online consultations. Your health matters! 👨‍⚕️",
            
            'emergency': "🚨 EMERGENCY SIGNS: Severe stomach pain, persistent vomiting, difficulty breathing, skin bleeding, or sudden weakness. IMMEDIATE ACTION: Call 108 (ambulance) or visit nearest hospital. Don't delay! In Karnataka, major hospitals include: Manipal, Apollo, Fortis. Time is critical in dengue complications!",
            
            'general_health': "I'm here to help with dengue prevention, symptom guidance, weather-health connections, and general wellness tips for Karnataka residents. You can ask me about mosquito control, when to see a doctor, travel safety during dengue season, or how to use our prediction tools effectively! 💚"
        }
    
    def get_ai_response(self, user_message, user_context=None):
        """Get AI response from OpenAI or demo mode"""
        try:
            if self.demo_mode:
                return self._get_demo_response(user_message)
            else:
                return self._get_openai_response(user_message, user_context)
        except Exception as e:
            logging.error(f"HealthGuru AI error: {str(e)}")
            return self._get_fallback_response(user_message)
    
    def _get_demo_response(self, user_message):
        """Provide intelligent demo responses"""
        message_lower = user_message.lower()
        
        # Pattern matching for demo responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start', 'help']):
            return self.demo_responses['greeting']
        elif any(word in message_lower for word in ['symptom', 'fever', 'headache', 'pain', 'rash']):
            return self.demo_responses['dengue_symptoms']
        elif any(word in message_lower for word in ['prevent', 'avoid', 'stop', 'protect', 'mosquito']):
            return self.demo_responses['prevention']
        elif any(word in message_lower for word in ['weather', 'rain', 'humidity', 'temperature', 'climate']):
            return self.demo_responses['weather']
        elif any(word in message_lower for word in ['doctor', 'hospital', 'medical', 'when', 'consult']):
            return self.demo_responses['when_doctor']
        elif any(word in message_lower for word in ['emergency', 'urgent', 'serious', 'dangerous', 'help']):
            return self.demo_responses['emergency']
        else:
            return self.demo_responses['general_health']
    
    def _get_openai_response(self, user_message, user_context):
        """Get response from OpenAI API using new format"""
        try:
            from openai import OpenAI
            
            # Initialize the client
            client = OpenAI(api_key=self.openai_api_key)
            
            context_info = ""
            if user_context:
                context_info = f"\nUser Context: Location: {user_context.get('city', 'Karnataka')}, Recent Risk Level: {user_context.get('risk_level', 'Unknown')}, Symptoms: {user_context.get('symptoms', 'None reported')}"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt + context_info},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            logging.warning("OpenAI library not available - using demo mode")
            return self._get_demo_response(user_message)
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return self._get_demo_response(user_message)
    
    def _get_fallback_response(self, user_message):
        """Fallback response when everything fails"""
        return """I'm HealthGuru, your AI healthcare assistant! I'm here to help with dengue prevention and health guidance. 

For immediate help:
🚨 Emergency: Call 108
🏥 Dengue symptoms: High fever, headache, body pain, rash
🦟 Prevention: Remove stagnant water, use repellents, wear protective clothing
💊 Consult doctor: For fever above 38.5°C lasting 2+ days

Use our other features:
• Symptom checker for risk assessment
• Weather prediction for your city
• Doctor consultation booking
• Local dengue alerts

How else can I help you stay healthy?"""

    def get_quick_suggestions(self):
        """Get quick suggestion buttons for the chat interface"""
        return [
            "How to prevent dengue?",
            "What are dengue symptoms?",
            "When should I see a doctor?",
            "How does weather affect dengue?",
            "Emergency signs to watch for",
            "Mosquito control tips"
        ]

# Global instance
health_guru = HealthGuruAI()