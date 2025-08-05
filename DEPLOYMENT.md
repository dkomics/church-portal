# 🚀 Church Portal Deployment Guide for Render

This guide will help you deploy your Church Membership Portal to Render with PostgreSQL database.

## 📋 Prerequisites

1. **Render Account**: Ensure you have an active Render subscription
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Domain (Optional)**: Custom domain if you want to use your own URL

## 🔧 Deployment Steps

### Step 1: Prepare Your Repository

1. **Push all changes to GitHub:**
   ```bash
   git add .
   git commit -m "feat: Prepare for Render deployment with production configuration"
   git push origin main
   ```

### Step 2: Create PostgreSQL Database on Render

1. Go to your [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure your database:
   - **Name**: `church-portal-db`
   - **Database**: `church_portal`
   - **User**: `church_admin`
   - **Region**: Choose closest to your users
   - **Plan**: Starter ($7/month) or higher
4. Click **"Create Database"**
5. **Save the Database URL** - you'll need this for the web service

### Step 3: Create Web Service on Render

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the web service:
   - **Name**: `church-portal` or `jbfm-arusha`
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn church_portal.wsgi:application`
   - **Plan**: Starter ($7/month) or higher

### Step 4: Configure Environment Variables

In your Render web service settings, add these environment variables:

#### Required Variables:
```
DJANGO_SECRET_KEY=<generate-a-strong-secret-key>
DEBUG=False
DATABASE_URL=<your-postgresql-database-url-from-step-2>
```

#### Optional Variables:
```
SENTRY_DSN=<your-sentry-dsn-for-error-monitoring>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<your-app-password>
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Run the build script (`./build.sh`)
   - Install dependencies
   - Collect static files
   - Run database migrations
   - Create the admin user
   - Start the application with Gunicorn

### Step 6: Access Your Application

1. **Your app will be available at**: `https://your-service-name.onrender.com`
2. **Admin Login**:
   - URL: `https://your-service-name.onrender.com/auth/login/`
   - Username: `admin`
   - Password: `ChurchAdmin2024!`

## 🔐 Post-Deployment Security

### 1. Change Default Admin Password
```bash
# Access your app's shell via Render dashboard
python manage.py shell
```
```python
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
admin.set_password('YourNewSecurePassword123!')
admin.save()
```

### 2. Create Additional Users
- Login as admin
- Go to: `https://your-app.onrender.com/auth/admin-dashboard/`
- Use "User Management" to create accounts for church staff

### 3. Configure Custom Domain (Optional)
1. In Render dashboard, go to your web service
2. Click **"Settings"** → **"Custom Domains"**
3. Add your domain (e.g., `portal.yourchurch.org`)
4. Update DNS records as instructed by Render

## 📊 Monitoring & Maintenance

### Application Monitoring
- **Logs**: Available in Render dashboard under "Logs" tab
- **Metrics**: Monitor performance in Render dashboard
- **Sentry**: Add Sentry DSN for error tracking

### Database Backups
- Render automatically backs up PostgreSQL databases
- Manual backups available in database dashboard

### Updates & Maintenance
```bash
# To deploy updates:
git add .
git commit -m "Update: description of changes"
git push origin main
# Render will automatically redeploy
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check build logs in Render dashboard
   - Ensure `build.sh` is executable: `chmod +x build.sh`

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` environment variable
   - Check PostgreSQL service status

3. **Static Files Not Loading**:
   - Ensure `whitenoise` is in requirements.txt
   - Check `STATIC_ROOT` and `STATICFILES_DIRS` settings

4. **Admin Login Issues**:
   - Check if superuser was created in build logs
   - Reset password via Django shell if needed

### Support Resources:
- **Render Documentation**: https://render.com/docs
- **Django Documentation**: https://docs.djangoproject.com/
- **Project Repository**: Your GitHub repository

## 🎉 Success!

Your Church Membership Portal is now live and secure! 

### Key Features Available:
- ✅ Secure authentication system
- ✅ Role-based access control
- ✅ Member registration and directory
- ✅ Admin dashboard and user management
- ✅ Professional church branding
- ✅ Mobile-responsive design
- ✅ Production-ready security settings

### Next Steps:
1. Change default admin password
2. Create user accounts for church staff
3. Add real member data
4. Configure email settings for notifications
5. Set up regular backups and monitoring

**Congratulations on your professional church management system!** 🎊
