# NuuR Technical Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  React PWA (Mobile & Desktop Browsers)                          │
│  - Anti-Theft Dashboard                                          │
│  - Path Tracker Interface                                        │
│  - Emergency Reporting                                           │
│  - User Profile & Settings                                       │
└───────────────────┬─────────────────────────────────────────────┘
                    │ HTTPS/WSS
┌───────────────────┴─────────────────────────────────────────────┐
│                     API Gateway Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Application Server                                      │
│  - REST API Endpoints                                            │
│  - WebSocket Connections                                         │
│  - JWT Authentication                                            │
│  - Rate Limiting & CORS                                          │
└───────────┬────────────┬────────────┬─────────────┬─────────────┘
            │            │            │             │
┌───────────┴───┐ ┌──────┴──────┐ ┌──┴──────┐ ┌────┴──────────┐
│ Service Layer │ │   Cache     │ │  Queue  │ │  External     │
├───────────────┤ ├─────────────┤ ├─────────┤ │  Services     │
│ Anti-Theft    │ │   Redis     │ │ Celery  │ ├───────────────┤
│ Path Tracker  │ │             │ │         │ │ SMS Gateway   │
│ Emergency     │ │ - Sessions  │ │ - Async │ │ Email Service │
│ Notification  │ │ - Rate Limit│ │ - Jobs  │ │ Media Storage │
│ Geo Services  │ │ - Real-time │ │ - Alerts│ │ Maps API      │
└───────┬───────┘ └─────────────┘ └─────────┘ └───────────────┘
        │
┌───────┴──────────────────────────────────────────────────────┐
│                     Data Layer                                │
├──────────────────────────────────────────────────────────────┤
│  PostgreSQL + PostGIS                                         │
│  - Users & Authentication                                     │
│  - Anti-Theft Configurations                                  │
│  - Emergency Contacts                                         │
│  - Path Tracking Data (geo-indexed)                          │
│  - Emergency Reports                                          │
│  - Audit Logs                                                 │
└──────────────────────────────────────────────────────────────┘
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    preferred_language VARCHAR(5) DEFAULT 'en',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
```

### Emergency Contacts Table
```sql
CREATE TABLE emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    contact_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    relationship VARCHAR(50),
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emergency_contacts_user ON emergency_contacts(user_id);
```

### Anti-Theft Configuration Table
```sql
CREATE TABLE anti_theft_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    trigger_keyword_hash VARCHAR(255) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    enable_gps_tracking BOOLEAN DEFAULT TRUE,
    enable_audio_recording BOOLEAN DEFAULT TRUE,
    enable_video_recording BOOLEAN DEFAULT FALSE,
    tracking_interval_seconds INTEGER DEFAULT 30,
    recording_duration_minutes INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Anti-Theft Events Table
```sql
CREATE TABLE anti_theft_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    triggered_by VARCHAR(20),
    trigger_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    is_test BOOLEAN DEFAULT FALSE,
    deactivated_at TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_anti_theft_events_user ON anti_theft_events(user_id);
CREATE INDEX idx_anti_theft_events_status ON anti_theft_events(status);
```

### Location Tracking Table
```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE location_tracking (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID REFERENCES anti_theft_events(id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    accuracy FLOAT,
    altitude FLOAT,
    speed FLOAT,
    heading FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    battery_level INTEGER
);

CREATE INDEX idx_location_tracking_event ON location_tracking(event_id);
CREATE INDEX idx_location_tracking_timestamp ON location_tracking(timestamp);
CREATE INDEX idx_location_tracking_geom ON location_tracking USING GIST(location);
```

### Media Recordings Table
```sql
CREATE TABLE media_recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES anti_theft_events(id) ON DELETE CASCADE,
    media_type VARCHAR(10) CHECK (media_type IN ('audio', 'video', 'photo')),
    file_url VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    duration_seconds INTEGER,
    encryption_key_id VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_media_recordings_event ON media_recordings(event_id);
```

