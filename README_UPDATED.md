# District IT Help Desk Ecosystem v2.0

A complete, production-ready IT help desk platform designed for school districts. This comprehensive ecosystem includes a full ITSM help desk system, Chromebook device management, vehicle request system, IT asset management (ITAM), CVE vulnerability monitoring, and a fully customizable interface.

## 🎯 What's New in v2.0

- **Chromebook Check-In/Check-Out System** - Complete device lifecycle management for student devices
- **Vehicle Request System** - Fleet management with approval workflows and maintenance tracking
- **Full Branding Engine** - Customize colors, fonts, logos, and CSS
- **Inventory Management** - Track consumables and supplies
- **Knowledge Base** - Self-service article library for end users

## 🎯 Core Features

### Help Desk Platform
- **Ticket Management**: Create, track, and resolve support tickets
- **ITSM Workflows**: Predefined categories, statuses, and priorities
- **SLA Tracking**: Automatic SLA calculation and breach detection
- **Email Notifications**: Automated updates via Gmail, Office 365, or custom SMTP
- **Google Chat Integration**: Two-way notifications to Google Chat spaces

### Chromebook Management
- **Device Inventory**: Track all student Chromebooks
- **Checkout/Check-in**: Student device assignment and return workflows
- **Damage Reporting**: Document and track device damage with severity levels
- **Compliance Policies**: Configurable checkout policies and liability rules
- **Overdue Tracking**: Automatic notifications for unreturned devices
- **Student History**: Complete checkout and damage history per student

### Vehicle Request System
- **Fleet Inventory**: Track all district vehicles
- **Request Workflow**: Student/staff request approval process
- **Mileage Tracking**: Log and track vehicle mileage
- **Maintenance Logging**: Schedule and track vehicle maintenance
- **Driver Assignment**: Assign drivers and track usage

### IT Asset Management (ITAM)
- **Asset Inventory**: Track hardware and software across all endpoints
- **Automatic Discovery**: Deployable agent collects system information
- **Software Tracking**: Installed applications and versions
- **Update Management**: Monitor pending Windows updates
- **Network Information**: IP addresses, MAC addresses, and connectivity

### Cybersecurity & CVE Monitoring
- **CVE Detection**: Automatic vulnerability scanning against NVD database
- **Risk Assessment**: CVSS scoring and severity classification
- **Acknowledgment Tracking**: Mark vulnerabilities as reviewed
- **Scheduled Scanning**: Weekly CVE checks (configurable)
- **Critical Alerts**: Real-time notifications for critical vulnerabilities

### Inventory Management
- **Consumables Tracking**: Monitor printer toner, keyboards, monitors, etc.
- **Reorder Alerts**: Automatic notifications when stock runs low
- **Transaction History**: Track all inventory movements
- **Supplier Management**: Maintain supplier information and contacts

### Knowledge Base
- **Self-Service Articles**: Staff and students can find answers independently
- **Category Organization**: Organize articles by topic
- **Search & Filtering**: Quick access to relevant information
- **Helpful Ratings**: Track article usefulness

### Reporting & Analytics
- **Dashboard**: Real-time metrics and KPIs
- **Standard Reports**: Pre-built ticket, asset, and CVE reports
- **Custom Reports**: Drag-and-drop report builder
- **Export Capabilities**: Generate and share reports in PDF, CSV, Excel

### Full Customization
- **Logo Upload**: Upload your school district logo
- **Color Customization**: Pick custom colors for all UI elements
- **Font Selection**: Choose from professional font families
- **Custom CSS**: Advanced users can add custom CSS
- **Live Preview**: See changes in real-time

### User Management
- **Role-Based Access**: Admin, Technician, End User roles
- **Google OAuth**: Single sign-on integration
- **Department Tracking**: Organize users and assets by department
- **Audit Trail**: Track all changes and actions

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (3000)                 │
│    Dashboard • Tickets • Chromebooks • Vehicles • Assets │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend (8000)                  │
│  Tickets • Assets • Chromebooks • Vehicles • Branding    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database (5432)                  │
│    All Data: Tickets, Assets, Devices, CVEs, Users      │
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
│   │   │   ├── models.py        # Core models
│   │   │   ├── models_extended.py  # Vehicles, Inventory, KB
│   │   │   └── chromebook_models.py # Chromebook system
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   │   ├── chromebooks.py   # Chromebook API
│   │   │   ├── vehicles.py      # Vehicle API
│   │   │   └── ...
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
│   │   │   ├── ChromebooksPage.jsx
│   │   │   ├── BrandingPage.jsx
│   │   │   └── ...
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
├── DEPLOYMENT.md                # Deployment guide
├── presentation.html            # Interactive overview
└── presentation_updated.html    # Updated with new modules
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

