# District IT Help Desk Ecosystem

A complete, production-ready IT help desk platform designed for school districts. This ecosystem includes a full ITSM help desk system, IT asset management (ITAM), CVE vulnerability monitoring, and a deployable agent for endpoint data collection.

## 🎯 Features

### Help Desk Platform
- **Ticket Management**: Create, track, and resolve support tickets
- **ITSM Workflows**: Predefined categories, statuses, and priorities
- **SLA Tracking**: Automatic SLA calculation and breach detection
- **Ticket Comments**: Internal notes and public replies
- **Email Notifications**: Automated email updates (Gmail, Office 365, custom SMTP)
- **Google Chat Integration**: Two-way notifications to Google Chat spaces

### IT Asset Management (ITAM)
- **Asset Inventory**: Track hardware and software across all endpoints
- **Automatic Discovery**: Deployable agent collects system information
- **Software Tracking**: Installed applications and versions
- **Update Management**: Monitor pending Windows updates

### Cybersecurity & CVE Monitoring
- **CVE Detection**: Automatic vulnerability scanning against NVD database
- **Risk Assessment**: CVSS scoring and severity classification
- **Acknowledgment Tracking**: Mark vulnerabilities as reviewed
- **Scheduled Scanning**: Weekly CVE checks (configurable)

### Reporting & Analytics
- **Dashboard**: Real-time metrics and KPIs
- **Standard Reports**: Pre-built ticket, asset, and CVE reports
- **Custom Reports**: Drag-and-drop report builder
- **Export Capabilities**: Generate and share reports

### User Management
- **Role-Based Access**: Admin, Technician, End User roles
- **Department Tracking**: Organize users and assets by department
- **Audit Trail**: Track all changes and actions

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (3000)                 │
│              Dashboard • Tickets • Assets • Reports       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend (8000)                  │
│  Tickets • Assets • Users • SLA • Email • Google Chat    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database (5432)                  │
│         Tickets • Assets • Users • CVE Alerts            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│         Deployable Agent (Windows/Linux/macOS)           │
│    ITAM Collection • CVE Monitoring • Ticket Creation    │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB RAM, 10GB disk space

### Deploy in 5 Minutes

```bash
# 1. Clone the repository
git clone <repository-url>
cd it_helpdesk_ecosystem

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Start services
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Default login: admin / password
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📦 Project Structure

```
it_helpdesk_ecosystem/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── utils/               # Utilities
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   └── database.py          # Database setup
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                     # React SPA
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client
│   │   ├── stores/              # Zustand stores
│   │   ├── styles/              # Tailwind CSS
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── agent/                        # Deployable agent
│   ├── agent.py                 # Main agent code
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml           # Orchestration
├── .env.example                 # Environment template
├── README.md                    # This file
└── DEPLOYMENT.md                # Deployment guide
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | - | JWT secret key (generate random) |
| `AGENT_API_KEY` | - | API key for agents |
| `DATABASE_URL` | `postgresql://...` | Database connection string |
| `SMTP_ENABLED` | `False` | Enable email notifications |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `GOOGLE_CHAT_ENABLED` | `False` | Enable Google Chat |
| `CVE_CHECK_INTERVAL_HOURS` | `168` | CVE scan frequency (hours) |

See [.env.example](.env.example) for all options.

## 🔐 Security

### Default Credentials

⚠️ **MUST be changed in production!**

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `password` |

### Security Recommendations

1. Change all default credentials
2. Use HTTPS/TLS in production
3. Keep Docker images updated
4. Regular database backups
5. Use strong API keys
6. Restrict network access
7. Enable SMTP authentication
8. Rotate secrets regularly

## 📊 API Endpoints

### Authentication
- `POST /api/auth/token` - Login
- `GET /api/auth/me` - Get current user

### Tickets
- `GET /api/tickets` - List tickets
- `POST /api/tickets` - Create ticket
- `GET /api/tickets/{id}` - Get ticket details
- `PUT /api/tickets/{id}` - Update ticket
- `POST /api/tickets/{id}/comments` - Add comment

### Assets
- `GET /api/assets` - List assets
- `GET /api/assets/{id}` - Get asset details
- `GET /api/assets/{id}/cves` - Get CVE alerts

### Reports
- `GET /api/reports/dashboard` - Dashboard stats
- `GET /api/reports/tickets/by-status` - Ticket breakdown
- `GET /api/reports/cves/by-severity` - CVE breakdown

See http://localhost:8000/docs for full API documentation.

## 🤖 Deploying the Agent

### Windows Endpoint

```bash
# 1. Install Python 3.11+
# 2. Download agent files
# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env
HELPDESK_API_URL=http://your-server:8000/api
AGENT_API_KEY=your-api-key
ASSET_TAG=ASSET-001

# 5. Run agent
python agent.py

# 6. (Optional) Install as Windows service
python -m win32serviceutil.InstallService -serviceName "HelpdeskAgent" ...
```

See [agent/README.md](agent/README.md) for detailed instructions.

## 📈 Monitoring

### Dashboard Metrics
- Open/In-Progress/Resolved tickets
- SLA compliance
- CVE alerts by severity
- Asset inventory status
- Update status

### Reporting
- Ticket resolution time
- SLA breach analysis
- CVE vulnerability trends
- Asset distribution by type/department

## 🔄 Scheduled Tasks

- **CVE Scanning**: Weekly (configurable)
- **SLA Monitoring**: Continuous
- **Agent Reporting**: Daily (configurable)
- **Email Notifications**: Real-time

## 🛠️ Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Agent Development

```bash
cd agent
pip install -r requirements.txt
python agent.py
```

## 📝 Database Schema

### Core Tables
- `users` - User accounts and roles
- `tickets` - Support tickets
- `ticket_comments` - Ticket replies and notes
- `ticket_history` - Change tracking
- `slas` - SLA definitions

### ITAM Tables
- `assets` - Managed devices
- `installed_software` - Software inventory
- `update_status` - Pending updates

### Security Tables
- `cve_alerts` - Vulnerability alerts

## 🐛 Troubleshooting

### Services Won't Start
```bash
docker-compose logs
docker-compose build --no-cache
```

### Database Connection Error
```bash
docker-compose exec db psql -U helpdesk -l
```

### Agent Can't Connect
```bash
# Check API URL and API key
# Verify firewall rules
docker-compose logs backend | grep agent
```

See [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) for more solutions.

## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [agent/README.md](agent/README.md) - Agent documentation
- [API Docs](http://localhost:8000/docs) - Interactive API documentation

## 🤝 Support

For issues, questions, or feature requests:
1. Check the documentation
2. Review logs: `docker-compose logs`
3. Check the API documentation: http://localhost:8000/docs
4. Contact your IT department

## 📄 License

This project is provided as-is for school district IT departments.

## 🎓 For School Districts

This ecosystem is specifically designed for school district IT operations:
- Handles typical school IT workloads (hardware, software, network)
- Supports multiple departments and locations
- Scales from small to large districts
- Integrates with common school systems
- Provides compliance tracking and reporting

## 🚀 Next Steps

1. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Configure**: Set up SMTP and Google Chat
3. **Deploy Agents**: Install on Windows endpoints
4. **Train Users**: Show staff how to submit tickets
5. **Monitor**: Check dashboards and reports regularly

---

**Built for school districts. By IT professionals.**
