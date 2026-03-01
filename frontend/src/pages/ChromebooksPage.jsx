import { useEffect, useState } from 'react'
import { chromebookService } from '../services/api'
import { FiPlus, FiSearch, FiFilter, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi'

export default function ChromebooksPage() {
  const [inventory, setInventory] = useState(null)
  const [activeCheckouts, setActiveCheckouts] = useState([])
  const [overdueCheckouts, setOverdueCheckouts] = useState([])
  const [damageReports, setDamageReports] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showCheckoutForm, setShowCheckoutForm] = useState(false)
  const [showDamageForm, setShowDamageForm] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [invResponse, checkoutResponse, overdueResponse, damageResponse] = await Promise.all([
          chromebookService.getInventory(),
          chromebookService.getActiveCheckouts(),
          chromebookService.getOverdueCheckouts(),
          chromebookService.getPendingDamageReports(),
        ])

        setInventory(invResponse.data)
        setActiveCheckouts(checkoutResponse.data.active_checkouts)
        setOverdueCheckouts(overdueResponse.data.overdue_checkouts)
        setDamageReports(damageResponse.data.pending_reports)
      } catch (error) {
        console.error('Failed to fetch Chromebook data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleCheckout = async (formData) => {
    try {
      await chromebookService.checkoutChromebook(formData)
      setShowCheckoutForm(false)
      // Refresh data
      window.location.reload()
    } catch (error) {
      console.error('Checkout failed:', error)
    }
  }

  const handleCheckin = async (checkoutId) => {
    try {
      await chromebookService.checkinChromebook(checkoutId, {
        actual_return_date: new Date(),
        condition_at_return: 'Good',
        damage_at_return: 'none',
      })
      window.location.reload()
    } catch (error) {
      console.error('Check-in failed:', error)
    }
  }

  const handleDamageReport = async (formData) => {
    try {
      await chromebookService.createDamageReport(formData)
      setShowDamageForm(false)
      window.location.reload()
    } catch (error) {
      console.error('Damage report failed:', error)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="loading"></div></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Chromebook Management</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowCheckoutForm(!showCheckoutForm)}
            className="btn-primary flex items-center gap-2"
          >
            <FiPlus /> Checkout Device
          </button>
          <button
            onClick={() => setShowDamageForm(!showDamageForm)}
            className="btn-secondary flex items-center gap-2"
          >
            <FiAlertTriangle /> Report Damage
          </button>
        </div>
      </div>

      {/* Inventory Summary */}
      {inventory && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary">{inventory.total}</div>
            <div className="text-sm text-gray-600">Total Devices</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-green-600">{inventory.available}</div>
            <div className="text-sm text-gray-600">Available</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-blue-600">{inventory.checked_out}</div>
            <div className="text-sm text-gray-600">Checked Out</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-orange-600">{inventory.in_repair}</div>
            <div className="text-sm text-gray-600">In Repair</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-gray-600">{inventory.retired}</div>
            <div className="text-sm text-gray-600">Retired</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-red-600">{inventory.lost}</div>
            <div className="text-sm text-gray-600">Lost</div>
          </div>
        </div>
      )}

      {/* Checkout Form */}
      {showCheckoutForm && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Checkout Chromebook</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              handleCheckout(Object.fromEntries(formData))
            }}
            className="space-y-4"
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Chromebook Asset Tag</label>
                <input type="text" name="chromebook_id" required className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Student ID</label>
                <input type="text" name="student_id" required className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Student Name</label>
                <input type="text" name="student_name" required className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Grade Level</label>
                <select name="grade_level" className="input-field">
                  <option>9th</option>
                  <option>10th</option>
                  <option>11th</option>
                  <option>12th</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Condition at Checkout</label>
                <textarea name="condition_at_checkout" rows="2" className="input-field" />
              </div>
            </div>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowCheckoutForm(false)} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Checkout Device
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Damage Report Form */}
      {showDamageForm && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Report Device Damage</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              handleDamageReport(Object.fromEntries(formData))
            }}
            className="space-y-4"
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Asset Tag</label>
                <input type="text" name="chromebook_id" required className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Damage Level</label>
                <select name="damage_level" required className="input-field">
                  <option value="minor">Minor</option>
                  <option value="moderate">Moderate</option>
                  <option value="severe">Severe</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea name="damage_description" rows="3" required className="input-field" />
              </div>
              <div className="col-span-2">
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="student_responsible" className="w-4 h-4" />
                  <span className="text-sm font-medium text-gray-700">Student Responsible</span>
                </label>
              </div>
            </div>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowDamageForm(false)} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Submit Report
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Overdue Checkouts Alert */}
      {overdueCheckouts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-900 mb-3">⚠️ Overdue Checkouts ({overdueCheckouts.length})</h3>
          <div className="space-y-2">
            {overdueCheckouts.map((checkout) => (
              <div key={checkout.id} className="flex items-center justify-between p-3 bg-white rounded border border-red-100">
                <div>
                  <p className="font-medium text-gray-900">{checkout.student_name}</p>
                  <p className="text-sm text-gray-600">{checkout.asset_tag} • {checkout.days_overdue} days overdue</p>
                </div>
                <button
                  onClick={() => handleCheckin(checkout.id)}
                  className="btn-primary text-sm"
                >
                  Check In
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Checkouts */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Active Checkouts ({activeCheckouts.length})</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Asset Tag</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Student</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Grade</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Checkout Date</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Expected Return</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-900">Action</th>
              </tr>
            </thead>
            <tbody>
              {activeCheckouts.map((checkout) => (
                <tr key={checkout.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-900">{checkout.asset_tag}</td>
                  <td className="py-3 px-4 text-gray-600">{checkout.student_name}</td>
                  <td className="py-3 px-4 text-gray-600">{checkout.grade_level}</td>
                  <td className="py-3 px-4 text-gray-600">{checkout.checkout_date}</td>
                  <td className="py-3 px-4 text-gray-600">{checkout.expected_return_date}</td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => handleCheckin(checkout.id)}
                      className="text-primary hover:text-primary-dark font-medium"
                    >
                      Check In
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Damage Reports */}
      {damageReports.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pending Damage Reports ({damageReports.length})</h2>
          <div className="space-y-3">
            {damageReports.map((report) => (
              <div key={report.id} className="p-4 border border-orange-200 rounded-lg bg-orange-50">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{report.asset_tag}</p>
                    <p className="text-sm text-gray-600 mt-1">{report.damage_description}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Severity: <span className="font-medium capitalize">{report.damage_level}</span>
                    </p>
                    {report.student_responsible && (
                      <p className="text-sm text-red-600 mt-1">⚠️ Student Responsible</p>
                    )}
                  </div>
                  <span className="px-3 py-1 bg-orange-200 text-orange-900 rounded-full text-sm font-medium">
                    Pending
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
