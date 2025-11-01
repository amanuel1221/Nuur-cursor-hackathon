# NuuR Deployment Guide

## Quick Start with Docker

The fastest way to get NuuR running locally is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yourusername/nuur.git
cd nuur

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs

## Local Development Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 14+ with PostGIS extension
- Redis 6+

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Setup Database**
```bash
# Create PostgreSQL database
createdb nuur_db

# Enable PostGIS extension
psql nuur_db -c "CREATE EXTENSION postgis;"

# Run migrations (if using Alembic)
alembic upgrade head
```

5. **Run Development Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with backend API URL
```

3. **Run Development Server**
```bash
npm run dev
```

## Production Deployment

### Option 1: Cloud Platform (Recommended)

#### Backend Deployment (Railway/Render)

1. **Prepare for Deployment**
```bash
cd backend
```

2. **Configure Environment Variables** on your platform:
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=<generate-secure-key>
ENCRYPTION_KEY=<generate-secure-key>
AFRICASTALKING_API_KEY=<your-api-key>
SENDGRID_API_KEY=<your-api-key>
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

3. **Deploy**
- Railway: `railway up`
- Render: Connect GitHub repository and configure build settings

#### Frontend Deployment (Vercel/Netlify)

1. **Build Configuration**
- Build Command: `npm run build`
- Output Directory: `dist`
- Node Version: 18

2. **Environment Variables**
```
VITE_API_URL=https://your-backend-api.com/api/v1
```

3. **Deploy**
- Vercel: `vercel --prod`
- Netlify: `netlify deploy --prod`

### Option 2: VPS Deployment (DigitalOcean/AWS EC2)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nginx postgresql postgresql-contrib postgis redis-server \
  python3-pip python3-venv nodejs npm certbot python3-certbot-nginx

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. Database Setup

```bash
# Create database
sudo -u postgres createdb nuur_db
sudo -u postgres psql -c "CREATE USER nuur_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nuur_db TO nuur_user;"

# Enable PostGIS
sudo -u postgres psql nuur_db -c "CREATE EXTENSION postgis;"
```

#### 3. Backend Deployment

```bash
# Clone repository
cd /var/www
sudo git clone https://github.com/yourusername/nuur.git
cd nuur/backend

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
sudo nano .env  # Add production settings

# Setup systemd service
sudo nano /etc/systemd/system/nuur-backend.service
```

**nuur-backend.service:**
```ini
[Unit]
Description=NuuR Backend API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/nuur/backend
Environment="PATH=/var/www/nuur/backend/venv/bin"
ExecStart=/var/www/nuur/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable nuur-backend
sudo systemctl start nuur-backend
```

#### 4. Frontend Deployment

```bash
cd /var/www/nuur/frontend

# Install dependencies and build
npm install
npm run build

# Files will be in dist/ directory
```

#### 5. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/nuur
```

**Nginx Config:**
```nginx
# Backend API
server {
    listen 80;
    server_name api.nuur.et;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name nuur.et www.nuur.et;

    root /var/www/nuur/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nuur /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d nuur.et -d www.nuur.et -d api.nuur.et
```

### Option 3: Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (advanced deployment).

## Environment Variables Reference

### Backend Required Variables

```bash
# Application
SECRET_KEY=<random-32-char-string>
JWT_SECRET_KEY=<random-32-char-string>
ENCRYPTION_KEY=<random-32-char-string>

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis
REDIS_URL=redis://host:port/db

# SMS (Africa's Talking - Recommended for Ethiopia)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=<your-api-key>
AFRICASTALKING_SENDER_ID=NuuR

# Email (SendGrid)
SENDGRID_API_KEY=<your-api-key>
FROM_EMAIL=noreply@nuur.et

# Storage (AWS S3)
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_S3_BUCKET=nuur-media
AWS_REGION=us-east-1
```

### Frontend Required Variables

```bash
VITE_API_URL=https://api.nuur.et/api/v1
```

## SMS Gateway Setup (Africa's Talking)

1. Create account at https://africastalking.com
2. For Ethiopia, choose Ethiopian phone numbers
3. Get API credentials from dashboard
4. Add to backend `.env`:
```
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring & Logging

### Application Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend
```

### Sentry Integration

1. Create Sentry project
2. Add DSN to `.env`:
```
SENTRY_DSN=https://...@sentry.io/...
```

## Backup Strategy

### Database Backup

```bash
# Automated daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump -U nuur_user nuur_db > /backups/nuur_db_$DATE.sql
find /backups -name "nuur_db_*.sql" -mtime +7 -delete
```

### Media Files Backup

- Use AWS S3 versioning
- Enable automated backups

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple backend instances behind load balancer
- Use managed PostgreSQL (AWS RDS, DigitalOcean Managed DB)
- Use Redis Cluster for caching
- Use CDN for static assets (CloudFlare)

### Performance Optimization

- Enable database connection pooling (pgBouncer)
- Implement Redis caching for frequent queries
- Use database read replicas
- Compress media files before upload
- Enable Gzip compression on Nginx

## Security Checklist

- [ ] Change all default passwords
- [ ] Use HTTPS/SSL certificates
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Database encryption at rest
- [ ] Secure API keys in environment variables
- [ ] Implement request validation
- [ ] Set up automated backups

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Verify database connection
psql $DATABASE_URL

# Check Python dependencies
pip list
```

### Frontend build errors
```bash
# Clear cache
rm -rf node_modules
npm install

# Check Node version
node --version  # Should be 18+
```

### Database connection issues
```bash
# Test PostgreSQL connection
psql -h localhost -U nuur_user -d nuur_db

# Check PostGIS extension
psql nuur_db -c "SELECT PostGIS_version();"
```

## Support

For deployment issues, please open an issue on GitHub or contact support@nuur.et

## License

MIT License - See LICENSE file for details

