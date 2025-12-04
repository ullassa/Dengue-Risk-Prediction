# 🌤️ WEATHER API SETUP GUIDE
## Fix Live Weather Data in Production

### 🚨 **PROBLEM**
Your deployed application is showing mock weather data instead of live data because the OpenWeather API key is not configured.

### ✅ **SOLUTION STEPS**

#### **Step 1: Get OpenWeather API Key**
1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to "API Keys" section
4. Copy your API key (it looks like: `1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`)

#### **Step 2: Configure Environment Variables**

**For Local Development:**
```bash
# Create .env file in your project root
echo "OPENWEATHER_API_KEY=your_actual_api_key_here" >> .env
```

**For Render.com Deployment:**
1. Go to your Render dashboard
2. Select your deployed service
3. Go to "Environment" tab
4. Add environment variable:
   - **Key:** `OPENWEATHER_API_KEY`
   - **Value:** Your actual API key from OpenWeatherMap

**For Other Hosting Platforms:**
- **Heroku:** `heroku config:set OPENWEATHER_API_KEY=your_actual_api_key_here`
- **DigitalOcean:** Add to environment variables in app platform
- **Railway:** Add in environment variables section

#### **Step 3: Verify the Fix**

**Test Locally:**
```bash
# Test your weather API
python test_weather.py
```

**Test in Production:**
1. Redeploy your application
2. Visit your weather prediction page
3. Check that real weather data appears (no "mock data" in description)

### 🔍 **HOW TO IDENTIFY THE ISSUE**

**Signs of Mock Data:**
- Weather description shows "mock data - partly cloudy"
- Same weather values for different cities
- No real-time updates

**Signs of Working API:**
- Realistic, varied weather descriptions
- Different values for different cities
- Real-time updates every few minutes

### 🚀 **QUICK TEST**

```python
# Run this in your terminal to test
import os
import requests

api_key = os.getenv('OPENWEATHER_API_KEY')
if api_key:
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Bangalore&appid={api_key}&units=metric"
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API working!")
        data = response.json()
        print(f"Bangalore weather: {data['main']['temp']}°C")
    else:
        print("❌ API error:", response.text)
else:
    print("❌ No API key found")
```

### 📝 **DEPLOYMENT CHECKLIST**

- [ ] Obtained OpenWeather API key
- [ ] Added OPENWEATHER_API_KEY to environment variables
- [ ] Redeployed application
- [ ] Tested weather prediction feature
- [ ] Verified real weather data (not mock data)
- [ ] Confirmed for multiple Karnataka cities

### 🔧 **TROUBLESHOOTING**

**If still showing mock data:**
1. Check environment variable is exactly: `OPENWEATHER_API_KEY`
2. Verify API key is active (check OpenWeather dashboard)
3. Check application logs for API errors
4. Ensure requests library is installed: `pip install requests`

**API Rate Limits:**
- Free tier: 1000 calls/day, 60 calls/minute
- Upgrade if needed for higher usage

### 💡 **EXHIBITION TIP**
For tomorrow's exhibition, if you can't fix it immediately:
- Emphasize the AI prediction model (which works fine)
- Mention "In production, we integrate live weather APIs"
- Show the system architecture and data flow
- Focus on the comprehensive features working perfectly