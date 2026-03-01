FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .

# Create .env file from environment variables
RUN echo "HELPDESK_API_URL=${HELPDESK_API_URL:-http://localhost:8000/api}" > .env && \
    echo "AGENT_API_KEY=${AGENT_API_KEY:-change-me}" >> .env && \
    echo "ASSET_TAG=${ASSET_TAG:-docker-agent}" >> .env && \
    echo "REPORT_INTERVAL_HOURS=${REPORT_INTERVAL_HOURS:-24}" >> .env && \
    echo "CVE_CHECK_INTERVAL_HOURS=${CVE_CHECK_INTERVAL_HOURS:-168}" >> .env

# Run the agent
CMD ["python", "agent.py"]
