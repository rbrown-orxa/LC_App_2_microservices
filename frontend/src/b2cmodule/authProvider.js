import { MsalAuthProvider, LoginType } from "react-aad-msal";
const tenant = "derapp.onmicrosoft.com";
const signInPolicy = "B2C_1_sign_up_sign_in";
const applicationID = "b249bf9e-9569-4c14-b12a-46b2563b2090";
// const reactRedirectUri = "https://lcapp.orxa.io/b2c";
//const reactRedirectUri = "http://localhost:3000/b2c";
const reactRedirectUri = "https://lcappv2test.azurewebsites.net/b2c";
const tenantSubdomain = tenant.split(".")[0];
const instance = `https://${tenantSubdomain}.b2clogin.com/tfp/`;
const signInAuthority = `${instance}${tenant}/${signInPolicy}`;
// Msal Configurations
const signInConfig = {
  auth: {
    authority: signInAuthority,
    clientId: applicationID,
    redirectUri: reactRedirectUri,
    validateAuthority: false,
    // postLogoutRedirectUri: "https://lcapp.orxa.io/",
    //postLogoutRedirectUri: "http://localhost:3000/",
    postLogoutRedirectUri: "https://lcappv2test.azurewebsites.net/",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: true
  }
};
// Authentication Parameters
const authenticationParameters = {
  scopes: [
    "https://graph.microsoft.com/Directory.Read.All",
    "https://derapp.onmicrosoft.com/apirjs/demo.read"
  ]
};
// Options
const options = {
  loginType: LoginType.Redirect,
  tokenRefreshUri: window.location.origin + "/auth.html",
  persistLoginPastSession: true
};


export const signInAuthProviderB2C = new MsalAuthProvider(
  signInConfig,
  authenticationParameters,
  options
);