### Paths Table
```sql
CREATE TABLE paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200),
    description TEXT,
    path_type VARCHAR(20) CHECK (path_type IN ('walk', 'commute', 'taxi', 'other')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    total_distance_meters FLOAT,
    average_speed_mps FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_paths_user ON paths(user_id);
CREATE INDEX idx_paths_start_time ON paths(start_time);
```

### Path Points Table
```sql
CREATE TABLE path_points (
    id BIGSERIAL PRIMARY KEY,
    path_id UUID REFERENCES paths(id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    accuracy FLOAT,
    altitude FLOAT,
    speed FLOAT,
    heading FLOAT,
    timestamp TIMESTAMP NOT NULL
);

CREATE INDEX idx_path_points_path ON path_points(path_id);
CREATE INDEX idx_path_points_timestamp ON path_points(timestamp);
CREATE INDEX idx_path_points_geom ON path_points USING GIST(location);
```

### Shared Paths Table
```sql
CREATE TABLE shared_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id UUID REFERENCES paths(id) ON DELETE CASCADE,
    shared_with_email VARCHAR(255),
    shared_with_phone VARCHAR(20),
    share_token VARCHAR(100) UNIQUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shared_paths_token ON shared_paths(share_token);
```

### Emergency Reports Table
```sql
CREATE TABLE emergency_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    report_type VARCHAR(20) CHECK (report_type IN ('fire', 'medical', 'accident', 'security', 'other')),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    address_text TEXT,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'responding', 'resolved', 'cancelled')),
    is_anonymous BOOLEAN DEFAULT FALSE,
    severity VARCHAR(10) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emergency_reports_user ON emergency_reports(user_id);
CREATE INDEX idx_emergency_reports_type ON emergency_reports(report_type);
CREATE INDEX idx_emergency_reports_status ON emergency_reports(status);
CREATE INDEX idx_emergency_reports_geom ON emergency_reports USING GIST(location);
```

### Emergency Report Media Table
```sql
CREATE TABLE emergency_report_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES emergency_reports(id) ON DELETE CASCADE,
    media_type VARCHAR(10) CHECK (media_type IN ('photo', 'video', 'audio')),
    file_url VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emergency_report_media_report ON emergency_report_media(report_id);
```

## API Architecture

### Authentication Flow

```
1. User Registration/Login
   ├─> POST /api/v1/auth/register
   │   └─> Create user, send verification SMS/email
   │
   ├─> POST /api/v1/auth/verify
   │   └─> Verify code, activate account
   │
   └─> POST /api/v1/auth/login
       └─> Return JWT access + refresh tokens

2. Protected Requests
   ├─> Include "Authorization: Bearer {access_token}"
   │
   ├─> Middleware validates JWT
   │   ├─> Check signature
   │   ├─> Verify expiration
   │   └─> Load user context
   │
   └─> If expired:
       └─> POST /api/v1/auth/refresh
           └─> Return new access token
```

### Anti-Theft Trigger Flow

```
1. SMS Received at Gateway
   │
   ├─> POST /api/v1/webhooks/sms
   │   ├─> Parse sender, message
   │   ├─> Extract keyword
   │   └─> Validate user + keyword hash
   │
2. If Valid Trigger
   │
   ├─> Create anti_theft_event
   │
   ├─> Send Immediate Alerts
   │   ├─> SMS to emergency contacts
   │   ├─> Email to emergency contacts
   │   ├─> Push notification to user
   │   └─> Alert authorities (if configured)
   │
   ├─> Start GPS Tracking
   │   └─> WebSocket connection to device
   │       └─> Receive location updates every N seconds
   │           └─> Store in location_tracking table
   │
   ├─> Activate Media Recording (if enabled)
   │   ├─> Request audio stream from device
   │   ├─> Request video stream (optional)
   │   └─> Store encrypted media files
   │
   └─> Real-time Dashboard Update
       └─> WebSocket broadcast to emergency contacts
```

### Path Tracking Flow

