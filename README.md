# NuuR - Urban Safety Platform for Ethiopian Cities




## Overview

NuuR is a comprehensive web-based safety platform designed for Ethiopian urban environments,that can't get urbans technology providing three core safety features:

1. **Anti-Theft Protection** - SMS-triggered remote tracking and alert system
2. **Path Tracker** - Movement history recording and route replay
3. **Emergency Issue Reporting** - Rapid geo-tagged incident reporting

## Technology Stack

### Frontend
- **React** 18+ with TypeScript
- **React Router** for navigation
- **Leaflet/Mapbox** for interactive maps
- **i18next** for Amharic/English localization
- **TailwindCSS** for responsive UI
- **PWA** support for mobile-like experience

### Backend
- **FastAPI** (Python 3.9+)
- **PostgreSQL** with PostGIS for geospatial data
- **Redis** for caching and real-time features
- **JWT** for authentication
- **Twilio/Africa's Talking** for SMS gateway
- **SendGrid/AWS SES** for email notifications
- **WebSocket** for real-time updates

### Security
- End-to-end encryption for sensitive data
- HTTPS/TLS enforced
- Rate limiting and CORS protection
- Secure media storage with signed URLs
- GDPR-compliant data handling

## Features

### 1. Anti-Theft Protection

**User Flow:**
1. User registers emergency contacts (phone/email)
2. User sets up custom SMS trigger keyword
3. If phone stolen, trusted contact sends keyword via SMS
4. System activates:
   - Live GPS tracking
   - Discreet audio/video recording
   - Silent alerts to contacts and authorities
   - In-app recovery guidance

**Technical Implementation:**
- SMS webhook listener (Twilio/Africa's Talking)
- Background geolocation tracking
- Media capture API with encryption
- Failsafe alert dispatch system

### 2. Path Tracker

**User Flow:**
1. User starts tracking (walk/commute/taxi ride)
2. App records GPS coordinates with timestamps
3. User can:
   - Save and name routes
   - Replay historical routes on map
   - Share routes with trusted contacts
   - Export route data

**Technical Implementation:**
- Continuous GPS tracking with battery optimization
- Efficient coordinate compression
- Interactive map visualization
- Route comparison and analysis

### 3. Emergency Issue Reporting

**User Flow:**
1. One-tap emergency button on home screen
2. Select incident type (fire, medical, accident, security)
3. Auto-capture location + optional photo/description
4. Instant dispatch to authorities and emergency contacts
5. Real-time status updates

**Technical Implementation:**
- Geo-tagged incident creation
- Multi-channel alert dispatch
- Failsafe redundancy system
- Anonymous reporting option

## Project Structure

```
nuur/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, security, dependencies
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Helper functions
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── features/      # Feature modules
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API clients
│   │   ├── utils/         # Helper functions
│   │   ├── locales/       # i18n translations
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml      # Local development
└── docs/                   # Documentation
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 14+ with PostGIS
- Redis 6+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Set environment variables
cp .env.example .env
# Edit .env with backend API URL

# Start development server
npm start
```

### Docker Setup (Recommended)

```bash
docker-compose up -d
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Anti-Theft
- `POST /api/v1/anti-theft/setup` - Configure anti-theft settings
- `GET /api/v1/anti-theft/contacts` - Get emergency contacts
- `POST /api/v1/anti-theft/contacts` - Add emergency contact
- `DELETE /api/v1/anti-theft/contacts/{id}` - Remove contact
- `POST /api/v1/anti-theft/trigger` - Manual trigger (testing)
- `GET /api/v1/anti-theft/status` - Get current status
- `POST /api/v1/anti-theft/location` - Update location

### Path Tracker
- `POST /api/v1/paths/start` - Start tracking
- `POST /api/v1/paths/stop` - Stop tracking
- `POST /api/v1/paths/{id}/points` - Add location points
- `GET /api/v1/paths` - List user's paths
- `GET /api/v1/paths/{id}` - Get path details
- `PUT /api/v1/paths/{id}` - Update path (name, notes)
- `DELETE /api/v1/paths/{id}` - Delete path
- `POST /api/v1/paths/{id}/share` - Share path with contact

### Emergency Reporting
- `POST /api/v1/emergency/report` - Submit emergency report
- `GET /api/v1/emergency/reports` - Get user's reports
- `GET /api/v1/emergency/reports/{id}` - Get report details
- `PUT /api/v1/emergency/reports/{id}/status` - Update status
- `POST /api/v1/emergency/reports/{id}/media` - Upload media

### User Profile
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update profile
- `GET /api/v1/users/contacts` - Get trusted contacts
- `POST /api/v1/users/contacts` - Add trusted contact

## Security Considerations

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (user, responder, admin)
- Secure password hashing (bcrypt)
- Session management with Redis

### Data Protection
- Encrypted storage for sensitive data (AES-256)
- HTTPS-only in production
- Secure media uploads with virus scanning
- Rate limiting on all endpoints
- CORS protection with whitelist

### Privacy
- User consent for location tracking
- Data retention policies
- Right to deletion (GDPR compliance)
- Anonymous reporting options
- Minimal data collection principle

### Anti-Theft Security
- Encrypted SMS trigger keywords
- Multiple verification steps
- Abuse prevention mechanisms
- Secure media streaming
- Location data encryption in transit

## Localization

The platform supports:
- **English** (en) - Default
- **Amharic** (am) - አማርኛ

All user-facing text is externalized in JSON files under `frontend/src/locales/`.

## Deployment

### Production Checklist
- [ ] Configure production environment variables
- [ ] Set up SSL certificates
- [ ] Configure SMS gateway (Africa's Talking recommended for Ethiopia)
- [ ] Set up email service (SendGrid/AWS SES)
- [ ] Configure media storage (AWS S3/Cloudinary)
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure backup strategy
- [ ] Enable rate limiting
- [ ] Set up CDN for static assets
- [ ] Configure auto-scaling

### Recommended Hosting
- **Backend**: Railway, Render, DigitalOcean
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: Supabase, Railway, DigitalOcean Managed PostgreSQL
- **Media**: AWS S3, Cloudinary

## Ethiopian Context Considerations

1. **SMS Gateway**: Use Africa's Talking for reliable Ethiopian network coverage
2. **Emergency Numbers**: Integrate local emergency services (991, 907, 939)
3. **Languages**: Amharic primary, English secondary
4. **Connectivity**: Offline-first approach with data sync
5. **Mobile-First**: Optimize for mobile browsers (limited smartphone adoption)
6. **Low Bandwidth**: Compress media, lazy load images
7. **Payment**: No payment features as per requirements

## Contributing

See CONTRIBUTING.md for development guidelines.

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions, please use GitHub Issues or contact support@nuur.et

