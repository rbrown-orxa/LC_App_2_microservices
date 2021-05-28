import { MsalAuthProvider, LoginType } from "react-aad-msal";
import { Logger, LogLevel } from "msal";
// const tenantid = "f0e8a3c1-f57f-446b-b105-37b6d1ee94cc";
//const signInPolicy = "B2C_1_sign_up_sign_in";
const applicationID = "454f560c-4e04-46dc-bb7d-a74f753f3952";
// const reactRedirectUri = "https://lcapp.orxa.io/ad";
//const reactRedirectUri = "http://localhost:3000/ad";
const reactRedirectUri = "https://lcappv2test.azurewebsites.net/ad";
// const tenantSubdomain = tenant.split(".")[0];
// const instance = `https://${tenantSubdomain}.b2clogin.com/tfp/`;
//const signInAuthority = `https://login.microsoftonline.com/${tenantid}`;
const signInAuthority = `https://login.microsoftonline.com/common`;
// Msal Configurations
const signInConfig = {
  auth: {
    authority: signInAuthority,
    clientId: applicationID,
    redirectUri: reactRedirectUri,
    validateAuthority: true,
    // postLogoutRedirectUri: "https://lcapp.orxa.io/",
    //postLogoutRedirectUri: "http://localhost:3000/",
    postLogoutRedirectUri: "https://lcappv2test.azurewebsites.net/",
    navigateToLoginRequestUrl: true,
  },
  system: {
    logger: new Logger(
      (logLevel, message, containsPii) => {
        console.log("[MSAL]", message);
      },
      {
        level: LogLevel.Verbose,
        piiLoggingEnabled: true
      }
    )
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: true
  }
};
// Authentication Parameters
const authenticationParameters = {
  scopes: [
    `${applicationID}/.default`
  ]
};

export const authenticationParametersGraph = {
  scopes: [
  'openid'
  ]
};

// Options
const options = {
  loginType: LoginType.Popup,
  tokenRefreshUri: window.location.origin + "/auth.html",
  persistLoginPastSession: true
};


export const signInAuthProviderAD = new MsalAuthProvider(
  signInConfig,
  authenticationParameters,
  options
);