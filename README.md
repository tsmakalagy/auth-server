# Authentication Server

A Flask-based authentication server supporting both phone number (SMS) and email authentication, with Supabase integration and FRP for deployment in China.

## Features

- **Multi-factor Authentication**
  - Phone number verification via SMS
  - Email verification with OTP
  - Support for both Chinese and Madagascar phone numbers

- **Security**
  - JWT-based authentication
  - Rate limiting for login attempts
  - Session management
  - Secure token handling

- **Integrations**
  - Supabase for database and real-time features
  - SMS Gateway (via Raspberry Pi)
  - Email service (SMTP)
  - FRP for deployment in China

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- SMS Gateway running on Raspberry Pi
- Supabase account
- SMTP server access
- FRP server (for China deployment)

## Environment Variables

```env
# Authentication
JWT_SECRET_KEY=your_secure_key

# SMS Gateway
SMS_GATEWAY_URL=http://your_raspberry_pi:5001

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_app_password

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Flask
FLASK_ENV=production
FLASK_APP=app.py
```

## Project Structure

```
app/
├── __init__.py
├── auth_service.py
├── config.py
├── email_service.py
├── routes/
│   ├── email_auth.py
│   └── phone_auth.py
├── session_manager.py
├── token_manager.py
└── utils/
    ├── rate_limiter.py
    └── validators.py
docker/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

### Email Authentication
```
POST /auth/email/register
POST /auth/email/verify
POST /auth/email/login
```

### Phone Authentication
```
POST /auth/phone/register
POST /auth/phone/verify
POST /auth/phone/login
```

### Session Management
```
POST /auth/refresh-token
POST /auth/logout
GET  /auth/sessions
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auth-server.git
cd auth-server
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and start services:
```bash
docker-compose up -d --build
```

## Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment (China)
1. Set up FRP configuration:
```bash
# Copy FRP config
cp frpc.example.ini frpc.ini
# Edit frpc.ini with your settings
```

2. Deploy using Docker Compose:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## Testing

1. Health check:
```bash
curl http://localhost:5000/health
```

2. Test email registration:
```bash
curl -X POST http://localhost:5000/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "name":"Test User"}'
```

## Monitoring

The server includes health checks and logging. Monitor using:
```bash
# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

## Maintenance

### Backup Configuration
Regular backups are handled by Supabase. Additional configuration files should be backed up manually.

### Updates
1. Pull latest changes:
```bash
git pull origin main
```

2. Rebuild and restart services:
```bash
docker-compose down
docker-compose up -d --build
```

## Troubleshooting

Common issues and solutions:

1. SMS Gateway Connection:
   - Check if Raspberry Pi is accessible
   - Verify SMS Gateway service is running

2. FRP Connection:
   - Verify FRP server is running
   - Check network connectivity to OVH VPS

3. Email Service:
   - Verify SMTP credentials
   - Check email service provider settings

## Security Considerations

- Keep environment variables secure
- Regularly update dependencies
- Monitor login attempts
- Review session activities
- Keep Supabase credentials secure

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Support

For issues related to this implementation, please open an issue in the repository.