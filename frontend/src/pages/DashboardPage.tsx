import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { Shield, MapPin, AlertTriangle, TrendingUp } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { antiTheftApi, pathApi, emergencyApi } from '../services/api'

const DashboardPage = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  
  const [antiTheftEnabled, setAntiTheftEnabled] = useState(false)
  const [recentPaths, setRecentPaths] = useState([])
  const [recentReports, setRecentReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [antiTheftRes, pathsRes, reportsRes] = await Promise.all([
        antiTheftApi.getStatus().catch(() => ({ data: { is_enabled: false } })),
        pathApi.getList(5).catch(() => ({ data: [] })),
        emergencyApi.getReports(5).catch(() => ({ data: [] })),
      ])

      setAntiTheftEnabled(antiTheftRes.data?.is_enabled || false)
      setRecentPaths(pathsRes.data || [])
      setRecentReports(reportsRes.data || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    {
      title: t('dashboard.setupAntiTheft'),
      icon: Shield,
      color: 'bg-blue-500',
      action: () => navigate('/anti-theft'),
    },
    {
      title: t('dashboard.startTracking'),
      icon: MapPin,
      color: 'bg-green-500',
      action: () => navigate('/path-tracker'),
    },
    {
      title: t('dashboard.reportEmergency'),
      icon: AlertTriangle,
      color: 'bg-red-500',
      action: () => navigate('/emergency'),
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          {t('dashboard.welcome')}, {user?.first_name || user?.email}!
        </h1>
      </div>

      {/* Status Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.antiTheftStatus')}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {antiTheftEnabled ? t('dashboard.enabled') : t('dashboard.disabled')}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${antiTheftEnabled ? 'bg-green-100' : 'bg-gray-100'}`}>
              <Shield className={antiTheftEnabled ? 'text-green-600' : 'text-gray-400'} size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.recentPaths')}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{recentPaths.length}</p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <MapPin className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.recentReports')}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{recentReports.length}</p>
            </div>
            <div className="p-3 rounded-lg bg-red-100">
              <AlertTriangle className="text-red-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('dashboard.quickActions')}</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className="flex items-center space-x-4 p-6 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition"
            >
              <div className={`p-3 rounded-lg ${action.color}`}>
                <action.icon className="text-white" size={24} />
              </div>
              <span className="font-medium text-gray-900">{action.title}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage

