# Deployment Guide

## Local Development

### Prerequisites
```bash
# Python 3.8+
python3 --version

# Git
git --version
```

### Setup
```bash
# Clone repository
git clone https://github.com/mrayhankhan/insole_webapp_v2.git
cd insole_webapp_v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Application
```bash
# Start server
python professional_server.py

# Open browser to http://localhost:8000
```

## Production Deployment

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bluetooth \
    libbluetooth-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "professional_server.py"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  insole-webapp:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - /dev:/dev
    privileged: true
    environment:
      - PORT=8000
      - HOST=0.0.0.0
```

#### Build and Run
```bash
docker build -t insole-webapp .
docker run -p 8000:8000 --privileged -v /dev:/dev insole-webapp
```

### Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### DigitalOcean App Platform
1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `python professional_server.py`
4. Configure environment variables

### Environment Variables
```bash
# Production settings
export PORT=8000
export HOST=0.0.0.0
export DEBUG=false

# Optional: Secure WebSocket
export USE_SSL=true
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

## Reverse Proxy Setup

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPreserveHost On
    ProxyRequests Off
    
    ProxyPass /ws ws://localhost:8000/ws
    ProxyPassReverse /ws ws://localhost:8000/ws
    
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
    
    RewriteEngine on
    RewriteCond %{HTTP:UPGRADE} websocket [NC]
    RewriteCond %{HTTP:CONNECTION} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:8000/$1" [P,L]
</VirtualHost>
```

## SSL Configuration

### Let's Encrypt (Certbot)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring

### Health Check Endpoint
The application provides a health check at `/health`:

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "version": "1.0.0"}
```

### Log Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Security Considerations

1. **HTTPS Only**: Use SSL certificates in production
2. **CORS**: Configure appropriate CORS settings
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Validate all user inputs
5. **Device Access**: Limit Bluetooth/Serial permissions
6. **Updates**: Keep dependencies updated

## Performance Optimization

1. **WebSocket Connection Pooling**
2. **Data Compression**: Enable gzip compression
3. **Static File Caching**: Cache CSS/JS files
4. **Database**: Add database for data persistence
5. **CDN**: Use CDN for static assets
