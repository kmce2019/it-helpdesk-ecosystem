import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { assetsService } from '../services/api'
import { FiSearch } from 'react-icons/fi'

export default function AssetsPage() {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deviceType, setDeviceType] = useState('')

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const response = await assetsService.list({ search, device_type: deviceType })
        setAssets(response.data)
      } catch (error) {
        console.error('Failed to fetch assets:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchAssets()
  }, [search, deviceType])

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="loading"></div></div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Assets (ITAM)</h1>

      {/* Filters */}
      <div className="card space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <FiSearch className="absolute left-3 top-3 text-gray-400" />
            <input
              type="text"
              placeholder="Search assets..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          <select
            value={deviceType}
            onChange={(e) => setDeviceType(e.target.value)}
            className="input-field"
          >
            <option value="">All Device Types</option>
            <option value="desktop">Desktop</option>
            <option value="laptop">Laptop</option>
            <option value="server">Server</option>
            <option value="printer">Printer</option>
          </select>
        </div>
      </div>

      {/* Assets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {assets.map((asset) => (
          <Link
            key={asset.id}
            to={`/assets/${asset.id}`}
            className="card hover:shadow-lg transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-bold text-gray-900">{asset.hostname || asset.asset_tag}</h3>
                <p className="text-sm text-gray-600">{asset.device_type}</p>
              </div>
              <span className={`badge ${asset.is_active ? 'badge-success' : 'badge-danger'}`}>
                {asset.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium">Asset Tag:</span> {asset.asset_tag}</p>
              <p><span className="font-medium">OS:</span> {asset.os_name} {asset.os_version}</p>
              <p><span className="font-medium">IP:</span> {asset.ip_address || 'N/A'}</p>
              <p><span className="font-medium">RAM:</span> {asset.ram_gb ? `${asset.ram_gb}GB` : 'N/A'}</p>
              <p><span className="font-medium">Last Seen:</span> {asset.last_seen ? new Date(asset.last_seen).toLocaleDateString() : 'Never'}</p>
            </div>
          </Link>
        ))}
      </div>

      {assets.length === 0 && (
        <div className="text-center py-12 text-gray-500">No assets found</div>
      )}
    </div>
  )
}
