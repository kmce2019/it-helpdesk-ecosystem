import { useEffect, useState } from 'react'
import { reportingService } from '../services/api'
import { PieChart, Pie, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { FiPlus, FiX } from 'react-icons/fi'

export default function ReportsPage() {
  const [dashboardStats, setDashboardStats] = useState(null)
  const [customReports, setCustomReports] = useState([])
  const [showBuilder, setShowBuilder] = useState(false)
  const [selectedCharts, setSelectedCharts] = useState([])
  const [reportName, setReportName] = useState('')
  const [loading, setLoading] = useState(true)

  const AVAILABLE_CHARTS = [
    { id: 'tickets-by-status', name: 'Tickets by Status', type: 'bar' },
    { id: 'tickets-by-priority', name: 'Tickets by Priority', type: 'pie' },
    { id: 'tickets-by-category', name: 'Tickets by Category', type: 'pie' },
    { id: 'cves-by-severity', name: 'CVEs by Severity', type: 'bar' },
    { id: 'assets-by-type', name: 'Assets by Type', type: 'pie' },
    { id: 'assets-by-department', name: 'Assets by Department', type: 'bar' },
    { id: 'sla-compliance', name: 'SLA Compliance', type: 'line' },
    { id: 'resolution-time', name: 'Avg Resolution Time', type: 'bar' },
  ]

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await reportingService.getDashboard()
        setDashboardStats(response.data)
      } catch (error) {
        console.error('Failed to fetch reports:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchReports()
  }, [])

  const handleAddChart = (chartId) => {
    if (!selectedCharts.includes(chartId)) {
      setSelectedCharts([...selectedCharts, chartId])
    }
  }

  const handleRemoveChart = (chartId) => {
    setSelectedCharts(selectedCharts.filter(id => id !== chartId))
  }

  const handleSaveReport = () => {
    if (reportName && selectedCharts.length > 0) {
      const newReport = {
        id: Date.now(),
        name: reportName,
        charts: selectedCharts,
        createdAt: new Date(),
      }
      setCustomReports([...customReports, newReport])
      setReportName('')
      setSelectedCharts([])
      setShowBuilder(false)
    }
  }

  const handleDeleteReport = (reportId) => {
    setCustomReports(customReports.filter(r => r.id !== reportId))
  }

  const handlePrintReport = (reportId) => {
    window.print()
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="loading"></div></div>
  }

  const COLORS = ['#1a56db', '#7e8ba3', '#05b981', '#f59e0b', '#f02316']

  const renderChart = (chartId) => {
    if (!dashboardStats) return null

    const chartConfig = {
      'tickets-by-status': {
        data: Object.entries(dashboardStats.tickets_by_status).map(([name, value]) => ({
          name: name.replace(/_/g, ' ').toUpperCase(),
          value,
        })),
        type: 'bar',
      },
      'tickets-by-priority': {
        data: Object.entries(dashboardStats.tickets_by_priority).map(([name, value]) => ({
          name: name.toUpperCase(),
          value,
        })),
        type: 'pie',
      },
      'tickets-by-category': {
        data: Object.entries(dashboardStats.tickets_by_category).map(([name, value]) => ({
          name: name.replace(/_/g, ' ').toUpperCase(),
          value,
        })),
        type: 'pie',
      },
    }

    const config = chartConfig[chartId]
    if (!config) return null

    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {AVAILABLE_CHARTS.find(c => c.id === chartId)?.name}
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          {config.type === 'pie' ? (
            <PieChart>
              <Pie data={config.data} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                {config.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          ) : (
            <BarChart data={config.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#1a56db" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <button
          onClick={() => setShowBuilder(!showBuilder)}
          className="btn-primary flex items-center gap-2"
        >
          <FiPlus /> Build Custom Report
        </button>
      </div>

      {/* Report Builder */}
      {showBuilder && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Build Custom Report</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Report Name</label>
              <input
                type="text"
                value={reportName}
                onChange={(e) => setReportName(e.target.value)}
                placeholder="Enter report name..."
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Available Charts</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {AVAILABLE_CHARTS.map((chart) => (
                  <button
                    key={chart.id}
                    onClick={() => handleAddChart(chart.id)}
                    disabled={selectedCharts.includes(chart.id)}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      selectedCharts.includes(chart.id)
                        ? 'border-primary bg-blue-50'
                        : 'border-gray-200 hover:border-primary'
                    }`}
                  >
                    <p className="font-medium text-gray-900">{chart.name}</p>
                    <p className="text-xs text-gray-600">{chart.type}</p>
                  </button>
                ))}
              </div>
            </div>

            {selectedCharts.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Selected Charts</label>
                <div className="space-y-2">
                  {selectedCharts.map((chartId) => (
                    <div key={chartId} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <p className="font-medium text-gray-900">
                        {AVAILABLE_CHARTS.find(c => c.id === chartId)?.name}
                      </p>
                      <button
                        onClick={() => handleRemoveChart(chartId)}
                        className="text-danger hover:text-red-700"
                      >
                        <FiX />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3 justify-end pt-4">
              <button
                onClick={() => setShowBuilder(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveReport}
                disabled={!reportName || selectedCharts.length === 0}
                className="btn-primary"
              >
                Save Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Standard Reports */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Standard Reports</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {renderChart('tickets-by-status')}
          {renderChart('tickets-by-priority')}
          {renderChart('tickets-by-category')}
        </div>
      </div>

      {/* Custom Reports */}
      {customReports.length > 0 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Custom Reports</h2>
          {customReports.map((report) => (
            <div key={report.id} className="card">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{report.name}</h3>
                  <p className="text-sm text-gray-600">Created {report.createdAt.toLocaleDateString()}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handlePrintReport(report.id)}
                    className="btn-secondary"
                  >
                    Print
                  </button>
                  <button
                    onClick={() => handleDeleteReport(report.id)}
                    className="btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {report.charts.map((chartId) => renderChart(chartId))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
