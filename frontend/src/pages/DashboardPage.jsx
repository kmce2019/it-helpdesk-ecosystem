import { useEffect, useState } from 'react'
import { reportingService } from '../services/api'
import { PieChart, Pie, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { FiAlertCircle, FiCheckCircle, FiClock, FiHardDrive } from 'react-icons/fi'

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await reportingService.getDashboard()
        setStats(response.data)
      } catch (error) {
        console.error('Failed to fetch dashboard:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="loading"></div></div>
  }

  if (!stats) {
    return <div className="text-center py-12">Failed to load dashboard</div>
  }

  const COLORS = ['#1a56db', '#7e8ba3', '#05b981', '#f59e0b', '#f02316']

  const categoryData = Object.entries(stats.tickets_by_category).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').toUpperCase(),
    value,
  }))

  const statusData = Object.entries(stats.tickets_by_status).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').toUpperCase(),
    value,
  }))

  const priorityData = Object.entries(stats.tickets_by_priority).map(([name, value]) => ({
    name: name.toUpperCase(),
    value,
  }))

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Last updated: {new Date().toLocaleString()}</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Open Tickets</p>
              <p className="text-3xl font-bold text-primary mt-2">{stats.open_tickets}</p>
            </div>
            <FiClock className="text-primary text-4xl opacity-20" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">In Progress</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{stats.in_progress_tickets}</p>
            </div>
            <FiCheckCircle className="text-blue-600 text-4xl opacity-20" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">SLA Breached</p>
              <p className="text-3xl font-bold text-danger mt-2">{stats.sla_breached}</p>
            </div>
            <FiAlertCircle className="text-danger text-4xl opacity-20" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Assets</p>
              <p className="text-3xl font-bold text-success mt-2">{stats.active_assets}</p>
            </div>
            <FiHardDrive className="text-success text-4xl opacity-20" />
          </div>
        </div>
      </div>

      {/* CVE Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">CVE Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Critical CVEs</span>
              <span className="badge badge-danger">{stats.critical_cves}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">High CVEs</span>
              <span className="badge badge-warning">{stats.high_cves}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Pending Updates</span>
              <span className="badge badge-info">{stats.pending_updates}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Tickets</span>
              <span className="font-bold text-lg">{stats.total_tickets}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Resolved Today</span>
              <span className="font-bold text-lg text-success">{stats.resolved_today}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Critical Tickets</span>
              <span className="font-bold text-lg text-danger">{stats.critical_tickets}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Assets</span>
              <span className="font-bold text-lg">{stats.total_assets}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active</span>
              <span className="font-bold text-lg text-success">{stats.active_assets}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Inactive</span>
              <span className="font-bold text-lg text-gray-500">{stats.total_assets - stats.active_assets}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tickets by Priority</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={priorityData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                {priorityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tickets by Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#1a56db" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Tickets</h3>
          <div className="space-y-3">
            {stats.recent_tickets.slice(0, 5).map((ticket) => (
              <div key={ticket.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{ticket.ticket_number}</p>
                  <p className="text-sm text-gray-600 truncate">{ticket.title}</p>
                </div>
                <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent CVE Alerts</h3>
          <div className="space-y-3">
            {stats.recent_cve_alerts.slice(0, 5).map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{alert.cve_id}</p>
                  <p className="text-sm text-gray-600">{alert.software_name}</p>
                </div>
                <span className={`badge badge-${alert.cvss_severity?.toLowerCase()}`}>{alert.cvss_score?.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
