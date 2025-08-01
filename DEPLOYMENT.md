# Deployment Guide for Mimesis

## 🚀 **Recommended Deployment Platforms**

### **Option 1: Render (Recommended - Free Tier)**

1. **Prepare Your Repository**:
   - Ensure all code is pushed to GitHub
   - `.env` file should NOT be in the repository (it's in .gitignore)
   - Make sure `requirements.txt` and `Procfile` are present

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `mimesis-app` (or your preferred name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn main:app`
     - **Plan**: Free (or paid for more resources)

3. **Add Environment Variables**:
   In the Render dashboard, go to "Environment" tab and add:
   ```
   QLOO_API_KEY=your_qloo_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   SESSION_SECRET=your_secure_session_secret_here
   DATABASE_URL=sqlite:///mimesis.db
   ```

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Your app will be available at: `https://your-app-name.onrender.com`

### **Option 2: Railway (Alternative - Free Tier)**

1. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app) and sign up
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect it's a Python app

2. **Add Environment Variables**:
   In the Railway dashboard, go to "Variables" tab and add the same variables as above.

3. **Deploy**:
   - Railway will automatically deploy your app
   - Your app will be available at the provided URL

### **Option 3: Heroku (Paid)**

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku App**:
   ```bash
   heroku create your-mimesis-app
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set QLOO_API_KEY=your_qloo_api_key
   heroku config:set GEMINI_API_KEY=your_gemini_api_key
   heroku config:set SESSION_SECRET=your_session_secret
   heroku config:set DATABASE_URL=sqlite:///mimesis.db
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🔧 **Required Files for Deployment**

### **1. Procfile** (already exists)
```
web: gunicorn main:app
```

### **2. requirements.txt** (updated)
Contains all Python dependencies without PostgreSQL.

### **3. runtime.txt** (created)
Specifies Python version for deployment platforms.

### **4. .gitignore** (already exists)
Ensures `.env` file is not uploaded to GitHub.

## 🌐 **Environment Variables**

These must be set in your deployment platform's dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `QLOO_API_KEY` | Your Qloo API key for cultural analysis | `CvVdTX4-BEHocC3z1A9VCakIfYFSeSlXtXtY-4SKijo` |
| `GEMINI_API_KEY` | Your Google Gemini API key | `AIzaSyC...` |
| `SESSION_SECRET` | Secret key for Flask sessions | `your-super-secret-key-here` |
| `DATABASE_URL` | Database connection string | `sqlite:///mimesis.db` |

## 📱 **Post-Deployment**

### **1. Test Your App**:
- Visit your deployed URL
- Test the signup/login functionality
- Try generating style recommendations
- Check if all features work correctly

### **2. Monitor Performance**:
- Check the logs in your deployment platform
- Monitor API usage and costs
- Ensure the app is responding quickly

### **3. Set Up Custom Domain** (Optional):
- Most platforms allow custom domain setup
- Configure SSL certificates
- Update DNS settings

## 🚨 **Important Notes**

### **Database Considerations**:
- **SQLite**: Works for small to medium applications
- **For Production**: Consider using PostgreSQL or MySQL for better performance
- **Data Persistence**: SQLite data may be lost on some free tiers when the app restarts

### **API Rate Limits**:
- Monitor your Qloo and Gemini API usage
- Set up alerts for rate limits
- Consider implementing caching for better performance

### **Security**:
- Never commit API keys to GitHub
- Use strong session secrets
- Enable HTTPS in production
- Regularly update dependencies

## 🔍 **Troubleshooting**

### **Common Issues**:

1. **Build Failures**:
   - Check if all dependencies are in `requirements.txt`
   - Ensure Python version is compatible
   - Check build logs for specific errors

2. **Environment Variables**:
   - Verify all required variables are set
   - Check variable names (case-sensitive)
   - Restart the app after adding variables

3. **Database Issues**:
   - Ensure database URL is correct
   - Check if database tables are created
   - Monitor database connection limits

4. **API Errors**:
   - Verify API keys are correct
   - Check API rate limits
   - Monitor API response times

## 📞 **Support**

If you encounter issues:
1. Check the deployment platform's documentation
2. Review the application logs
3. Test locally to isolate issues
4. Contact the platform's support team

---

**Happy Deploying! 🚀** 