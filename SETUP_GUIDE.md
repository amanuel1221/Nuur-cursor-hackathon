# NuuR Quick Setup Guide

This guide will help you get NuuR running in 10 minutes.

## Prerequisites

Install these tools:
- Docker & Docker Compose (easiest option)
- OR Node.js 18+, Python 3.9+, PostgreSQL 14+, Redis 6+

## Option 1: Docker Setup (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/nuur.git
cd nuur
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs

### 4. Create Your Account
1. Open http://localhost:3000
2. Click "Get Started"
3. Fill in registration form
4. Start using NuuR!

## Option 2: Manual Setup

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup PostgreSQL database
createdb nuur_db
psql nuur_db -c "CREATE EXTENSION postgis;"

# 5. Configure environment
# Create .env file with:
DATABASE_URL=postgresql://localhost/nuur_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# 6. Run backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# 1. Navigate to frontend (in new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
# Create .env file with:
VITE_API_URL=http://localhost:8000/api/v1

# 4. Run frontend
npm run dev
```

## Testing the Application

### 1. Register a New User
- Navigate to http://localhost:3000
- Click "Get Started"
- Fill in your details:
  - First Name, Last Name
  - Email address
  - Phone number (format: +251912345678)
  - Password (min 8 characters)
- Click "Register"

### 2. Explore the Dashboard
After registration, you'll see:
- Anti-Theft status
- Recent paths
- Recent emergency reports
- Quick action buttons

### 3. Setup Anti-Theft Protection
1. Click "Anti-Theft" in sidebar
2. Configure:
   - Set trigger keyword (min 4 characters)
   - Enable GPS tracking
   - Enable audio/video recording
   - Set tracking interval
3. Add emergency contacts:
   - Contact name
   - Phone number
   - Email (optional)
   - Priority level
4. Save settings

### 4. Path Tracking
1. Click "Path Tracker" in sidebar
2. Click "Start Tracking"
3. Move around (or simulate with test data)
4. Click "Stop Tracking"
5. View saved paths
6. Share paths with contacts

### 5. Emergency Reporting
1. Click "Emergency" in sidebar
2. Click "Report Incident"
3. Select incident type:
   - Fire
   - Medical Emergency
   - Accident
   - Security Threat
   - Other
4. Add description
5. Location is auto-captured
6. Submit report

## API Testing

### Using Swagger UI
Visit http://localhost:8000/api/v1/docs for interactive API documentation.

### Using cURL

**Register User:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "phone_number": "+251912345678",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Get Profile (with token):**
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Language Support

NuuR supports English and Amharic (አማርኛ).

**To Switch Language:**
1. Click the globe icon in the navigation
2. Select your preferred language
3. The interface will update immediately

## Configuration for Ethiopia

### SMS Gateway (Africa's Talking)

1. **Create Account**
   - Visit https://africastalking.com
   - Register with Ethiopian phone number
   - Verify your account

2. **Get API Credentials**
   - Go to Dashboard
   - Navigate to API Keys
   - Copy your API Key and Username

3. **Configure Backend**
   Add to `backend/.env`:
   ```
   SMS_PROVIDER=africastalking
   AFRICASTALKING_USERNAME=your_username
   AFRICASTALKING_API_KEY=your_api_key
   AFRICASTALKING_SENDER_ID=NuuR
   ```

### Email Service (SendGrid)

1. **Create Account**
   - Visit https://sendgrid.com
   - Sign up for free tier

2. **Create API Key**
   - Go to Settings → API Keys
   - Create new API key with full access
   - Copy the key (shown once)

3. **Configure Backend**
   Add to `backend/.env`:
   ```
   EMAIL_PROVIDER=sendgrid
   SENDGRID_API_KEY=your_api_key
   FROM_EMAIL=noreply@yourdomain.com
   FROM_NAME=NuuR Safety Platform
   ```

### Media Storage (AWS S3)

1. **Create AWS Account**
   - Visit https://aws.amazon.com
   - Create account

2. **Create S3 Bucket**
   - Go to S3 service
   - Create bucket (e.g., "nuur-media")
   - Set bucket to private
   - Enable versioning

3. **Create IAM User**
   - Go to IAM
   - Create user with S3 access
   - Save Access Key ID and Secret Key

4. **Configure Backend**
   Add to `backend/.env`:
   ```
   MEDIA_STORAGE=s3
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_S3_BUCKET=nuur-media
   AWS_REGION=us-east-1
   ```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Start Redis
redis-server
```

### Frontend Build Error
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

## Next Steps

1. **Customize Settings**
   - Update `.env` files with your credentials
   - Configure SMS/Email providers
   - Set up media storage

2. **Deploy to Production**
   - See `DEPLOYMENT.md` for production setup
   - Configure domain and SSL certificates
   - Set up monitoring and backups

3. **Invite Users**
   - Share the registration link
   - Set up emergency contacts
   - Test anti-theft triggers

4. **Monitor Usage**
   - Check logs: `docker-compose logs -f`
   - Monitor database size
   - Track API usage

## Support

- **Documentation**: See README.md and TECHNICAL_ARCHITECTURE.md
- **Issues**: GitHub Issues
- **Email**: support@nuur.et

## Security Notes

⚠️ **Important:**
- Change all default passwords
- Use strong SECRET_KEY and JWT_SECRET_KEY
- Never commit `.env` files to git
- Enable HTTPS in production
- Regularly update dependencies
- Set up automated backups

## License

MIT License - See LICENSE file for details.

---

**Happy Coding! Stay Safe with NuuR! 🛡️**

