import api from './config'

export const billingAPI = {
  // Get pricing plans
  getPricing: async () => {
    const response = await api.get('/pricing')
    return response.data
  },
  
  // Create checkout session
  createCheckoutSession: async (priceId) => {
    const response = await api.post('/billing/checkout-session', {
      price_id: priceId
    })
    return response.data
  },
  
  // Get billing portal URL
  getBillingPortal: async () => {
    const response = await api.post('/billing/portal')
    return response.data
  }
}