```
1. Start Tracking
   │
   ├─> POST /api/v1/paths/start
   │   └─> Create path record (is_active = true)
   │
2. Continuous Location Updates
   │
   ├─> POST /api/v1/paths/{id}/points (batch)
   │   ├─> Validate path ownership
   │   ├─> Insert multiple path_points
   │   └─> Calculate distance/speed metrics
   │
3. Stop Tracking
   │
   └─> POST /api/v1/paths/{id}/stop
       ├─> Set is_active = false
       ├─> Set end_time
       ├─> Calculate final statistics
       └─> Return complete path data
```

### Emergency Reporting Flow

```
1. Submit Report
   │
   ├─> POST /api/v1/emergency/report
   │   ├─> Capture current location
   │   ├─> Select incident type
   │   ├─> Optional: photo/description
   │   └─> Create emergency_report
   │
2. Multi-Channel Dispatch
   │
   ├─> SMS to local emergency services
   ├─> API call to emergency response system
   ├─> Email to emergency contacts
   ├─> Push notification to nearby users (future)
   │
3. Failsafe Mechanisms
   │
   ├─> If API fails:
   │   ├─> Queue in localStorage
   │   └─> Retry with exponential backoff
   │
   ├─> If network unavailable:
   │   └─> Store locally, sync when online
   │
   └─> Multiple dispatch channels ensure delivery
```

## Security Architecture

### Data Encryption

```
1. In Transit
   ├─> All API calls over HTTPS (TLS 1.3)
   ├─> WebSocket over WSS
   └─> Certificate pinning on mobile

2. At Rest
   ├─> Database encryption (PostgreSQL pgcrypto)
   ├─> Sensitive fields encrypted with AES-256
   │   ├─> SMS trigger keywords
   │   ├─> Location data
   │   └─> Media files
   │
   └─> Encryption keys managed separately
       └─> AWS KMS / HashiCorp Vault

3. Media Files
   ├─> Server-side encryption (SSE)
   ├─> Client-side encryption before upload (optional)
   ├─> Signed URLs with expiration
   └─> Automatic deletion after retention period
```

### Authentication & Authorization

```
JWT Token Structure:
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "unique_token_id"
}

Token Lifecycle:
├─> Access Token: 15 minutes
├─> Refresh Token: 7 days
└─> Stored in httpOnly cookies (web) or secure storage (mobile)

Role-Based Access:
├─> user: Standard features
├─> responder: Access emergency reports
└─> admin: Full system access
```

### Rate Limiting

```
Rate Limits by Endpoint:
├─> /auth/login: 5 req/min per IP
├─> /auth/register: 3 req/hour per IP
├─> /emergency/report: 10 req/hour per user
├─> /paths/*/points: 120 req/min per user
└─> Default: 100 req/min per user

Implementation: Redis with token bucket algorithm
```

## Real-Time Features

### WebSocket Architecture

```
Connection Types:

1. Anti-Theft Tracking Channel
   ├─> ws://api/v1/ws/anti-theft/{event_id}
   │   ├─> Real-time location updates
   │   ├─> Media recording status
   │   └─> Event status changes
   │
2. Path Tracking Channel
   ├─> ws://api/v1/ws/path/{path_id}
   │   ├─> Live path updates
   │   └─> Distance/speed metrics
   │
3. Emergency Dashboard Channel
   └─> ws://api/v1/ws/emergency
       ├─> New incident alerts
       └─> Status updates

Message Format:
{
  "type": "location_update",
  "timestamp": "2025-11-01T12:00:00Z",
  "data": {
    "lat": 9.0320,
    "lon": 38.7469,
    "accuracy": 10
  }
}
```

## Geospatial Features

### PostGIS Functions Used

```sql
-- Distance calculation (meters)
SELECT ST_Distance(
  ST_GeogFromText('POINT(38.7469 9.0320)'),
  location
) FROM emergency_reports;

-- Nearby incidents (within 1km)
SELECT * FROM emergency_reports
WHERE ST_DWithin(
  location,
  ST_GeogFromText('POINT(38.7469 9.0320)'),
  1000
);

-- Path length calculation
SELECT ST_Length(
  ST_MakeLine(location::geometry ORDER BY timestamp)
) FROM path_points
WHERE path_id = '...';

-- Bounding box query
SELECT * FROM paths
WHERE ST_Within(
  location,
  ST_MakeEnvelope(38.7, 9.0, 38.8, 9.1, 4326)
);
```

