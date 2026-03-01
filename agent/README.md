# District IT Help Desk - Deployable Agent

This agent is designed to run on Windows endpoints to collect ITAM data, monitor for CVE vulnerabilities, and report back to the central help desk system.

## Features

- **ITAM Data Collection**: Gathers hardware specs, OS info, installed software, and network details
- **CVE Monitoring**: Checks installed software against known CVE databases
- **Update Status**: Tracks pending Windows updates
- **Automatic Reporting**: Sends data to the help desk API on a schedule
- **Health Checks**: Verifies connectivity to the help desk system

## Installation

### Windows (Standalone)

1. **Install Python 3.11+** from python.org
2. **Clone or download the agent files**
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the agent** by editing `.env`:
   ```
   HELPDESK_API_URL=http://your-helpdesk-server:8000/api
   AGENT_API_KEY=your-agent-api-key
   ASSET_TAG=ASSET-001
   REPORT_INTERVAL_HOURS=24
   CVE_CHECK_INTERVAL_HOURS=168
   ```
5. **Run the agent**:
   ```bash
   python agent.py
   ```

### Windows (Service Installation)

To run the agent as a Windows service:

1. Install `pywin32`:
   ```bash
   pip install pywin32
   python Scripts/pywin32_postinstall.py -install
   ```

2. Create a batch file `install_service.bat`:
   ```batch
   @echo off
   python -m win32serviceutil.InstallService -serviceName "HelpdeskAgent" -displayName "IT Help Desk Agent" -moduleName agent
   ```

3. Run the batch file as Administrator

4. Start the service:
   ```bash
   net start HelpdeskAgent
   ```

### Docker

Build and run the agent in a Docker container:

```bash
docker build -t helpdesk-agent .
docker run -d \
  -e HELPDESK_API_URL=http://helpdesk-api:8000/api \
  -e AGENT_API_KEY=your-api-key \
  -e ASSET_TAG=docker-agent-001 \
  --name helpdesk-agent \
  helpdesk-agent
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HELPDESK_API_URL` | `http://localhost:8000/api` | URL to the help desk API |
| `AGENT_API_KEY` | `change-me` | API key for authentication |
| `ASSET_TAG` | System hostname | Unique identifier for this asset |
| `REPORT_INTERVAL_HOURS` | `24` | How often to report system data (hours) |
| `CVE_CHECK_INTERVAL_HOURS` | `168` | How often to check for CVEs (hours, default: weekly) |

## Logs

The agent logs to:
- **Console**: Real-time output
- **File**: `helpdesk_agent.log` in the agent directory

## Troubleshooting

### Connection Errors
- Verify `HELPDESK_API_URL` is correct and accessible
- Check `AGENT_API_KEY` matches the backend configuration
- Ensure firewall allows outbound connections to the help desk server

### Missing Data
- On Windows, WMI services may need to be running
- Some data (like installed software) requires admin privileges
- Check `helpdesk_agent.log` for specific errors

### CVE Checks Not Running
- Ensure the agent has been running for at least `CVE_CHECK_INTERVAL_HOURS`
- Check the help desk backend has NVD API access
- Review logs for API errors

## Security Considerations

- **API Key**: Keep `AGENT_API_KEY` confidential and change from default
- **HTTPS**: Use HTTPS for `HELPDESK_API_URL` in production
- **Firewall**: Restrict outbound connections to the help desk server only
- **Logs**: Logs may contain sensitive information; secure accordingly

## Support

For issues or questions, contact your IT department or check the help desk system logs.
