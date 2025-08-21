# IICE CRM Deployment Guide

## Recommended Free Hosting Platforms

Based on current research, here are the best free hosting options for Django applications:

### 1. Railway (Recommended)
- **Free Tier**: $5 credit per month (usually sufficient for small apps)
- **Pros**: Easy deployment, automatic HTTPS, good performance
- **Cons**: Limited free usage
- **Best for**: Production-ready deployments

### 2. PythonAnywhere
- **Free Tier**: Truly free with limitations
- **Pros**: Beginner-friendly, no credit card required
- **Cons**: Custom domains not available on free tier
- **Best for**: Testing and demonstrations

### 3. Fly.io
- **Free Tier**: $5 credit per month
- **Pros**: Good performance, Docker support
- **Cons**: More complex setup
- **Best for**: Advanced users

## Deployment Steps for Railway

### Prerequisites
1. GitHub account
2. Railway account (sign up at railway.app)
3. Push your code to GitHub repository

### Step 1: Prepare Your Repository
1. Ensure all files are committed to your GitHub repository
2. Make sure the following files are present:
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `railway.json`

### Step 2: Deploy on Railway
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your IICE-CRM repository
6. Railway will automatically detect it's a Django app

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```
DEBUG=False
SECRET_KEY=your-new-secret-key-here
ALLOWED_HOSTS=your-app-name.railway.app
DATABASE_URL=postgresql://... (Railway will provide this)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Step 4: Add PostgreSQL Database
1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set DATABASE_URL

### Step 5: Deploy
1. Railway will automatically deploy your app
2. Wait for deployment to complete
3. Your app will be available at: `https://your-app-name.railway.app`

## Deployment Steps for PythonAnywhere

### Step 1: Create Account
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Sign up for free account

### Step 2: Upload Code
1. Use Git to clone your repository:
   ```bash
   git clone https://github.com/your-username/IICE-CRM.git
   ```

### Step 3: Install Dependencies
```bash
cd IICE-CRM
pip3.10 install --user -r requirements.txt
```

### Step 4: Configure Web App
1. Go to Web tab in PythonAnywhere dashboard
2. Create new web app
3. Choose Django
4. Set source code path: `/home/yourusername/IICE-CRM`
5. Set WSGI file path: `/home/yourusername/IICE-CRM/IICE/wsgi.py`

### Step 5: Configure Database
1. Go to Databases tab
2. Create MySQL database
3. Update settings.py with database credentials

### Step 6: Collect Static Files
```bash
python manage.py collectstatic
python manage.py migrate
```

## Post-Deployment Steps

### 1. Create Superuser
```bash
python manage.py createsuperuser
```

### 2. Test the Application
- Visit your deployed URL
- Test login functionality
- Verify all features work correctly

### 3. Configure Email Settings
- Update email credentials in environment variables
- Test email functionality

## Troubleshooting

### Common Issues
1. **Static files not loading**: Run `python manage.py collectstatic`
2. **Database errors**: Check DATABASE_URL configuration
3. **Email not working**: Verify Gmail app password setup
4. **500 errors**: Check logs in hosting platform dashboard

### Debug Mode
For debugging, temporarily set `DEBUG=True` in environment variables, but remember to set it back to `False` for production.

## Security Notes

1. Never commit sensitive information to GitHub
2. Use environment variables for all secrets
3. Generate a new SECRET_KEY for production
4. Keep DEBUG=False in production
5. Use HTTPS in production (most platforms provide this automatically)

## Support

If you encounter issues during deployment, check:
1. Platform-specific documentation
2. Application logs in the hosting dashboard
3. Django documentation for production deployment