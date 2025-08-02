import { useState, FormEvent } from 'react'
import useAuthStore from '../stores/authStore'
import { authAPI } from '../api/auth'
import { billingAPI } from '../api/billing'
import { Message } from '../types/types'

function Account() {
  const { user, setUser } = useAuthStore()
  const [isEditingUsername, setIsEditingUsername] = useState(false)
  const [newUsername, setNewUsername] = useState(user?.username || '')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<Message | null>(null)
  
  const handleUpdateUsername = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)
    
    try {
      const updatedUser = await authAPI.updateUsername(newUsername)
      setUser(updatedUser)
      setIsEditingUsername(false)
      setMessage({ type: 'success', text: 'Username updated successfully' })
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to update username' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleManageBilling = async () => {
    setLoading(true)
    try {
      const { url } = await billingAPI.getBillingPortal()
      window.location.href = url
    } catch {
      setMessage({ type: 'error', text: 'Failed to open billing portal' })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Account Settings</h1>
      
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message.text}
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow divide-y">
        {/* Profile Section */}
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <p className="mt-1 text-gray-900">{user?.email}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Username</label>
              {isEditingUsername ? (
                <form onSubmit={handleUpdateUsername} className="mt-1 flex gap-2">
                  <input
                    type="text"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsEditingUsername(false)
                      setNewUsername(user?.username || '')
                    }}
                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </form>
              ) : (
                <div className="mt-1 flex items-center gap-2">
                  <p className="text-gray-900">{user?.username || 'Not set'}</p>
                  <button
                    onClick={() => setIsEditingUsername(true)}
                    className="text-blue-600 hover:text-blue-500 text-sm"
                  >
                    Edit
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Subscription Section */}
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-4">Subscription</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Current Plan</label>
              <p className="mt-1 text-gray-900 capitalize">
                {user?.subscription?.plan || 'Free'}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Status</label>
              <p className="mt-1">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  user?.subscription?.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {user?.subscription?.status || 'Inactive'}
                </span>
              </p>
            </div>
            
            {user?.subscription?.status === 'active' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Images Remaining</label>
                  <p className="mt-1 text-gray-900">
                    {user.subscription.quota_remaining} / {user.subscription.quota_limit}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Next Billing Date</label>
                  <p className="mt-1 text-gray-900">
                    {new Date(user.subscription.current_period_end).toLocaleDateString()}
                  </p>
                </div>
              </>
            )}
            
            <button
              onClick={handleManageBilling}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Manage Billing
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Account