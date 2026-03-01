import { useState } from 'react'
import { settingsService } from '../services/api'

export default function SettingsPage() {
  const [smtpSettings, setSmtpSettings] = useState({
    host: 'smtp.gmail.com',
    port: '587',
    username: '',
    password: '',
    from_email: 'helpdesk@district.edu',
  })

  const [googleChatSettings, setGoogleChatSettings] = useState({
    webhook_url: '',
  })

  const [testEmail, setTestEmail] = useState('')
  const [testMessage, setTestMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const handleSmtpChange = (field, value) => {
    setSmtpSettings({ ...smtpSettings, [field]: value })
  }

  const handleGoogleChatChange = (field, value) => {
    setGoogleChatSettings({ ...googleChatSettings, [field]: value })
  }

  const handleTestEmail = async () => {
    setLoading(true)
    try {
      const response = await settingsService.testEmail({
        to_email: testEmail,
        subject: 'Test Email from District IT Help Desk',
      })
      if (response.data.success) {
        setSuccessMessage('Test email sent successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (error) {
      console.error('Failed to send test email:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTestGoogleChat = async () => {
    setLoading(true)
    try {
      const response = await settingsService.testGoogleChat({
        message: testMessage || 'Test message from District IT Help Desk',
      })
      if (response.data.success) {
        setSuccessMessage('Test message sent successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (error) {
      console.error('Failed to send test message:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Settings</h1>

      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* SMTP Configuration */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Email (SMTP) Configuration</h2>
        <div className="space-y-4 mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Host</label>
              <input
                type="text"
                value={smtpSettings.host}
                onChange={(e) => handleSmtpChange('host', e.target.value)}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Port</label>
              <input
                type="number"
                value={smtpSettings.port}
                onChange={(e) => handleSmtpChange('port', e.target.value)}
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={smtpSettings.username}
              onChange={(e) => handleSmtpChange('username', e.target.value)}
              placeholder="your-email@gmail.com"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password / App Password</label>
            <input
              type="password"
              value={smtpSettings.password}
              onChange={(e) => handleSmtpChange('password', e.target.value)}
              placeholder="Enter your app-specific password"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From Email Address</label>
            <input
              type="email"
              value={smtpSettings.from_email}
              onChange={(e) => handleSmtpChange('from_email', e.target.value)}
              className="input-field"
            />
          </div>
        </div>

        <div className="border-t border-gray-200 pt-4 space-y-3">
          <h3 className="font-semibold text-gray-900">Test Email Configuration</h3>
          <div className="flex gap-3">
            <input
              type="email"
              value={testEmail}
              onChange={(e) => setTestEmail(e.target.value)}
              placeholder="Enter test email address"
              className="input-field flex-1"
            />
            <button
              onClick={handleTestEmail}
              disabled={!testEmail || loading}
              className="btn-primary"
            >
              {loading ? 'Sending...' : 'Send Test'}
            </button>
          </div>
        </div>
      </div>

      {/* Google Chat Configuration */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Google Chat Integration</h2>
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Webhook URL</label>
            <input
              type="text"
              value={googleChatSettings.webhook_url}
              onChange={(e) => handleGoogleChatChange('webhook_url', e.target.value)}
              placeholder="https://chat.googleapis.com/v1/spaces/..."
              className="input-field"
            />
            <p className="text-sm text-gray-600 mt-2">
              Get your webhook URL from <a href="https://chat.google.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google Chat</a>
            </p>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-4 space-y-3">
          <h3 className="font-semibold text-gray-900">Test Google Chat</h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Enter test message"
              className="input-field flex-1"
            />
            <button
              onClick={handleTestGoogleChat}
              disabled={!googleChatSettings.webhook_url || loading}
              className="btn-primary"
            >
              {loading ? 'Sending...' : 'Send Test'}
            </button>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">System Information</h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Application Name</span>
            <span className="font-medium text-gray-900">District IT Help Desk</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Version</span>
            <span className="font-medium text-gray-900">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Environment</span>
            <span className="font-medium text-gray-900">Production</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Database</span>
            <span className="font-medium text-gray-900">PostgreSQL</span>
          </div>
        </div>
      </div>
    </div>
  )
}
