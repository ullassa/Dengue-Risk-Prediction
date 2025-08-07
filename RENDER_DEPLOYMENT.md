# Render Deployment Guide for Dengue Detection App

## 🌐 Deploy to Render with Admin Access

### 1. Prerequisites
- GitHub repository with your code
- Render account (free tier available)

### 2. Render Service Configuration

**Web Service Settings:**
```
Name: dengue-detection-app
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (leave empty)
Build Command: ./build.sh
Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
```

### 3. Environment Variables in Render

**Required Environment Variables** (set in Render dashboard):

```
DATABASE_URL=<your-render-postgres-url>
SESSION_SECRET=<generate-32-char-random-string>
FLASK_ENV=production
FLASK_DEBUG=False
ADMIN_EMAIL=your-email@domain.com
ADMIN_PASSWORD=your-secure-admin-password
```

### 4. PostgreSQL Database Setup

**Option 1: Render PostgreSQL (Recommended)**
1. Create PostgreSQL service in Render
2. Copy the "External Database URL"
3. Use it as your DATABASE_URL

**Option 2: External PostgreSQL**
- Use any PostgreSQL provider (ElephantSQL, Supabase, etc.)

### 5. Admin Access After Deployment

**Your live admin interface will be at:**
- Login: `https://your-app-name.onrender.com/login`
- Admin Dashboard: `https://your-app-name.onrender.com/admin`

**As admin you can access:**
- All user registrations from real users
- All dengue risk predictions
- Database statistics and monitoring
- Individual user details and history

### 6. Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create Render Services:**
   - Web Service (your Flask app)
   - PostgreSQL Database

3. **Configure Environment Variables**
4. **Deploy and Monitor**

### 7. Admin Security in Production

**Important:** Change these defaults before deployment:
- Replace `admin@dengue.com` with your email
- Replace `admin123` with a strong password
- Use environment variables for all secrets

### 8. Monitoring Your App

**Admin Dashboard Features:**
- Real user analytics
- Prediction trends by region
- Database performance metrics
- User activity monitoring

### 9. Free Tier Limitations

**Render Free Tier:**
- App sleeps after 15 minutes of inactivity
- PostgreSQL: 1GB storage, 97 hours/month
- Sufficient for testing and small deployments

### 10. Production Checklist

- [ ] PostgreSQL database created
- [ ] Environment variables configured
- [ ] Admin credentials changed from defaults
- [ ] Build script executable
- [ ] Requirements.txt updated
- [ ] GitHub repository ready
- [ ] Render services configured

## 🔗 Useful Render URLs

- **Dashboard**: https://dashboard.render.com
- **Documentation**: https://render.com/docs
- **PostgreSQL Guide**: https://render.com/docs/databases
