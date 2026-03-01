import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { assetsService } from '../services/api'
import { FiArrowLeft, FiAlertCircle } from 'react-icons/fi'

export default function AssetDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [asset, setAsset] = useState(null)
  const [cves, setCves] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAsset = async () => {
      try {
        const [assetRes, cvesRes] = await Promise.all([
          assetsService.get(id),
          assetsService.getCves(id),
        ])
        setAsset(assetRes.data)
        setCves(cvesRes.data)
      } catch (error) {
        console.error('Failed to fetch asset:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchAsset()
  }, [id])

  const handleAcknowledgeCve = async (cveId) => {
    try {
      await assetsService.acknowledgeCve(id, cveId)
      const response = await assetsService.getCves(id)
      setCves(response.data)
    } catch (error) {
      console.error('Failed to acknowledge CVE:', error)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="loading"></div></div>
  }

  if (!asset) {
    return <div className="text-center py-12">Asset not found</div>
  }

  const criticalCves = cves.filter(c => c.cvss_severity === 'CRITICAL')
  const highCves = cves.filter(c => c.cvss_severity === 'HIGH')
  const unacknowledgedCves = cves.filter(c => !c.is_acknowledged)

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'badge-danger',
      HIGH: 'badge-warning',
      MEDIUM: 'badge-info',
      LOW: 'badge-success',
    }
    return colors[severity] || 'badge-primary'
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/assets')}
        className="flex items-center gap-2 text-primary hover:text-blue-700"
      >
        <FiArrowLeft /> Back to Assets
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Asset Overview */}
          <div className="card">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{asset.hostname || asset.asset_tag}</h1>
            <p className="text-gray-600 mb-6">{asset.device_type}</p>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-600 mb-4">Hardware</h3>
                <div className="space-y-3 text-sm">
                  <div>
                    <p className="text-gray-600">Manufacturer</p>
                    <p className="font-medium text-gray-900">{asset.manufacturer || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Model</p>
                    <p className="font-medium text-gray-900">{asset.model || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Serial Number</p>
                    <p className="font-medium text-gray-900">{asset.serial_number || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">CPU</p>
                    <p className="font-medium text-gray-900 truncate">{asset.cpu || 'N/A'}</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-600 mb-4">System</h3>
                <div className="space-y-3 text-sm">
                  <div>
                    <p className="text-gray-600">OS</p>
                    <p className="font-medium text-gray-900">{asset.os_name} {asset.os_version}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">RAM</p>
                    <p className="font-medium text-gray-900">{asset.ram_gb ? `${asset.ram_gb}GB` : 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Disk Space</p>
                    <p className="font-medium text-gray-900">
                      {asset.disk_free_gb && asset.disk_total_gb
                        ? `${asset.disk_free_gb}GB / ${asset.disk_total_gb}GB`
                        : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Installed Software */}
          {asset.software && asset.software.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Installed Software</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {asset.software.map((sw, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{sw.name}</p>
                      <p className="text-sm text-gray-600">{sw.version || 'Unknown version'}</p>
                    </div>
                    {sw.vendor && <p className="text-sm text-gray-500">{sw.vendor}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* CVE Alerts */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FiAlertCircle className="text-danger" />
              CVE Vulnerabilities ({cves.length})
            </h3>

            {cves.length === 0 ? (
              <p className="text-gray-600">No CVEs detected</p>
            ) : (
              <div className="space-y-3">
                {cves.map((cve) => (
                  <div key={cve.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-bold text-gray-900">{cve.cve_id}</p>
                        <p className="text-sm text-gray-600">{cve.software_name} {cve.software_version}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`badge ${getSeverityColor(cve.cvss_severity)}`}>
                          {cve.cvss_severity}
                        </span>
                        <span className="text-sm font-bold text-gray-900">{cve.cvss_score?.toFixed(1)}</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{cve.description}</p>
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-gray-500">
                        Published: {new Date(cve.published_date).toLocaleDateString()}
                      </p>
                      {!cve.is_acknowledged && (
                        <button
                          onClick={() => handleAcknowledgeCve(cve.cve_id)}
                          className="text-sm text-primary hover:text-blue-700 font-medium"
                        >
                          Acknowledge
                        </button>
                      )}
                      {cve.is_acknowledged && (
                        <span className="text-xs text-gray-500">
                          Acknowledged by {cve.acknowledged_by}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Status</h3>
            <div className="space-y-3">
              <div>
                <p className="text-gray-600 text-sm">Status</p>
                <span className={`badge ${asset.is_active ? 'badge-success' : 'badge-danger'}`}>
                  {asset.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Last Seen</p>
                <p className="font-medium text-gray-900">
                  {asset.last_seen ? new Date(asset.last_seen).toLocaleString() : 'Never'}
                </p>
              </div>
            </div>
          </div>

          {/* CVE Summary */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">CVE Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Critical</span>
                <span className="badge badge-danger">{criticalCves.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">High</span>
                <span className="badge badge-warning">{highCves.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Unacknowledged</span>
                <span className="badge badge-info">{unacknowledgedCves.length}</span>
              </div>
            </div>
          </div>

          {/* Network Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Network</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-600">IP Address</p>
                <p className="font-medium text-gray-900">{asset.ip_address || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">MAC Address</p>
                <p className="font-medium text-gray-900 break-all">{asset.mac_address || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">Location</p>
                <p className="font-medium text-gray-900">{asset.location || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">Department</p>
                <p className="font-medium text-gray-900">{asset.department || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
