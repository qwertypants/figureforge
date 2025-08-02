import { useAuth } from 'react-oidc-context'

interface UserInfo {
  email?: string
  username?: string
  sub?: string
}

export const useOidcAuth = () => {
  const auth = useAuth()

  return {
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    user: auth.user,
    error: auth.error,
    
    signIn: () => auth.signinRedirect(),
    
    signOut: () => auth.signoutRedirect(),
    
    getAccessToken: (): string | undefined => auth.user?.access_token,
    
    getIdToken: (): string | undefined => auth.user?.id_token,
    
    getUserInfo: (): UserInfo => ({
      email: auth.user?.profile?.email as string | undefined,
      username: (auth.user?.profile?.preferred_username || auth.user?.profile?.name) as string | undefined,
      sub: auth.user?.profile?.sub as string | undefined
    })
  }
}