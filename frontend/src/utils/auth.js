import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js'

// Cognito configuration
const poolData = {
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || '',
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID || ''
}

const userPool = new CognitoUserPool(poolData)

export const cognitoAuth = {
  // Sign up new user
  signUp: async (email, password, username) => {
    return new Promise((resolve, reject) => {
      userPool.signUp(
        email,
        password,
        [
          {
            Name: 'preferred_username',
            Value: username
          }
        ],
        null,
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
  confirmSignUp: async (email, code) => {
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
  signIn: async (email, password) => {
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
  signOut: () => {
    const cognitoUser = userPool.getCurrentUser()
    if (cognitoUser) {
      cognitoUser.signOut()
    }
    localStorage.removeItem('authToken')
  },
  
  // Get current user
  getCurrentUser: () => {
    return userPool.getCurrentUser()
  },
  
  // Get session
  getSession: async () => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser()
      if (!cognitoUser) {
        reject(new Error('No user'))
        return
      }
      
      cognitoUser.getSession((err, session) => {
        if (err) {
          reject(err)
        } else {
          resolve(session)
        }
      })
    })
  },
  
  // Refresh token
  refreshToken: async () => {
    const session = await cognitoAuth.getSession()
    if (session.isValid()) {
      const idToken = session.getIdToken().getJwtToken()
      localStorage.setItem('authToken', idToken)
      return idToken
    }
  },
  
  // Forgot password
  forgotPassword: async (email) => {
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
  confirmPassword: async (email, code, newPassword) => {
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