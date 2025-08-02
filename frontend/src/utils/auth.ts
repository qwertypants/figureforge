import { 
  CognitoUserPool, 
  CognitoUser, 
  AuthenticationDetails, 
  ISignUpResult,
  CognitoUserSession,
  CognitoUserAttribute
} from 'amazon-cognito-identity-js'

// Cognito configuration
const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || '',
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID || ''
}

const userPool = new CognitoUserPool(poolData)

export const cognitoAuth = {
  // Sign up new user
  signUp: async (email: string, password: string, username: string): Promise<ISignUpResult | undefined> => {
    return new Promise((resolve, reject) => {
      const attributes: CognitoUserAttribute[] = [
        new CognitoUserAttribute({
          Name: 'preferred_username',
          Value: username
        })
      ]
      
      userPool.signUp(
        email,
        password,
        attributes,
        [],
        (err, result) => {
          if (err) {
            reject(err)
          } else {
            resolve(result)
          }
        }
      )
    })
  },
  
  // Confirm sign up with code
  confirmSignUp: async (email: string, code: string): Promise<any> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool
      })
      
      cognitoUser.confirmRegistration(code, true, (err, result) => {
        if (err) {
          reject(err)
        } else {
          resolve(result)
        }
      })
    })
  },
  
  // Sign in user
  signIn: async (email: string, password: string): Promise<CognitoUserSession> => {
    return new Promise((resolve, reject) => {
      const authenticationDetails = new AuthenticationDetails({
        Username: email,
        Password: password
      })
      
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool
      })
      
      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result) => {
          const idToken = result.getIdToken().getJwtToken()
          localStorage.setItem('authToken', idToken)
          resolve(result)
        },
        onFailure: (err) => {
          reject(err)
        }
      })
    })
  },
  
  // Sign out user
  signOut: (): void => {
    const cognitoUser = userPool.getCurrentUser()
    if (cognitoUser) {
      cognitoUser.signOut()
    }
    localStorage.removeItem('authToken')
  },
  
  // Get current user
  getCurrentUser: (): CognitoUser | null => {
    return userPool.getCurrentUser()
  },
  
  // Get session
  getSession: async (): Promise<CognitoUserSession> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser()
      if (!cognitoUser) {
        reject(new Error('No user'))
        return
      }
      
      cognitoUser.getSession((err: Error | null, session: CognitoUserSession | null) => {
        if (err) {
          reject(err)
        } else if (session) {
          resolve(session)
        } else {
          reject(new Error('No session'))
        }
      })
    })
  },
  
  // Refresh token
  refreshToken: async (): Promise<string | undefined> => {
    const session = await cognitoAuth.getSession()
    if (session.isValid()) {
      const idToken = session.getIdToken().getJwtToken()
      localStorage.setItem('authToken', idToken)
      return idToken
    }
  },
  
  // Forgot password
  forgotPassword: async (email: string): Promise<any> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool
      })
      
      cognitoUser.forgotPassword({
        onSuccess: (result) => {
          resolve(result)
        },
        onFailure: (err) => {
          reject(err)
        }
      })
    })
  },
  
  // Confirm new password
  confirmPassword: async (email: string, code: string, newPassword: string): Promise<any> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool
      })
      
      cognitoUser.confirmPassword(code, newPassword, {
        onSuccess: (result) => {
          resolve(result)
        },
        onFailure: (err) => {
          reject(err)
        }
      })
    })
  }
}