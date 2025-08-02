import api from "./config";
import { PricingPlan, CheckoutSession, BillingPortal } from "../types/types";

interface PricingResponse {
  plans: PricingPlan[];
}

export const billingAPI = {
  // Get pricing plans
  getPricing: async (): Promise<PricingResponse> => {
    const response = await api.get<PricingResponse>("/pricing");
    return response.data;
  },

  // Create checkout session
  createCheckoutSession: async (priceId: string): Promise<CheckoutSession> => {
    const response = await api.post<CheckoutSession>(
      "/billing/checkout-session",
      {
        price_id: priceId,
      },
    );
    return response.data;
  },

  // Get billing portal URL
  getBillingPortal: async (): Promise<BillingPortal> => {
    const response = await api.post<BillingPortal>("/billing/portal");
    return response.data;
  },
};
