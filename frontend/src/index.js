import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import Footer from './components/Footer';
import logo from './img/ORXA_Logo_Wordmark.png';
import emoji from './img/googledogfaceemoji.png';
import * as serviceWorker from './serviceWorker';
//import HomePage from './components/HomePage';
// import {BrowserRouter as Router, Switch, Route} from 'react-router-dom';
import {AzureAD, AuthenticationState} from "react-aad-msal";
import { signInAuthProviderB2C} from "./b2cmodule/authProvider";
import { signInAuthProviderAD} from "./admodule/authProvider";
let isAuthRequired=false;
let signInAuthProvider;

// console.log(isAuthRequired)

if (window.location.href.includes('/b2c')) {
  signInAuthProvider=signInAuthProviderB2C
}
else if (window.location.href.includes('/ad')){
   signInAuthProvider=signInAuthProviderAD
  }
    else{
      isAuthRequired=false
    }

isAuthRequired
?
ReactDOM.render(
  <AzureAD provider={signInAuthProvider} forceLogin={true}>
    {
    ({login, logout, authenticationState, error, accountInfo}) => {
      // console.log('authenticationState',authenticationState)
      switch (authenticationState) {
        case AuthenticationState.Authenticated:
          return (
            <p>

            <React.Fragment>
              <App
                accountInfo={accountInfo} logout={logout}
                />
            </React.Fragment>
            </p>

          );
        case AuthenticationState.Unauthenticated:
          return (
            <div>
              {error && <p><span>An error occurred during authentication, please try again!</span></p>}
              <p>
                <span>Hey stranger, you look new!</span>
                <button onClick={login}>Login</button>
              </p>
            </div>
          );
        case AuthenticationState.InProgress:
          return (<p>Authenticating...</p>);

        default:
          return (<p>Loading...</p>);

       }
     }
    }
      </AzureAD>,
document.getElementById('root')
      )
      :

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

