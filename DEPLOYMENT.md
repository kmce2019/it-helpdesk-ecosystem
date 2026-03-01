# District IT Help Desk - Deployment Guide

This guide covers deploying the complete IT Help Desk ecosystem using Docker Compose.

## Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** (for cloning the repository)
- At least 4GB RAM and 10GB disk space

## Quick Start

### 1. Clone or Download the Project

```bash
cd /path/to/it_helpdesk_ecosystem
```

### 2. Configure Environment Variables

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY`: Generate a random secret key
- `AGENT_API_KEY`: Generate a random API key for agents
- SMTP settings (if you want email notifications)
- Google Chat webhook URL (if you want Google Chat integration)

### 3. Start the Services

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL Database** (port 5432)
- **FastAPI Backend** (port 8000)
- **React Frontend** (port 3000)

### 4. Initialize the Database

The database tables are created automatically on first run. To verify:

```bash
docker-compose logs backend | grep "CREATE TABLE"
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Default Login

Use these credentials to log in:

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `password` |

**⚠️ Change these credentials immediately in production!**

## Configuration

### SMTP Email Setup (Gmail Example)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Update `.env`:
   ```
   SMTP_ENABLED=True
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM_EMAIL=helpdesk@district.edu
   ```
4. Restart the backend:
   ```bash
   docker-compose restart backend
   ```

### Google Chat Integration

1. Create a Google Chat space for notifications
2. Set up a webhook: https://developers.google.com/chat/how-tos/webhooks
3. Update `.env`:
   ```
   GOOGLE_CHAT_ENABLED=True
   GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/...
   ```
4. Restart the backend

### CVE Monitoring

The system checks for CVEs weekly by default. To change:

```env
CVE_CHECK_INTERVAL_HOURS=168  # Change to desired interval
```

For faster CVE checks during testing, set to `1` (hourly).

## Deploying the Agent

### Windows Endpoint

1. **Install Python 3.11+**
2. **Download agent files** from the `agent/` directory
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure `.env`**:
   ```
   HELPDESK_API_URL=http://your-helpdesk-server:8000/api
   AGENT_API_KEY=your-agent-api-key
   ASSET_TAG=ASSET-001
   ```
5. **Run the agent**:
   ```bash
   python agent.py
   ```

### Docker (Testing)

To run the agent in Docker:

```bash
docker-compose --profile agent up -d agent
```

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Database Backup

```bash
docker-compose exec db pg_dump -U helpdesk helpdesk_db > backup.sql
```

### Database Restore

```bash
docker-compose exec -T db psql -U helpdesk helpdesk_db < backup.sql
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Data

```bash
docker-compose down -v
```

## Production Deployment

### Security Considerations

1. **Change all default credentials**
   - Admin password
   - Database password
   - API keys

2. **Use HTTPS**
   - Set up SSL/TLS certificates
   - Use a reverse proxy (Nginx, Traefik)
   - Update `FRONTEND_URL` to use `https://`

3. **Secure Environment Variables**
   - Use Docker secrets or a secrets management system
   - Never commit `.env` to version control
   - Rotate keys regularly

4. **Network Security**
   - Use a firewall to restrict access
   - Only expose ports 80/443 (HTTP/HTTPS)
   - Keep the database on an internal network

5. **Backup Strategy**
   - Regular database backups
   - Test restore procedures
   - Store backups securely

### Scaling

For larger deployments:

1. **Separate Database Server**
   - Use a managed database service (RDS, Cloud SQL)
   - Update `DATABASE_URL` in `.env`

2. **Multiple Backend Instances**
   - Use a load balancer (Nginx, HAProxy)
   - Scale horizontally with `docker-compose up --scale backend=3`

3. **Separate Frontend Hosting**
   - Deploy frontend to a CDN or static hosting
   - Update `FRONTEND_URL` and `VITE_API_URL`

4. **Caching Layer**
   - Add Redis for session caching
   - Implement rate limiting

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Verify ports are available
netstat -an | grep 3000
netstat -an | grep 8000
netstat -an | grep 5432

# Rebuild images
docker-compose build --no-cache
```

### Database Connection Errors

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify database exists
docker-compose exec db psql -U helpdesk -l
```

### Agent Can't Connect

```bash
# Verify API URL is correct
# Check firewall allows outbound connections
# Verify AGENT_API_KEY matches backend configuration
# Check backend logs for authentication errors
docker-compose logs backend | grep -i agent
```

### CVE Checks Not Running

```bash
# Check backend logs
docker-compose logs backend | grep -i cve

# Verify NVD API is accessible
# Check CVE_CHECK_INTERVAL_HOURS is set correctly
```

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Frontend Issues**: Check browser console (F12)
- **Backend Issues**: Check `docker-compose logs backend`
- **Database Issues**: Check `docker-compose logs db`

## Updating

To update to a newer version:

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

## Uninstalling

To completely remove the installation:

```bash
# Stop and remove all containers
docker-compose down -v

# Remove images (optional)
docker rmi it_helpdesk_ecosystem-backend
docker rmi it_helpdesk_ecosystem-frontend
docker rmi it_helpdesk_ecosystem-agent
```