## Performance Optimization

### Caching Strategy

```
Redis Cache Layers:

1. Session Data
   ├─> Key: session:{user_id}
   └─> TTL: 7 days

2. User Profile
   ├─> Key: user:{user_id}
   └─> TTL: 1 hour

3. Anti-Theft Status
   ├─> Key: anti-theft:status:{user_id}
   └─> TTL: 5 minutes

4. Path Summary
   ├─> Key: path:summary:{path_id}
   └─> TTL: 15 minutes

5. Rate Limiting
   ├─> Key: rate:{endpoint}:{user_id}
   └─> TTL: 1 minute
```

### Database Optimization

```
1. Indexing Strategy
   ├─> B-tree indexes on frequently queried columns
   ├─> GiST indexes for geospatial queries
   └─> Partial indexes for filtered queries

2. Query Optimization
   ├─> Use EXPLAIN ANALYZE for slow queries
   ├─> Batch inserts for location points
   └─> Pagination for large result sets

3. Connection Pooling
   ├─> pgBouncer for connection management
   └─> Pool size: 20-50 connections

4. Partitioning
   └─> Time-based partitioning for path_points
       (monthly partitions for historical data)
```

## Monitoring & Observability

### Metrics to Track

```
Application Metrics:
├─> Request rate (req/s)
├─> Response time (p50, p95, p99)
├─> Error rate (5xx, 4xx)
├─> Active WebSocket connections
└─> Queue depth (Celery)

Business Metrics:
├─> Active users (DAU, MAU)
├─> Anti-theft triggers per day
├─> Emergency reports per day
├─> Path tracking sessions
└─> Average response time to emergencies

Infrastructure Metrics:
├─> CPU/Memory utilization
├─> Database connections
├─> Cache hit rate
├─> Disk I/O
└─> Network throughput
```

### Logging Strategy

```
Log Levels:
├─> DEBUG: Development only
├─> INFO: General application flow
├─> WARNING: Deprecated features, unusual behavior
├─> ERROR: Handled errors
└─> CRITICAL: System failures

Structured Logging Format (JSON):
{
  "timestamp": "2025-11-01T12:00:00Z",
  "level": "INFO",
  "service": "api",
  "user_id": "...",
  "request_id": "...",
  "message": "Anti-theft triggered",
  "context": {...}
}

Tools: Sentry (errors), Datadog/ELK (logs)
```

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────┐
│         CDN (Cloudflare)                    │
│         - Static assets                     │
│         - DDoS protection                   │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│      Load Balancer (Nginx)                  │
│      - SSL termination                      │
│      - Rate limiting                        │
└────┬─────────────────────┬──────────────────┘
     │                     │
┌────┴──────────┐   ┌──────┴──────────┐
│  API Server 1 │   │  API Server 2   │
│  (FastAPI)    │   │  (FastAPI)      │
└────┬──────────┘   └──────┬──────────┘
     │                     │
     └──────────┬──────────┘
                │
┌───────────────┴───────────────────────┐
│  Database Cluster                     │
│  - PostgreSQL Primary                 │
│  - PostgreSQL Replicas (read)         │
│  - PostGIS Extension                  │
└───────────────────────────────────────┘

Auxiliary Services:
├─> Redis Cluster (caching)
├─> Celery Workers (async tasks)
├─> S3/Cloudinary (media storage)
├─> Africa's Talking (SMS)
└─> SendGrid (email)
```

### Scalability Considerations

```
Horizontal Scaling:
├─> Stateless API servers (add more instances)
├─> Database read replicas
└─> Redis cluster mode

Vertical Scaling:
├─> Increase server resources for DB
└─> Optimize queries before scaling

Auto-Scaling Rules:
├─> Scale up: CPU > 70% for 5 minutes
├─> Scale down: CPU < 30% for 10 minutes
└─> Min instances: 2, Max instances: 10
```

This architecture provides a robust, scalable, and secure foundation for the NuuR platform.

