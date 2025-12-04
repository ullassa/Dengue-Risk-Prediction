from modules.ai_predictor import DengueOutbreakPredictor

print('🧠 Testing AI Dengue Outbreak Prediction...')

# Initialize predictor
predictor = DengueOutbreakPredictor()

# Test prediction for Bangalore
print('\nTesting prediction for Bangalore (3 weeks ahead):')
result = predictor.predict_outbreak('Bangalore', 3)

if 'error' in result:
    print(f"❌ Error: {result['error']}")
else:
    print(f"✅ Success! AI prediction generated for {result['city']}")
    print(f"   Model: {result['model_info']['algorithm']}")
    print(f"   Features: {result['model_info']['features']}")
    print(f"   Training data: {result['model_info']['trained_on']}")
    
    print('\n📈 Weekly Predictions:')
    for pred in result['predictions']:
        print(f"   Week {pred['week']} ({pred['date']}): {pred['predicted_cases']} cases - {pred['risk_level']} risk")

print('\n🚀 AI Prediction system is ready!')