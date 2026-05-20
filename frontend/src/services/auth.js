import axios from 'axios'

const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID
const REGION = import.meta.env.VITE_COGNITO_REGION

export const authService = {
  async login(email, password) {
    // Cognito authentication
    const response = await axios.post(
      `https://cognito-idp.${REGION}.amazonaws.com/`,
      {
        AuthFlow: 'USER_PASSWORD_AUTH',
        ClientId: CLIENT_ID,
        AuthParameters: {
          USERNAME: email,
          PASSWORD: password
        }
      },
      {
        headers: {
          'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
          'Content-Type': 'application/x-amz-json-1.1'
        }
      }
    )

    return response.data.AuthenticationResult
  },

  async signup(email, password, name) {
    const response = await axios.post(
      `https://cognito-idp.${REGION}.amazonaws.com/`,
      {
        ClientId: CLIENT_ID,
        Username: email,
        Password: password,
        UserAttributes: [
          {
            Name: 'email',
            Value: email
          },
          {
            Name: 'name',
            Value: name
          }
        ]
      },
      {
        headers: {
          'X-Amz-Target': 'AWSCognitoIdentityProviderService.SignUp',
          'Content-Type': 'application/x-amz-json-1.1'
        }
      }
    )

    return response.data
  },

  async refreshToken(refreshToken) {
    const response = await axios.post(
      `https://cognito-idp.${REGION}.amazonaws.com/`,
      {
        AuthFlow: 'REFRESH_TOKEN_AUTH',
        ClientId: CLIENT_ID,
        AuthParameters: {
          REFRESH_TOKEN: refreshToken
        }
      },
      {
        headers: {
          'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
          'Content-Type': 'application/x-amz-json-1.1'
        }
      }
    )

    return response.data.AuthenticationResult
  },

  async forgotPassword(email) {
    const response = await axios.post(
      `https://cognito-idp.${REGION}.amazonaws.com/`,
      {
        ClientId: CLIENT_ID,
        Username: email
      },
      {
        headers: {
          'X-Amz-Target': 'AWSCognitoIdentityProviderService.ForgotPassword',
          'Content-Type': 'application/x-amz-json-1.1'
        }
      }
    )

    return response.data
  }
}
