import { useAuth } from 'react-oidc-context'

export const useOidcAuth = () => {
  const auth = useAuth()

  return {
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    user: auth.user,
    error: auth.error,
    
    signIn: () => auth.signinRedirect(),
    
    signOut: () => auth.signoutRedirect(),
    
    getAccessToken: () => auth.user?.access_token,
    
    getIdToken: () => auth.user?.id_token,
    
    getUserInfo: () => ({
      email: auth.user?.profile?.email,
      username: auth.user?.profile?.preferred_username || auth.user?.profile?.name,
      sub: auth.user?.profile?.sub
    })
  }
}