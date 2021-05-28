import React from 'react'
// import logo from '../img/ORXA_Logo_Wordmark.png';
// import questionIcon from '../img/questionmark.png';
import Nav from './Nav';

export default function Header(props){
  let {isSolarFormPage,togglerStyleClass,navStyle} = props;
    return(
      <div>
        <header className="App-header">
        <span>
          <Nav togglerStyleClass={togglerStyleClass} isSolarFormPage={isSolarFormPage} navStyle={navStyle} 
                logout={props.logout} accountInfo={props.accountInfo}
          />
        </span>
    </header>
    </div>
    );
}