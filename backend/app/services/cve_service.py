import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from ..models.models import Asset, InstalledSoftware, CVEAlert
from ..config import settings

logger = logging.getLogger(__name__)

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


async def query_nvd_for_software(software_name: str, version: Optional[str] = None) -> List[Dict]:
    """Query the NVD API for CVEs related to a specific software."""
    params = {
        "keywordSearch": software_name,
        "resultsPerPage": 20,
    }
    if settings.NVD_API_KEY:
        params["apiKey"] = settings.NVD_API_KEY

    headers = {}
    if settings.NVD_API_KEY:
        headers["apiKey"] = settings.NVD_API_KEY

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(NVD_BASE_URL, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get("vulnerabilities", [])
                results = []
                for vuln in vulnerabilities:
                    cve = vuln.get("cve", {})
                    cve_id = cve.get("id", "")
                    descriptions = cve.get("descriptions", [])
                    description = next(
                        (d["value"] for d in descriptions if d.get("lang") == "en"), ""
                    )
                    metrics = cve.get("metrics", {})
                    cvss_score = None
                    cvss_severity = None

                    # Try CVSS v3.1 first, then v3.0, then v2.0
                    for cvss_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                        if cvss_key in metrics and metrics[cvss_key]:
                            m = metrics[cvss_key][0]
                            cvss_data = m.get("cvssData", {})
                            cvss_score = cvss_data.get("baseScore")
                            cvss_severity = cvss_data.get("baseSeverity") or m.get("baseSeverity")
                            break

                    published = cve.get("published", "")
                    try:
                        published_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    except Exception:
                        published_dt = None

                    results.append({
                        "cve_id": cve_id,
                        "description": description,
                        "cvss_score": cvss_score,
                        "cvss_severity": cvss_severity,
                        "published_date": published_dt,
                    })
                return results
            else:
                logger.warning(f"NVD API returned status {response.status_code} for {software_name}")
                return []
    except Exception as e:
        logger.error(f"Error querying NVD for {software_name}: {e}")
        return []


async def run_cve_scan_for_asset(db: Session, asset: Asset) -> int:
    """Run a CVE scan for all software on a given asset. Returns number of new alerts."""
    new_alerts = 0
    existing_cve_ids = {alert.cve_id for alert in asset.cve_alerts}

    # Focus on OS and key software
    software_to_check = []
    if asset.os_name and asset.os_version:
        software_to_check.append((f"{asset.os_name} {asset.os_version}", asset.os_version))

    for sw in asset.software:
        if sw.name and sw.version:
            software_to_check.append((sw.name, sw.version))

    checked_names = set()
    for sw_name, sw_version in software_to_check[:20]:  # Limit to 20 per scan to respect rate limits
        if sw_name in checked_names:
            continue
        checked_names.add(sw_name)

        cves = await query_nvd_for_software(sw_name, sw_version)
        for cve_data in cves:
            cve_id = cve_data["cve_id"]
            if cve_id not in existing_cve_ids:
                alert = CVEAlert(
                    asset_id=asset.id,
                    cve_id=cve_id,
                    software_name=sw_name,
                    software_version=sw_version,
                    cvss_score=cve_data.get("cvss_score"),
                    cvss_severity=cve_data.get("cvss_severity"),
                    description=cve_data.get("description"),
                    published_date=cve_data.get("published_date"),
                )
                db.add(alert)
                existing_cve_ids.add(cve_id)
                new_alerts += 1

    db.commit()
    return new_alerts


async def run_full_cve_scan(db: Session) -> Dict:
    """Run CVE scan for all active assets."""
    assets = db.query(Asset).filter(Asset.is_active == True).all()
    total_new_alerts = 0
    assets_scanned = 0

    for asset in assets:
        try:
            new = await run_cve_scan_for_asset(db, asset)
            total_new_alerts += new
            assets_scanned += 1
        except Exception as e:
            logger.error(f"CVE scan failed for asset {asset.asset_tag}: {e}")

    logger.info(f"CVE scan complete: {assets_scanned} assets scanned, {total_new_alerts} new alerts")
    return {"assets_scanned": assets_scanned, "new_alerts": total_new_alerts}
