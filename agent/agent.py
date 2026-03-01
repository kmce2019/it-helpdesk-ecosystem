#!/usr/bin/env python3
"""
District IT Help Desk - Deployable Agent
Collects ITAM data, monitors for CVEs, and reports to the central help desk system.
"""

import os
import sys
import json
import logging
import socket
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional
import requests
import schedule
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('HELPDESK_API_URL', 'http://localhost:8000/api')
AGENT_API_KEY = os.getenv('AGENT_API_KEY', 'change-me')
ASSET_TAG = os.getenv('ASSET_TAG', socket.gethostname())
REPORT_INTERVAL_HOURS = int(os.getenv('REPORT_INTERVAL_HOURS', '24'))
CVE_CHECK_INTERVAL_HOURS = int(os.getenv('CVE_CHECK_INTERVAL_HOURS', '168'))  # Weekly

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('helpdesk_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemInfo:
    """Collect system information for ITAM."""

    @staticmethod
    def get_hostname() -> str:
        """Get system hostname."""
        return socket.gethostname()

    @staticmethod
    def get_device_type() -> str:
        """Determine device type (desktop, laptop, server)."""
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystem():
                    chassis = item.PCSystemType
                    if chassis == 2:
                        return 'laptop'
                    elif chassis == 3:
                        return 'desktop'
                    elif chassis == 1:
                        return 'server'
            except Exception:
                pass
        return 'desktop'

    @staticmethod
    def get_manufacturer() -> str:
        """Get system manufacturer."""
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystemProduct():
                    return item.Vendor or 'Unknown'
            except Exception:
                pass
        return 'Unknown'

    @staticmethod
    def get_model() -> str:
        """Get system model."""
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystemProduct():
                    return item.Name or 'Unknown'
            except Exception:
                pass
        return 'Unknown'

    @staticmethod
    def get_serial_number() -> str:
        """Get system serial number."""
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystemProduct():
                    return item.IdentifyingNumber or 'Unknown'
            except Exception:
                pass
        return 'Unknown'

    @staticmethod
    def get_os_info() -> Dict[str, str]:
        """Get OS information."""
        system = platform.system()
        version = platform.version()
        release = platform.release()
        
        if system == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_OperatingSystem():
                    return {
                        'name': item.Caption or 'Windows',
                        'version': item.Version or version,
                        'build': item.BuildNumber or '',
                    }
            except Exception:
                pass
        
        return {
            'name': system,
            'version': version,
            'build': release,
        }

    @staticmethod
    def get_cpu_info() -> str:
        """Get CPU information."""
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_Processor():
                    return item.Name or 'Unknown'
            except Exception:
                pass
        return platform.processor() or 'Unknown'

    @staticmethod
    def get_memory_info() -> Dict[str, float]:
        """Get memory information in GB."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                'total_gb': mem.total / (1024 ** 3),
                'available_gb': mem.available / (1024 ** 3),
                'used_gb': mem.used / (1024 ** 3),
            }
        except Exception:
            return {'total_gb': 0, 'available_gb': 0, 'used_gb': 0}

    @staticmethod
    def get_disk_info() -> Dict[str, float]:
        """Get disk information in GB."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                'total_gb': disk.total / (1024 ** 3),
                'used_gb': disk.used / (1024 ** 3),
                'free_gb': disk.free / (1024 ** 3),
            }
        except Exception:
            return {'total_gb': 0, 'used_gb': 0, 'free_gb': 0}

    @staticmethod
    def get_ip_address() -> str:
        """Get primary IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return 'Unknown'

    @staticmethod
    def get_mac_address() -> str:
        """Get MAC address."""
        try:
            import uuid
            return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0, 2*6, 2)][::-1])
        except Exception:
            return 'Unknown'

    @staticmethod
    def get_installed_software() -> List[Dict]:
        """Get list of installed software."""
        software = []
        
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_Product():
                    software.append({
                        'name': item.Name or 'Unknown',
                        'version': item.Version or '',
                        'vendor': item.Vendor or '',
                        'install_date': item.InstallDate or '',
                    })
            except Exception as e:
                logger.warning(f"Failed to get installed software: {e}")
        
        return software[:100]  # Limit to 100 most recent

    @staticmethod
    def get_pending_updates() -> Dict:
        """Get pending Windows updates."""
        updates = {
            'pending_count': 0,
            'critical_count': 0,
            'security_count': 0,
            'updates': []
        }
        
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_QuickFixEngineering():
                    updates['updates'].append({
                        'kb_number': item.HotFixID or '',
                        'description': item.Description or '',
                    })
                updates['pending_count'] = len(updates['updates'])
            except Exception as e:
                logger.warning(f"Failed to get update status: {e}")
        
        return updates


class HelpdeskAgent:
    """Main agent class for reporting to the help desk system."""

    def __init__(self):
        self.api_url = API_BASE_URL
        self.api_key = AGENT_API_KEY
        self.asset_tag = ASSET_TAG
        self.session = requests.Session()
        self.session.headers.update({'X-Agent-Key': self.api_key})
        logger.info(f"Agent initialized for asset: {self.asset_tag}")

    def collect_system_data(self) -> Dict:
        """Collect all system data."""
        logger.info("Collecting system data...")
        
        os_info = SystemInfo.get_os_info()
        mem_info = SystemInfo.get_memory_info()
        disk_info = SystemInfo.get_disk_info()
        
        data = {
            'asset_tag': self.asset_tag,
            'hostname': SystemInfo.get_hostname(),
            'device_type': SystemInfo.get_device_type(),
            'manufacturer': SystemInfo.get_manufacturer(),
            'model': SystemInfo.get_model(),
            'serial_number': SystemInfo.get_serial_number(),
            'os_name': os_info.get('name'),
            'os_version': os_info.get('version'),
            'os_build': os_info.get('build'),
            'cpu': SystemInfo.get_cpu_info(),
            'ram_gb': mem_info.get('total_gb', 0),
            'disk_total_gb': disk_info.get('total_gb', 0),
            'disk_free_gb': disk_info.get('free_gb', 0),
            'ip_address': SystemInfo.get_ip_address(),
            'mac_address': SystemInfo.get_mac_address(),
            'agent_version': '1.0.0',
            'software': SystemInfo.get_installed_software(),
            'pending_updates': SystemInfo.get_pending_updates().get('updates', []),
        }
        
        logger.info(f"System data collected: {data['hostname']} ({data['os_name']} {data['os_version']})")
        return data

    def report_to_helpdesk(self):
        """Report system data to the help desk."""
        try:
            data = self.collect_system_data()
            
            response = self.session.post(
                f'{self.api_url}/agent/report',
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully reported to help desk: {response.json()}")
                return True
            else:
                logger.error(f"Failed to report to help desk: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error reporting to help desk: {e}")
            return False

    def health_check(self):
        """Check connection to help desk."""
        try:
            response = self.session.get(
                f'{self.api_url}/agent/health',
                timeout=10
            )
            if response.status_code == 200:
                logger.info("Health check passed")
                return True
            else:
                logger.warning(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False

    def schedule_reports(self):
        """Schedule periodic reports."""
        schedule.every(REPORT_INTERVAL_HOURS).hours.do(self.report_to_helpdesk)
        schedule.every(CVE_CHECK_INTERVAL_HOURS).hours.do(self.report_to_helpdesk)
        
        logger.info(f"Reports scheduled every {REPORT_INTERVAL_HOURS} hours")
        logger.info(f"CVE checks scheduled every {CVE_CHECK_INTERVAL_HOURS} hours")

    def run(self):
        """Run the agent."""
        logger.info("Starting District IT Help Desk Agent")
        
        # Initial health check
        if not self.health_check():
            logger.error("Cannot connect to help desk. Check API_URL and AGENT_API_KEY.")
            sys.exit(1)
        
        # Initial report
        self.report_to_helpdesk()
        
        # Schedule periodic reports
        self.schedule_reports()
        
        # Run scheduler
        logger.info("Agent running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
            sys.exit(0)


if __name__ == '__main__':
    agent = HelpdeskAgent()
    agent.run()