## 🎨 Customization

### Branding Settings

Access the **Branding & Customization** page in Settings to:

1. **Upload Logo** - Add your school district logo
2. **Choose Colors** - Customize primary, secondary, accent, and status colors
3. **Select Fonts** - Choose from professional font families
4. **Add Custom CSS** - Advanced styling options
5. **Configure Footer** - Add support contact information

All changes apply instantly across the entire platform.

## 📱 Chromebook Management

### Checkout Process
1. Staff member selects device and student
2. Condition documented at checkout
3. Device assigned to student
4. System tracks checkout date and expected return

### Check-In Process
1. Staff member records return
2. Condition documented at check-in
3. Damage assessed and reported if needed
4. Device returned to inventory

### Damage Reporting
- Document damage with photos
- Assign severity level (minor, moderate, severe)
- Track student responsibility
- Generate repair tickets

## 🚐 Vehicle Management

### Request Workflow
1. User submits vehicle request
2. Admin reviews and approves/rejects
3. Vehicle assigned if approved
4. Driver uses vehicle
5. Mileage and condition logged on return

### Maintenance Tracking
- Schedule maintenance
- Track service history
- Monitor warranty expiration
- Log maintenance costs

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

### Chromebook Endpoints
- `GET /api/chromebooks/inventory` - List all Chromebooks
- `POST /api/chromebooks/checkout` - Check out device
- `POST /api/chromebooks/checkin/{id}` - Check in device
- `GET /api/chromebooks/checkouts/active` - Active checkouts
- `GET /api/chromebooks/checkouts/overdue` - Overdue devices
- `POST /api/chromebooks/damage-report` - Report damage

### Vehicle Endpoints
- `GET /api/vehicles/inventory` - List vehicles
- `POST /api/vehicles/request` - Submit request
- `PUT /api/vehicles/request/{id}/approve` - Approve request
- `GET /api/vehicles/maintenance` - Maintenance logs

### Branding Endpoints
- `GET /api/settings/branding` - Get branding settings
- `PUT /api/settings/branding` - Update branding

See http://localhost:8000/docs for full API documentation.

## 🤖 Deploying the Agent

### Windows Endpoint

```bash
# 1. Install Python 3.11+
# 2. Download agent files
# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env
HELPDESK_API_URL=http://your-helpdesk-server:8000/api
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
- Chromebook checkout status
- Vehicle utilization

### Reporting
- Ticket resolution time
- SLA breach analysis
- CVE vulnerability trends
- Asset distribution by type/department
- Device damage trends
- Vehicle maintenance costs

## 🔄 Scheduled Tasks

- **CVE Scanning**: Weekly (configurable)
- **SLA Monitoring**: Continuous
- **Agent Reporting**: Daily (configurable)
- **Email Notifications**: Real-time
- **Overdue Notifications**: Daily

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

### Device Management
- `chromebooks` - Device inventory
- `chromebook_checkouts` - Checkout records
- `chromebook_damage_reports` - Damage tracking

### Fleet Management
- `vehicles` - Vehicle inventory
- `vehicle_requests` - Request records
- `vehicle_maintenance_logs` - Maintenance history

### ITAM Tables
- `assets` - Managed devices
- `installed_software` - Software inventory
- `update_status` - Pending updates

### Security Tables
- `cve_alerts` - Vulnerability alerts

### Customization
- `branding_settings` - Branding configuration

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
- [presentation.html](presentation.html) - Interactive overview
- [presentation_updated.html](presentation_updated.html) - Updated overview with new modules

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
- Handles typical school IT workloads (hardware, software, network, devices)
- Supports student device management (Chromebooks, tablets)
- Includes fleet management for transportation
- Scales from small to large districts
- Integrates with common school systems
- Provides compliance tracking and reporting

## 🚀 Next Steps

1. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Customize**: Update branding and colors in Settings
3. **Configure**: Set up SMTP and Google Chat
4. **Deploy Agents**: Install on Windows endpoints
5. **Train Users**: Show staff how to submit tickets
6. **Monitor**: Check dashboards and reports regularly

---

**Built for school districts. By IT professionals.**

Version 2.0.0 - Chromebook Management, Vehicle Requests, and Full Customization
