import api from "./config";
import { User } from "../types/types";

export const authAPI = {
  // Get current user profile
  getProfile: async (): Promise<User> => {
    const response = await api.get("/auth/user/");
    // Map backend response to User type
    const userData: User = {
      id: response.data.user_id,
      email: response.data.email,
      username: response.data.username,
      role: response.data.role,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      subscription: {
        plan: response.data.subscription_plan || "hobby",
        status: "active",
        quota_limit: response.data.quota_limit || 50,
        quota_remaining:
          (response.data.quota_limit || 50) - (response.data.quota_used || 0),
        current_period_start: new Date().toISOString(),
        current_period_end: new Date(
          Date.now() + 30 * 24 * 60 * 60 * 1000,
        ).toISOString(),
      },
    };
    return userData;
  },

  // Update username
  updateUsername: async (username: string): Promise<User> => {
    const response = await api.put("/auth/user/update/", { username });
    // Map backend response to User type
    return {
      id: response.data.user.user_id,
      email: response.data.user.email,
      username: response.data.user.username,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as User;
  },

  // Logout (if backend has logout endpoint)
  logout: async (): Promise<void> => {
    try {
      await api.post("/logout");
    } catch {
      // Logout endpoint might not exist, continue with local logout
    }
    localStorage.removeItem("authToken");
  },

  // Request magic link
  requestMagicLink: async (email: string): Promise<void> => {
    await api.post("/auth/magic-link/request/", { email });
  },

  // Verify magic link
  verifyMagicLink: async (
    email: string,
    code: string,
  ): Promise<{ access_token: string }> => {
    const response = await api.post("/auth/magic-link/verify/", {
      email,
      code,
    });
    return response.data;
  },
};
