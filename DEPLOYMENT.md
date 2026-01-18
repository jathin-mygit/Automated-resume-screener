# Deployment Guide

This guide covers various deployment options for the Automated Resume Screener.

## 🚀 Production Deployment Options

### 1. Docker Deployment (Recommended)

#### Using Docker Compose
```bash
# Clone the repository
git clone <repository-url>
cd automated-resume-screener

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Manual Docker Build
```bash
# Build image
docker build -t resume-screener .

# Run container
docker run -d \
  --name resume-screener \
  -p 5000:5000 \
  -e FLASK_CONFIG=production \
  -e SECRET_KEY=your-production-secret-key \
  -v $(pwd)/data:/app/data:ro \
  resume-screener

# Check health
curl http://localhost:5000/health
```

### 2. Cloud Platform Deployment

#### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set FLASK_CONFIG=production
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# Scale
heroku ps:scale web=1
```

#### AWS EC2
```bash
# Launch EC2 instance (Ubuntu 20.04+)
# SSH into instance

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# Clone and deploy
git clone <repository-url>
cd automated-resume-screener
sudo docker-compose up -d

# Configure security group to allow port 5000
```

#### Google Cloud Run
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-screener

# Deploy to Cloud Run
gcloud run deploy resume-screener \
  --image gcr.io/PROJECT-ID/resume-screener \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1
```

### 3. Traditional Server Deployment

#### Using Gunicorn (Linux/Mac)
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn config
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF

# Start with Gunicorn
gunicorn --config gunicorn.conf.py run:app
```

#### Using uWSGI
```bash
# Install uWSGI
pip install uwsgi

# Create uWSGI config
cat > uwsgi.ini << EOF
[uwsgi]
module = run:app
master = true
processes = 4
socket = /tmp/resume-screener.sock
chmod-socket = 666
vacuum = true
die-on-term = true
EOF

# Start with uWSGI
uwsgi --ini uwsgi.ini
```

#### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/resume-screener
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # File upload settings
        client_max_body_size 50M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static files
    location /static {
        alias /path/to/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔧 Environment Configuration

### Environment Variables
```bash
# Required
FLASK_CONFIG=production
SECRET_KEY=your-very-secure-secret-key

# Optional
HOST=0.0.0.0
PORT=5000
MAX_CONTENT_LENGTH=16777216  # 16MB
MAX_RESUMES_PER_BATCH=50

# Database (if implementing persistent storage)
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
```

### Configuration Files
```python
# config.py - Production settings
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Redis for caching
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # File storage
    UPLOAD_FOLDER = '/app/uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

## 📊 Monitoring & Logging

### Health Checks
```bash
# Basic health check
curl -f http://localhost:5000/health

# Detailed health check with monitoring
curl -s http://localhost:5000/health | jq '.'
```

### Logging Configuration
```python
# logging_config.py
import logging
import sys

def setup_logging(app):
    if not app.debug:
        # Production logging
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Resume Screener startup')
```

### Monitoring with Prometheus
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  resume-screener:
    # ... existing config
    
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔒 Security Considerations

### SSL/TLS Configuration
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Security Headers
```python
# In app.py
from flask_talisman import Talisman

def create_app():
    app = Flask(__name__)
    
    # Security headers
    Talisman(app, {
        'force_https': True,
        'strict_transport_security': True,
        'content_security_policy': {
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline'",
            'style-src': "'self' 'unsafe-inline' fonts.googleapis.com",
            'font-src': "'self' fonts.gstatic.com"
        }
    })
    
    return app
```

### Rate Limiting
```python
# Using Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per minute")
def process():
    # ... existing code
```

## 📈 Performance Optimization

### Caching Strategy
```python
# Using Redis for caching
import redis
from functools import wraps

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL'))

def cache_result(timeout=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Database Optimization
```python
# Using PostgreSQL for persistent storage
from flask_sqlalchemy import SQLAlchemy

class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), index=True)
    filename = db.Column(db.String(255))
    skills = db.Column(db.JSON)
    scores = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_session_created', 'session_id', 'created_at'),
    )
```

### Background Processing
```python
# Using Celery for async processing
from celery import Celery

celery = Celery('resume_screener')
celery.config_from_object('celeryconfig')

@celery.task
def process_resumes_async(job_text, files_data, hard_skills, nice_skills):
    # Process resumes in background
    results = process_resumes(job_text, files_data, hard_skills, nice_skills)
    return results
```

## 🚨 Troubleshooting

### Common Issues

#### Memory Issues
```bash
# Increase Docker memory limit
docker run --memory=4g resume-screener

# Monitor memory usage
docker stats resume-screener
```

#### File Upload Issues
```bash
# Check nginx client_max_body_size
sudo nano /etc/nginx/sites-available/resume-screener
# Add: client_max_body_size 50M;

# Restart nginx
sudo systemctl restart nginx
```

#### spaCy Model Issues
```bash
# Download model in container
docker exec -it resume-screener python -m spacy download en_core_web_sm

# Or rebuild image with model
```

### Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add request logging
@app.before_request
def log_request_info():
    app.logger.debug('Request: %s %s', request.method, request.url)
    app.logger.debug('Headers: %s', request.headers)
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Set production environment variables
- [ ] Configure secure secret key
- [ ] Test with production data
- [ ] Run security scan
- [ ] Set up monitoring
- [ ] Configure backups

### Post-deployment
- [ ] Verify health endpoint
- [ ] Test file uploads
- [ ] Check SSL certificate
- [ ] Monitor resource usage
- [ ] Set up log rotation
- [ ] Configure alerts

### Maintenance
- [ ] Regular security updates
- [ ] Monitor disk space
- [ ] Review logs for errors
- [ ] Update spaCy models
- [ ] Backup configuration
- [ ] Performance monitoring

---

For additional support, check the main README.md or create an issue in the repository.