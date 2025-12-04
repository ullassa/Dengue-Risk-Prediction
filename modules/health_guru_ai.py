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
        
        # Free model endpoints
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
        
    def get_ai_response(self, user_message, user_context=None):
        """Get AI response from multiple sources with fallback"""
        try:
            # Try Hugging Face first (best free option)
            if self.use_huggingface:
                response = self._get_huggingface_response(user_message, user_context)
                if response:
                    return response
            
            # Try OpenAI if available
            if self.use_openai:
                response = self._get_openai_response(user_message, user_context)
                if response:
                    return response
            
            # Try free Hugging Face inference without token
            response = self._get_free_hf_response(user_message, user_context)
            if response:
                return response
                
            # Fallback to enhanced demo responses
            return self._get_enhanced_demo_response(user_message)
            
        except Exception as e:
            logging.error(f"HealthGuru AI error: {str(e)}")
            return self._get_fallback_response(user_message)
    
    def _get_huggingface_response(self, user_message, user_context):
        """Get response from Hugging Face API"""
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_token}"}
            
            # Prepare context-aware prompt
            context_info = ""
            if user_context:
                context_info = f" User is in {user_context.get('city', 'Karnataka')}, recent risk level: {user_context.get('risk_level', 'Unknown')}."
            
            prompt = f"{self.system_prompt}\n\nUser Context:{context_info}\nUser Question: {user_message}\n\nHealthGuru Response:"
            
            # Try different models
            for model in self.hf_models:
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{model}"
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_length": 200,
                            "temperature": 0.7,
                            "do_sample": True,
                            "top_p": 0.9
                        }
                    }
                    
                    response = requests.post(api_url, headers=headers, json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            # Extract response after prompt
                            if 'HealthGuru Response:' in generated_text:
                                ai_response = generated_text.split('HealthGuru Response:')[-1].strip()
                                if ai_response and len(ai_response) > 10:
                                    return self._clean_response(ai_response)
                except Exception as model_error:
                    logging.warning(f"Model {model} failed: {str(model_error)}")
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Hugging Face API error: {str(e)}")
            return None
    
    def _get_free_hf_response(self, user_message, user_context):
        """Get response from free Hugging Face inference (no token required)"""
        try:
            # Use free public models
            free_models = [
                "microsoft/DialoGPT-medium",
                "facebook/blenderbot-400M-distill"
            ]
            
            for model in free_models:
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{model}"
                    
                    # Simplified prompt for free models
                    health_prompt = f"As a health assistant for dengue prevention in Karnataka: {user_message}"
                    
                    payload = {
                        "inputs": health_prompt,
                        "parameters": {
                            "max_length": 150,
                            "temperature": 0.8
                        }
                    }
                    
                    response = requests.post(api_url, json=payload, timeout=8)
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            if generated_text and len(generated_text) > 20:
                                return self._clean_response(generated_text) + "\n\n⚕️ *This information is for educational purposes. Consult healthcare professionals for medical advice.*"
                                
                except Exception as model_error:
                    continue
            
            return None
            
        except Exception as e:
            logging.warning(f"Free HF inference error: {str(e)}")
            return None
    
    def _clean_response(self, response):
        """Clean and format AI response"""
        # Remove prompt repetition and clean text
        response = response.replace("As a health assistant for dengue prevention in Karnataka:", "")
        response = response.replace("User Question:", "")
        response = response.replace("HealthGuru Response:", "")
        
        # Split into sentences and take meaningful ones
        sentences = response.split('.')
        cleaned_sentences = []
        
        for sentence in sentences[:4]:  # Limit to 4 sentences
            sentence = sentence.strip()
            if len(sentence) > 10 and not sentence.startswith("User") and not sentence.startswith("Question"):
                cleaned_sentences.append(sentence)
        
        if cleaned_sentences:
            return '. '.join(cleaned_sentences) + '.'
        
        return response.strip()
    
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
            logging.warning("OpenAI library not available - falling back")
            return None
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return None
    
    def _get_enhanced_demo_response(self, user_message):
        """Enhanced demo responses with comprehensive coverage"""
        message_lower = user_message.lower()
        
        # Expanded keyword matching for better coverage
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening', 'greetings']):
            return "Hello! I'm HealthGuru, your AI healthcare assistant for dengue prevention in Karnataka! 🌟 I can help with symptoms, prevention, weather risks, when to see doctors, and emergency guidance. What health question can I help you with today?"
            
        elif any(word in message_lower for word in ['symptom', 'fever', 'headache', 'pain', 'rash', 'nausea', 'vomit']):
            return "Common dengue symptoms include sudden high fever (40°C/104°F), severe headache, pain behind eyes, muscle and joint pain, and skin rash. ⚠️ **Warning signs:** severe abdominal pain, persistent vomiting, difficulty breathing, or bleeding. If you experience these, visit a hospital immediately or call 108. Early detection saves lives! 🏥"
            
        elif any(word in message_lower for word in ['prevent', 'avoid', 'stop', 'control', 'mosquito', 'bite']):
            return "Excellent question! **Dengue prevention steps:** 1) Remove stagnant water from containers, flower pots, coolers 2) Use mosquito nets and repellents 3) Wear long-sleeved clothes during dawn/dusk 4) Keep surroundings clean 5) Use mosquito coils/vaporizers. **Remember:** Aedes mosquitoes breed in clean, stagnant water and bite during daytime! 🦟"
            
        elif any(word in message_lower for word in ['weather', 'rain', 'humidity', 'temperature', 'climate', 'monsoon']):
            return "Weather greatly affects dengue risk! **High risk conditions:** Temperature 25-30°C + humidity 70%+ creates perfect mosquito breeding. During Karnataka's monsoon (June-September), risk increases due to water collection. **Check our weather prediction feature** for your city's current risk level. Stay extra vigilant during rainy seasons! 🌧️"
            
        elif any(word in message_lower for word in ['doctor', 'hospital', 'medical', 'when', 'consult', 'visit']):
            return "**Consult a doctor immediately if you have:** fever above 38.5°C for 2+ days, severe headache, body pain, nausea, or skin rash. **Don't wait for all symptoms!** Early medical care prevents complications. **Use our doctor consultation feature** to find nearby healthcare providers or book online consultations. Your health matters! 👨‍⚕️"
            
        elif any(word in message_lower for word in ['emergency', 'urgent', 'serious', 'dangerous', 'help', 'ambulance']):
            return "🚨 **EMERGENCY SIGNS:** Severe stomach pain, persistent vomiting, difficulty breathing, skin bleeding, sudden weakness, or rapid pulse drop. **IMMEDIATE ACTION:** Call 108 (ambulance) or visit nearest hospital. **Major Karnataka hospitals:** Manipal, Apollo, Fortis, NIMHANS. **Don't delay!** Time is critical in dengue complications!"
            
        elif any(word in message_lower for word in ['travel', 'trip', 'journey', 'safe', 'vacation']):
            return "**Travel safety during dengue season:** 1) Check destination's dengue status 2) Pack mosquito repellent, long-sleeved clothes 3) Stay in air-conditioned/screened accommodation 4) Avoid water-logged areas 5) Carry oral rehydration salts. **High-risk areas in Karnataka:** Bangalore, Mysore, Mangalore during monsoon. Stay safe! ✈️"
            
        elif any(word in message_lower for word in ['food', 'diet', 'eat', 'drink', 'nutrition', 'recovery']):
            return "**Dengue recovery diet:** 1) Drink lots of fluids - water, coconut water, ORS 2) Eat papaya leaves (boosts platelet count) 3) Include vitamin C foods - oranges, guava 4) Avoid oily, spicy foods 5) Take rest and sleep well. **Important:** Monitor platelet count and consult doctor for severe symptoms. 🥥"
            
        elif any(word in message_lower for word in ['child', 'baby', 'kid', 'infant', 'pediatric']):
            return "**Dengue in children:** Watch for fever, irritability, loss of appetite, skin rash. **Children dehydrate faster** - give fluids frequently. **Warning signs:** severe stomach pain, bleeding, difficulty breathing. **Seek immediate medical attention** for any concerning symptoms. Children's Hospital, Bangalore and Indira Gandhi Children's Hospital provide excellent pediatric care. 👶"
            
        elif any(word in message_lower for word in ['home', 'remedy', 'treatment', 'natural', 'cure']):
            return "**Home care for dengue:** 1) Complete bed rest 2) Drink 3-4 liters of fluids daily 3) Paracetamol for fever (NO aspirin/ibuprofen) 4) Papaya leaf juice 5) Monitor temperature and hydration. **⚠️ Important:** Home remedies support recovery but **cannot cure dengue**. Always follow doctor's advice and monitor for warning signs! 🏠"
            
        elif any(word in message_lower for word in ['medicine', 'drug', 'medication', 'pill', 'tablet']):
            return "**Dengue medications:** 1) **Safe:** Paracetamol for fever and pain 2) **AVOID:** Aspirin, ibuprofen, diclofenac (increases bleeding risk) 3) **Fluids:** ORS, coconut water, juices 4) **NO specific antiviral** exists for dengue. **Always consult doctor** before taking any medication. Self-medication can be dangerous! 💊"
            
        elif any(word in message_lower for word in ['platelet', 'blood', 'count', 'test', 'lab']):
            return "**Dengue blood tests:** 1) **NS1 Antigen** (Days 1-7) 2) **IgM/IgG Antibodies** (Day 5 onwards) 3) **Platelet count monitoring** - normal is 150,000-400,000. **Low platelets** (<100,000) need medical attention. **Complete Blood Count (CBC)** tracks recovery. Get tested if fever persists >2 days! 🔬"
            
        elif any(word in message_lower for word in ['pregnancy', 'pregnant', 'expecting', 'maternity']):
            return "**Dengue during pregnancy:** Higher risk for both mother and baby. **Immediate medical care needed** for any fever during pregnancy. **Complications:** premature delivery, low birth weight, bleeding. **Prevention crucial:** use safe repellents, avoid stagnant water, wear protective clothing. **Consult gynecologist immediately** for fever or symptoms! 🤰"
            
        else:
            # General health guidance for any other question
            return f"I'm here to help with dengue prevention and health guidance for Karnataka! 💚 **I can assist with:** symptoms identification, prevention strategies, weather-health connections, when to consult doctors, emergency guidance, travel safety, nutrition advice, medication guidance, and pregnancy-related concerns. **For your question about '{user_message[:50]}...'** - could you be more specific? This helps me provide better guidance. **Remember:** For serious symptoms, always consult healthcare professionals! 🏥"
    
    def _get_fallback_response(self, user_message):
        """Fallback response when everything fails"""
        return f"""I'm HealthGuru, your AI healthcare assistant! I'm here to help with dengue prevention and health guidance for Karnataka. 

**For immediate help:**
🚨 Emergency: Call 108
🏥 Dengue symptoms: High fever, headache, body pain, rash
🦟 Prevention: Remove stagnant water, use repellents, wear protective clothing
💊 Consult doctor: For fever above 38.5°C lasting 2+ days

**Your question:** "{user_message[:100]}..."

I can help you with specific topics like symptoms, prevention, treatment, weather risks, travel safety, diet during recovery, medications, pregnancy concerns, and when to seek medical help.

**Use our other features:**
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
            "Mosquito control tips",
            "Diet during recovery",
            "Safe medications for fever",
            "Travel safety tips",
            "Dengue in children"
        ]

# Global instance
health_guru = HealthGuruAI()