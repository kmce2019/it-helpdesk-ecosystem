import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ticketsService } from '../services/api'
import { useAuthStore } from '../stores/authStore'
import { FiArrowLeft } from 'react-icons/fi'

export default function TicketDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [ticket, setTicket] = useState(null)
  const [loading, setLoading] = useState(true)
  const [comment, setComment] = useState('')
  const [isUpdating, setIsUpdating] = useState(false)
  const [updateData, setUpdateData] = useState({})

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const response = await ticketsService.get(id)
        setTicket(response.data)
      } catch (error) {
        console.error('Failed to fetch ticket:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchTicket()
  }, [id])

  const handleAddComment = async (e) => {
    e.preventDefault()
    try {
      await ticketsService.addComment(id, { content: comment, is_internal: false })
      setComment('')
      const response = await ticketsService.get(id)
      setTicket(response.data)
    } catch (error) {
      console.error('Failed to add comment:', error)
    }
  }

  const handleUpdateTicket = async (field, value) => {
    try {
      await ticketsService.update(id, { [field]: value })
      const response = await ticketsService.get(id)
      setTicket(response.data)
    } catch (error) {
      console.error('Failed to update ticket:', error)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="loading"></div></div>
  }

  if (!ticket) {
    return <div className="text-center py-12">Ticket not found</div>
  }

  const canEdit = user?.role !== 'end_user' || ticket.submitter.id === user?.id

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/tickets')}
        className="flex items-center gap-2 text-primary hover:text-blue-700"
      >
        <FiArrowLeft /> Back to Tickets
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Ticket Header */}
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{ticket.title}</h1>
                <p className="text-gray-600 mt-1">{ticket.ticket_number}</p>
              </div>
              <span className={`badge badge-${ticket.priority}`}>{ticket.priority.toUpperCase()}</span>
            </div>
            <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
          </div>

          {/* Comments */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Comments & Updates</h3>
            <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
              {ticket.comments.map((c) => (
                <div key={c.id} className={`p-4 rounded-lg ${c.is_internal ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-gray-900">{c.author.full_name}</p>
                    <p className="text-xs text-gray-500">{new Date(c.created_at).toLocaleString()}</p>
                  </div>
                  {c.is_internal && <p className="text-xs text-yellow-700 mb-2">Internal Note</p>}
                  <p className="text-gray-700">{c.content}</p>
                </div>
              ))}
            </div>

            {canEdit && (
              <form onSubmit={handleAddComment} className="space-y-3 border-t border-gray-200 pt-4">
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="input-field"
                  rows="3"
                />
                <button type="submit" className="btn-primary">
                  Post Comment
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status & Assignment */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Details</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                {canEdit && user?.role !== 'end_user' ? (
                  <select
                    value={ticket.status}
                    onChange={(e) => handleUpdateTicket('status', e.target.value)}
                    className="input-field"
                  >
                    <option value="new">New</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                ) : (
                  <p className="text-gray-900 font-medium">{ticket.status.replace(/_/g, ' ')}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                {canEdit && user?.role !== 'end_user' ? (
                  <select
                    value={ticket.priority}
                    onChange={(e) => handleUpdateTicket('priority', e.target.value)}
                    className="input-field"
                  >
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                ) : (
                  <p className="text-gray-900 font-medium">{ticket.priority}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <p className="text-gray-900 font-medium">{ticket.category.replace(/_/g, ' ')}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Assigned To</label>
                <p className="text-gray-900 font-medium">{ticket.assignee?.full_name || 'Unassigned'}</p>
              </div>
            </div>
          </div>

          {/* SLA Info */}
          {ticket.sla && (
            <div className={`card ${ticket.sla_breached ? 'border-danger border-2' : ''}`}>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">SLA Status</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600">Response Due</p>
                  <p className="font-medium">{new Date(ticket.sla_response_due).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-600">Resolution Due</p>
                  <p className="font-medium">{new Date(ticket.sla_resolution_due).toLocaleString()}</p>
                </div>
                {ticket.sla_breached && (
                  <div className="bg-red-50 border border-red-200 rounded p-2">
                    <p className="text-danger font-medium">⚠️ SLA Breached</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="card text-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h3>
            <div className="space-y-3 text-gray-600">
              <div>
                <p className="font-medium text-gray-900">Created</p>
                <p>{new Date(ticket.created_at).toLocaleString()}</p>
              </div>
              {ticket.first_response_at && (
                <div>
                  <p className="font-medium text-gray-900">First Response</p>
                  <p>{new Date(ticket.first_response_at).toLocaleString()}</p>
                </div>
              )}
              {ticket.resolved_at && (
                <div>
                  <p className="font-medium text-gray-900">Resolved</p>
                  <p>{new Date(ticket.resolved_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
