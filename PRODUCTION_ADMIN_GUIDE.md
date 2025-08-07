# Production Deployment Security Checklist

## 🔒 Security Configuration for Production

### 1. Environment Variables (.env.production)
```
DATABASE_URL=postgresql://username:password@yourserver.postgres.database.azure.com:5432/denguedb
SESSION_SECRET=your-super-secure-random-session-key-here-minimum-32-chars
ADMIN_EMAIL=your-admin-email@yourdomain.com
ADMIN_PASSWORD=your-strong-admin-password-here
FLASK_ENV=production
FLASK_DEBUG=False
```

### 2. Admin Access in Production

**Admin Login URL**: `https://yourapp.azurewebsites.net/login`
**Admin Dashboard**: `https://yourapp.azurewebsites.net/admin`

**As admin, you can access:**
- All user registrations and profiles
- All dengue risk predictions made by users
- User activity logs and statistics
- Database connection information
- Individual user details and prediction history

### 3. Security Best Practices

1. **Change Default Admin Credentials**:
   - Use your own email instead of admin@dengue.com
   - Use a strong password (not admin123)

2. **Database Security**:
   - Use PostgreSQL in production (not SQLite)
   - Enable SSL connections
   - Use strong database passwords

3. **Application Security**:
   - Set strong SECRET_KEY
   - Disable debug mode in production
   - Use HTTPS only

### 4. Admin Features in Production

**User Management**:
- View all registered users
- See user registration dates
- Access user prediction history

**Database Monitoring**:
- Monitor database performance
- View connection statistics
- Check table sizes and data

**Security Monitoring**:
- Track login attempts
- Monitor admin access logs
- View application errors

### 5. Deployment Commands

```bash
# Azure deployment with admin features
az webapp up --name your-dengue-app --resource-group your-rg
```

### 6. Production Admin Workflow

1. Deploy application to Azure
2. Configure environment variables in Azure App Service
3. Initialize database with admin user
4. Access admin interface at your-app-url/admin
5. Monitor users and predictions through admin dashboard

## 🚨 Important Security Notes

- **Never expose admin credentials** in code or public repositories
- **Use environment variables** for all sensitive configuration
- **Enable logging** to monitor admin access
- **Regular security updates** for dependencies
- **Backup database** regularly through admin interface insights
