import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../stores/authStore'
import { billingAPI } from '../api/billing'
import { loadStripe } from '@stripe/stripe-js'

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '')

function Pricing() {
  const navigate = useNavigate()
  const { isAuthenticated, user } = useAuthStore()
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [checkoutLoading, setCheckoutLoading] = useState(null)
  
  useEffect(() => {
    loadPricing()
  }, [])
  
  const loadPricing = async () => {
    try {
      const data = await billingAPI.getPricing()
      setPlans(data.plans)
    } catch (error) {
      console.error('Failed to load pricing:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSubscribe = async (priceId) => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    
    setCheckoutLoading(priceId)
    
    try {
      const { sessionId } = await billingAPI.createCheckoutSession(priceId)
      const stripe = await stripePromise
      
      if (stripe) {
        const { error } = await stripe.redirectToCheckout({ sessionId })
        if (error) {
          console.error('Stripe redirect error:', error)
        }
      }
    } catch (error) {
      console.error('Failed to create checkout session:', error)
    } finally {
      setCheckoutLoading(null)
    }
  }
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading pricing...</div>
      </div>
    )
  }
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-xl text-gray-600">
          Select the perfect plan for your artistic journey
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => {
          const isCurrentPlan = user?.subscription?.plan === plan.name.toLowerCase()
          
          return (
            <div
              key={plan.id}
              className={`bg-white rounded-lg shadow-lg p-8 ${
                plan.recommended ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {plan.recommended && (
                <div className="bg-blue-500 text-white text-sm font-semibold px-3 py-1 rounded-full inline-block mb-4">
                  Recommended
                </div>
              )}
              
              <h2 className="text-2xl font-bold mb-2">{plan.name}</h2>
              <div className="mb-6">
                <span className="text-4xl font-bold">${plan.price}</span>
                <span className="text-gray-600">/month</span>
              </div>
              
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span>{plan.images_per_month} images per month</span>
                </li>
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              
              <button
                onClick={() => handleSubscribe(plan.stripe_price_id)}
                disabled={isCurrentPlan || checkoutLoading === plan.stripe_price_id}
                className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
                  isCurrentPlan
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : plan.recommended
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                } disabled:opacity-50`}
              >
                {isCurrentPlan
                  ? 'Current Plan'
                  : checkoutLoading === plan.stripe_price_id
                  ? 'Loading...'
                  : 'Subscribe'}
              </button>
            </div>
          )
        })}
      </div>
      
      <div className="mt-12 text-center text-gray-600">
        <p className="mb-2">All plans include:</p>
        <ul className="flex flex-wrap justify-center gap-4 text-sm">
          <li>• High-quality AI generation</li>
          <li>• Private image library</li>
          <li>• Download in high resolution</li>
          <li>• Cancel anytime</li>
        </ul>
      </div>
    </div>
  )
}

export default Pricing