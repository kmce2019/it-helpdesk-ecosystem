import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { FiHome, FiTicket, FiHardDrive, FiBarChart2, FiSettings, FiLogOut, FiMenu } from 'react-icons/fi'
import { useState } from 'react'

export default function Layout({ children }) {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  const navItems = [
    { path: '/', label: 'Dashboard', icon: FiHome },
    { path: '/tickets', label: 'Tickets', icon: FiTicket },
    { path: '/assets', label: 'Assets', icon: FiHardDrive },
    { path: '/reports', label: 'Reports', icon: FiBarChart2 },
    ...(user?.role === 'admin' ? [{ path: '/settings', label: 'Settings', icon: FiSettings }] : []),
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-white border-r border-gray-200 shadow-sm transition-all duration-300 fixed h-screen overflow-y-auto`}>
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen && <h1 className="text-xl font-bold text-primary">IT Help Desk</h1>}
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 hover:bg-gray-100 rounded">
              <FiMenu size={20} />
            </button>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-primary text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <item.icon size={20} />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className={`flex items-center gap-3 ${sidebarOpen ? '' : 'justify-center'}`}>
            <div className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-bold">
              {user?.full_name?.charAt(0).toUpperCase()}
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
                <p className="text-xs text-gray-500 truncate">{user?.role}</p>
              </div>
            )}
          </div>
          <button
            onClick={logout}
            className={`w-full mt-4 flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors ${
              sidebarOpen ? '' : 'justify-center'
            }`}
          >
            <FiLogOut size={18} />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className={`${sidebarOpen ? 'ml-64' : 'ml-20'} flex-1 overflow-auto transition-all duration-300`}>
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  )
}
