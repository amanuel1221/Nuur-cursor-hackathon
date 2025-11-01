import { useTranslation } from 'react-i18next'

const AntiTheftPage = () => {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">{t('antiTheft.title')}</h1>
      
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
        <p className="text-gray-600">Anti-theft configuration interface coming soon...</p>
        <p className="text-sm text-gray-500 mt-2">
          This page will allow users to configure SMS triggers, GPS tracking, and emergency contacts.
        </p>
      </div>
    </div>
  )
}

export default AntiTheftPage

