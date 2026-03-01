import { useState, useEffect } from 'react'
import { settingsService } from '../services/api'
import { FiUpload, FiSave, FiRefreshCw } from 'react-icons/fi'

export default function BrandingPage() {
  const [branding, setBranding] = useState({
    organization_name: 'District IT Help Desk',
    logo_url: '',
    favicon_url: '',
    primary_color: '#667eea',
    secondary_color: '#764ba2',
    accent_color: '#05b981',
    danger_color: '#f02316',
    warning_color: '#f59e0b',
    success_color: '#05b981',
    font_family: 'Inter',
    heading_font: 'Inter',
    footer_text: 'Built for school districts. By IT professionals.',
    support_email: 'support@district.edu',
    support_phone: '+1 (555) 123-4567',
    custom_css: '',
  })

  const [logoPreview, setLogoPreview] = useState(null)
  const [faviconPreview, setFaviconPreview] = useState(null)
  const [saving, setSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const FONT_OPTIONS = [
    { name: 'Inter', value: 'Inter' },
    { name: 'Roboto', value: 'Roboto' },
    { name: 'Open Sans', value: 'Open Sans' },
    { name: 'Poppins', value: 'Poppins' },
    { name: 'Lato', value: 'Lato' },
    { name: 'Montserrat', value: 'Montserrat' },
  ]

  const handleChange = (field, value) => {
    setBranding({ ...branding, [field]: value })
  }

  const handleLogoUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setLogoPreview(event.target.result)
        handleChange('logo_url', event.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleFaviconUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setFaviconPreview(event.target.result)
        handleChange('favicon_url', event.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await settingsService.updateBranding(branding)
      setSuccessMessage('Branding settings saved successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
      // Apply theme changes dynamically
      applyTheme(branding)
    } catch (error) {
      console.error('Failed to save branding:', error)
    } finally {
      setSaving(false)
    }
  }

  const applyTheme = (theme) => {
    const root = document.documentElement
    root.style.setProperty('--primary-color', theme.primary_color)
    root.style.setProperty('--secondary-color', theme.secondary_color)
    root.style.setProperty('--accent-color', theme.accent_color)
    root.style.setProperty('--danger-color', theme.danger_color)
    root.style.setProperty('--warning-color', theme.warning_color)
    root.style.setProperty('--success-color', theme.success_color)
    root.style.fontFamily = theme.font_family
  }

  const handleReset = () => {
    if (confirm('Reset all branding to defaults?')) {
      setBranding({
        organization_name: 'District IT Help Desk',
        logo_url: '',
        favicon_url: '',
        primary_color: '#667eea',
        secondary_color: '#764ba2',
        accent_color: '#05b981',
        danger_color: '#f02316',
        warning_color: '#f59e0b',
        success_color: '#05b981',
        font_family: 'Inter',
        heading_font: 'Inter',
        footer_text: 'Built for school districts. By IT professionals.',
        support_email: 'support@district.edu',
        support_phone: '+1 (555) 123-4567',
        custom_css: '',
      })
      setLogoPreview(null)
      setFaviconPreview(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Branding & Customization</h1>
        <button
          onClick={handleReset}
          className="btn-secondary flex items-center gap-2"
        >
          <FiRefreshCw /> Reset to Default
        </button>
      </div>

      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Organization Info */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Organization Information</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Organization Name</label>
            <input
              type="text"
              value={branding.organization_name}
              onChange={(e) => handleChange('organization_name', e.target.value)}
              className="input-field"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Support Email</label>
              <input
                type="email"
                value={branding.support_email}
                onChange={(e) => handleChange('support_email', e.target.value)}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Support Phone</label>
              <input
                type="tel"
                value={branding.support_phone}
                onChange={(e) => handleChange('support_phone', e.target.value)}
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Footer Text</label>
            <textarea
              value={branding.footer_text}
              onChange={(e) => handleChange('footer_text', e.target.value)}
              rows="2"
              className="input-field"
            />
          </div>
        </div>
      </div>

      {/* Logo & Favicon */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Logo & Favicon</h2>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Logo</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {logoPreview ? (
                <img src={logoPreview} alt="Logo preview" className="max-h-32 mx-auto mb-3" />
              ) : (
                <div className="text-gray-500 mb-3">No logo uploaded</div>
              )}
              <label className="btn-secondary flex items-center justify-center gap-2 cursor-pointer">
                <FiUpload /> Upload Logo
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoUpload}
                  className="hidden"
                />
              </label>
              <p className="text-xs text-gray-500 mt-2">PNG, JPG, or SVG (max 2MB)</p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Favicon</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {faviconPreview ? (
                <img src={faviconPreview} alt="Favicon preview" className="max-h-16 mx-auto mb-3" />
              ) : (
                <div className="text-gray-500 mb-3">No favicon uploaded</div>
              )}
              <label className="btn-secondary flex items-center justify-center gap-2 cursor-pointer">
                <FiUpload /> Upload Favicon
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFaviconUpload}
                  className="hidden"
                />
              </label>
              <p className="text-xs text-gray-500 mt-2">ICO or PNG (32x32px)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Color Scheme */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Color Scheme</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {[
            { label: 'Primary Color', field: 'primary_color' },
            { label: 'Secondary Color', field: 'secondary_color' },
            { label: 'Accent Color', field: 'accent_color' },
            { label: 'Danger Color', field: 'danger_color' },
            { label: 'Warning Color', field: 'warning_color' },
            { label: 'Success Color', field: 'success_color' },
          ].map((color) => (
            <div key={color.field}>
              <label className="block text-sm font-medium text-gray-700 mb-2">{color.label}</label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={branding[color.field]}
                  onChange={(e) => handleChange(color.field, e.target.value)}
                  className="w-16 h-10 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={branding[color.field]}
                  onChange={(e) => handleChange(color.field, e.target.value)}
                  className="input-field flex-1 font-mono text-sm"
                  placeholder="#000000"
                />
              </div>
            </div>
          ))}
        </div>

        {/* Color Preview */}
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <p className="text-sm font-medium text-gray-700 mb-4">Preview</p>
          <div className="flex gap-3 flex-wrap">
            <div
              className="w-24 h-24 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
              style={{ backgroundColor: branding.primary_color }}
            >
              Primary
            </div>
            <div
              className="w-24 h-24 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
              style={{ backgroundColor: branding.secondary_color }}
            >
              Secondary
            </div>
            <div
              className="w-24 h-24 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
              style={{ backgroundColor: branding.accent_color }}
            >
              Accent
            </div>
            <div
              className="w-24 h-24 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
              style={{ backgroundColor: branding.danger_color }}
            >
              Danger
            </div>
            <div
              className="w-24 h-24 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
              style={{ backgroundColor: branding.warning_color }}
            >
              Warning
            </div>
            <div
              className="w-24 h-24 rounded-lg shadow-md flex items-center justify-center text-white font-semibold"
              style={{ backgroundColor: branding.success_color }}
            >
              Success
            </div>
          </div>
        </div>
      </div>

      {/* Typography */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Typography</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Body Font</label>
            <select
              value={branding.font_family}
              onChange={(e) => handleChange('font_family', e.target.value)}
              className="input-field"
            >
              {FONT_OPTIONS.map((font) => (
                <option key={font.value} value={font.value}>
                  {font.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Heading Font</label>
            <select
              value={branding.heading_font}
              onChange={(e) => handleChange('heading_font', e.target.value)}
              className="input-field"
            >
              {FONT_OPTIONS.map((font) => (
                <option key={font.value} value={font.value}>
                  {font.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Font Preview */}
        <div className="mt-6 p-6 bg-gray-50 rounded-lg" style={{ fontFamily: branding.font_family }}>
          <p style={{ fontFamily: branding.heading_font }} className="text-2xl font-bold mb-2">
            Heading Preview
          </p>
          <p className="text-base">Body text preview with {branding.font_family} font family</p>
        </div>
      </div>

      {/* Custom CSS */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Advanced - Custom CSS</h2>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Custom CSS Overrides</label>
          <textarea
            value={branding.custom_css}
            onChange={(e) => handleChange('custom_css', e.target.value)}
            rows="8"
            className="input-field font-mono text-sm"
            placeholder="/* Add custom CSS here */&#10;.btn-primary { &#10;  /* your styles */ &#10;}"
          />
          <p className="text-xs text-gray-600 mt-2">
            Advanced users can add custom CSS to override default styles. Changes apply after saving.
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={handleReset}
          className="btn-secondary"
        >
          Reset
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center gap-2"
        >
          <FiSave /> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}
