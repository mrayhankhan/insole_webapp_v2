# Deployment Guide for Smart Insole Analytics

This guide shows you how to deploy the full Python webapp (with backend) to various cloud platforms.

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended - Free Tier Available)

1. **Fork/Clone** the repository to your GitHub account
2. **Sign up** at [render.com](https://render.com)
3. **Connect** your GitHub account
4. **Create New Web Service**
5. **Select** your repository
6. **Configure**:
   - Build Command: `pip install -r requirements-deploy.txt`
   - Start Command: `python professional_server.py`
   - Environment: `Python 3`
7. **Deploy** - Your app will be live at `https://your-app-name.onrender.com`

### Option 2: Railway (Easy & Fast)

1. **Visit** [railway.app](https://railway.app)
2. **Sign in** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select** your repository
5. **Add** environment variable: `PORT=8000`
6. **Deploy** automatically starts

### Option 3: Heroku

1. **Install** [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. **Login**: `heroku login`
3. **Create** app: `heroku create your-app-name`
4. **Set** buildpack: `heroku buildpacks:set heroku/python`
5. **Deploy**: `git push heroku main`

### Option 4: DigitalOcean App Platform

1. **Go to** [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. **Create App** → **GitHub**
3. **Select** repository
4. **Configure**:
   - Source Directory: `/`
   - Build Command: `pip install -r requirements-deploy.txt`
   - Run Command: `python professional_server.py`
5. **Launch**

## 🐳 Docker Deployment

If you prefer Docker:

```bash
# Build image
docker build -t smart-insole-analytics .

# Run container
docker run -p 8000:8000 smart-insole-analytics
```

## 🔧 Environment Variables

For production deployment, set these environment variables:

- `PORT`: Port number (default: 8000)
- `ENVIRONMENT`: Set to `production`

## 📝 Notes

- **Bluetooth features** are disabled in cloud deployments (no hardware access)
- **Serial port detection** may be limited on some platforms
- **Simulation mode** works perfectly in all deployments
- **WebSocket connections** are fully supported

## 🌐 What You'll Get

Your deployed webapp will include:

✅ Real-time sensor data simulation
✅ Interactive pressure heatmap
✅ Gait analysis dashboard
✅ WebSocket real-time updates
✅ Professional UI with dark theme
✅ Mobile-responsive design
✅ REST API endpoints

## 🚨 Troubleshooting

**Build Fails?**
- Use `requirements-deploy.txt` instead of `requirements.txt`
- Remove `pybluez` and `pyserial` for cloud deployment

**Port Issues?**
- Ensure your server uses `PORT` environment variable
- Most platforms auto-assign ports

**WebSocket Issues?**
- Enable WebSocket support in platform settings
- Check if platform supports persistent connections

## 💡 Pro Tips

1. **Use requirements-deploy.txt** for cloud deployments
2. **Enable auto-deploy** from main branch
3. **Set up custom domain** after successful deployment
4. **Monitor logs** for any runtime issues

Choose any platform above - they all work great! Render and Railway are the easiest for beginners.
