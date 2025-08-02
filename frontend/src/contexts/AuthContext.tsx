import React, { createContext, useContext, useEffect, useState } from "react";
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserSession,
  CognitoUserAttribute,
} from "amazon-cognito-identity-js";
import useAuthStore from "../stores/authStore";
import { authAPI } from "../api/auth";

interface AuthContextType {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: CognitoUser | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  confirmSignUp: (email: string, code: string) => Promise<void>;
  resendConfirmationCode: (email: string) => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  confirmPassword: (
    email: string,
    code: string,
    newPassword: string,
  ) => Promise<void>;
  getSession: () => Promise<CognitoUserSession | null>;
  refreshSession: () => Promise<void>;
  requestMagicLink: (email: string) => Promise<void>;
  verifyMagicLink: (email: string, code: string) => Promise<void>;
}

const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
};

const userPool = new CognitoUserPool(poolData);

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<CognitoUser | null>(null);
  const { setUser: setStoreUser, setLoading: setStoreLoading } = useAuthStore();

  const getSession = async (): Promise<CognitoUserSession | null> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();
      if (!cognitoUser) {
        resolve(null);
        return;
      }

      cognitoUser.getSession(
        (err: Error | null, session: CognitoUserSession | null) => {
          if (err) {
            reject(err);
          } else {
            resolve(session);
          }
        },
      );
    });
  };

  const refreshSession = async () => {
    try {
      const session = await getSession();
      if (session && session.isValid()) {
        const idToken = session.getIdToken().getJwtToken();
        localStorage.setItem("authToken", idToken);

        // Sync with backend
        const userProfile = await authAPI.getProfile();
        setStoreUser(userProfile);
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
        setStoreUser(null);
        localStorage.removeItem("authToken");
      }
    } catch (error) {
      console.error("Failed to refresh session:", error);
      setIsAuthenticated(false);
      setStoreUser(null);
      localStorage.removeItem("authToken");
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);
      setStoreLoading(true);

      try {
        const cognitoUser = userPool.getCurrentUser();
        if (cognitoUser) {
          setUser(cognitoUser);
          await refreshSession();
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
        setStoreLoading(false);
      }
    };

    checkAuth();
  }, [setStoreUser, setStoreLoading]);

  const signIn = async (email: string, password: string) => {
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: userPool,
    });

    const authDetails = new AuthenticationDetails({
      Username: email,
      Password: password,
    });

    return new Promise<void>((resolve, reject) => {
      cognitoUser.authenticateUser(authDetails, {
        onSuccess: async (session) => {
          setUser(cognitoUser);
          const idToken = session.getIdToken().getJwtToken();
          localStorage.setItem("authToken", idToken);

          try {
            const userProfile = await authAPI.getProfile();
            setStoreUser(userProfile);
            setIsAuthenticated(true);
            resolve();
          } catch (error) {
            reject(error);
          }
        },
        onFailure: (err) => {
          reject(err);
        },
      });
    });
  };

  const signUp = async (email: string, password: string) => {
    const attributeList = [
      new CognitoUserAttribute({
        Name: "email",
        Value: email,
      }),
    ];

    return new Promise<void>((resolve, reject) => {
      userPool.signUp(email, password, attributeList, [], (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  };

  const confirmSignUp = async (email: string, code: string) => {
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: userPool,
    });

    return new Promise<void>((resolve, reject) => {
      cognitoUser.confirmRegistration(code, true, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  };

  const resendConfirmationCode = async (email: string) => {
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: userPool,
    });

    return new Promise<void>((resolve, reject) => {
      cognitoUser.resendConfirmationCode((err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      });
    });
  };

  const signOut = async () => {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
    }
    setUser(null);
    setIsAuthenticated(false);
    setStoreUser(null);
    localStorage.removeItem("authToken");
  };

  const forgotPassword = async (email: string) => {
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: userPool,
    });

    return new Promise<void>((resolve, reject) => {
      cognitoUser.forgotPassword({
        onSuccess: () => {
          resolve();
        },
        onFailure: (err) => {
          reject(err);
        },
      });
    });
  };

  const confirmPassword = async (
    email: string,
    code: string,
    newPassword: string,
  ) => {
    const cognitoUser = new CognitoUser({
      Username: email,
      Pool: userPool,
    });

    return new Promise<void>((resolve, reject) => {
      cognitoUser.confirmPassword(code, newPassword, {
        onSuccess: () => {
          resolve();
        },
        onFailure: (err) => {
          reject(err);
        },
      });
    });
  };

  const requestMagicLink = async (email: string) => {
    try {
      await authAPI.requestMagicLink(email);
    } catch (error) {
      throw error;
    }
  };

  const verifyMagicLink = async (email: string, code: string) => {
    try {
      const response = await authAPI.verifyMagicLink(email, code);
      if (response.access_token) {
        localStorage.setItem("authToken", response.access_token);

        // Get user profile
        const userProfile = await authAPI.getProfile();
        setStoreUser(userProfile);
        setIsAuthenticated(true);
      }
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    isLoading,
    isAuthenticated,
    user,
    signIn,
    signUp,
    signOut,
    confirmSignUp,
    resendConfirmationCode,
    forgotPassword,
    confirmPassword,
    getSession,
    refreshSession,
    requestMagicLink,
    verifyMagicLink,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
