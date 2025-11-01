import { useTranslation } from 'react-i18next'

const EmergencyPage = () => {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">{t('emergency.title')}</h1>
      
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
        <p className="text-gray-600">Emergency reporting interface coming soon...</p>
        <p className="text-sm text-gray-500 mt-2">
          This page will allow users to quickly report emergencies with location and media attachments.
        </p>
      </div>
    </div>
  )
}

export default EmergencyPage

