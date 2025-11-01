import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Shield, MapPin, AlertTriangle, ArrowRight, Globe } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useEffect } from 'react'

const LandingPage = () => {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'am' : 'en'
    i18n.changeLanguage(newLang)
    localStorage.setItem('language', newLang)
  }

  const features = [
    {
      icon: Shield,
      title: t('landing.features.antiTheft.title'),
      description: t('landing.features.antiTheft.description'),
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      icon: MapPin,
      title: t('landing.features.pathTracker.title'),
      description: t('landing.features.pathTracker.description'),
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      icon: AlertTriangle,
      title: t('landing.features.emergency.title'),
      description: t('landing.features.emergency.description'),
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                N
              </div>
              <span className="text-2xl font-bold text-gray-900">{t('app.name')}</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleLanguage}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition"
              >
                <Globe size={20} />
                <span>{i18n.language === 'en' ? 'አማርኛ' : 'English'}</span>
              </button>
              
              <button
                onClick={() => navigate('/login')}
                className="px-6 py-2 text-primary-600 hover:text-primary-700 font-medium transition"
              >
                {t('landing.hero.ctaLogin')}
              </button>
              
              <button
                onClick={() => navigate('/register')}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition shadow-sm"
              >
                {t('landing.hero.ctaRegister')}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            {t('landing.hero.title')}
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            {t('landing.hero.subtitle')}
          </p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => navigate('/register')}
              className="flex items-center space-x-2 px-8 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition shadow-lg text-lg font-semibold"
            >
              <span>{t('landing.hero.ctaRegister')}</span>
              <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          {t('landing.features.title')}
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 hover:shadow-md transition"
            >
              <div className={`w-14 h-14 ${feature.bg} rounded-lg flex items-center justify-center mb-6`}>
                <feature.icon className={feature.color} size={28} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                N
              </div>
              <span className="text-2xl font-bold">{t('app.name')}</span>
            </div>
            <p className="text-gray-400 mb-2">{t('app.tagline')}</p>
            <p className="text-sm text-gray-500">
              © 2025 NuuR. All rights reserved. | Ethiopia
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

