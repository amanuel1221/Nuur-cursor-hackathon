import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'

const ProfilePage = () => {
  const { t } = useTranslation()
  const user = useAuthStore((state) => state.user)

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">{t('profile.title')}</h1>
      
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('profile.personalInfo')}</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('auth.email')}
            </label>
            <input
              type="email"
              value={user?.email || ''}
              readOnly
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('auth.phone')}
            </label>
            <input
              type="tel"
              value={user?.phone_number || ''}
              readOnly
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.firstName')}
              </label>
              <input
                type="text"
                value={user?.first_name || ''}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.lastName')}
              </label>
              <input
                type="text"
                value={user?.last_name || ''}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage

