import React,{Component} from 'react';
import '../App.css';
// import userIcon from '../img/usericon.png';
// import userIconDark from '../img/usericon_dark.png';
import logo from '../img/ORXA_Logo_Wordmark.png';

import {Link} from 'react-router-dom';

import {COMPANY_LOGO_URL} from '../common/constants'
import {COMPANY_WEBSITE_URL} from '../common/constants'


// let _logo = 'https://1000logos.net/wp-content/uploads/2021/05/Google-logo-500x281.png'
let _logo = COMPANY_LOGO_URL
let _logo_url = COMPANY_WEBSITE_URL


class Nav extends Component{

  constructor(props){
    super(props);
    this.state={
      togglerStyleClass:' navbar-dark',
      isSolarFormPage:false,

    };
    // this.setMenuStyle = this.setMenuStyle.bind(this);
  }

  // setMenuStyle(){
  //   const location = window.location.href;//useLocation();
  //   //console.log('location',location);
  //   if(location.includes('SolarPVForm')){
  //     this.setState({
  //       isSolarFormPage:true,
  //       togglerStyleClass:' navbar-light',
  //       navStyle:{color:'#2B2B2B',textDecoration:'none'}
  //     });
  //   }else{
  //     this.setState({togglerStyleClass:' navbar-dark',
  //                   isSolarFormPage:false,
  //                   navStyle:{color:'white',textDecoration:'none'}});
  //   }
  // }

  componentWillMount(){

  }

  componentWillReceiveProps(nextProps){

  }

  render(){
    let {togglerStyleClass}= this.props;
    let navStyle={color:'white',textDecoration:'none',position:'absolute',right:'20px'}
    if(window.location.href.includes('/b2c')||window.location.href.includes('/ad')||window.location.href.includes('/SolarPVForm')){
      togglerStyleClass=' navbar-light';
    }
    let isLoggedIn = !(this.props.logout===undefined)
    console.log('nav props',this.props.accountInfo)
    let firstName='Bob';
    if(this.props.accountInfo!==undefined && this.props.accountInfo.account!==undefined){
      if(this.props.accountInfo.account.name!==undefined)
      firstName=this.props.accountInfo.account.name.split(' ')[0];
    }
    return (
      <nav className={"navbar navbar-expand-lg"+togglerStyleClass} >

      <a  
      rel="noopener noreferrer" 
      style={{alignContent:'left'}} 
      href={_logo_url} 
      target="_blank"
      >
      <img src={_logo} 
      style={{height:'10vh',marginRight:'40px'}} 
      className="logo" alt="OrxaGrid"/>
      </a>

      <button className="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon">
          </span>
      </button>
      <span className="collapse navbar-collapse" id="navbarSupportedContent">
        <ul className="navbar-nav mr-auto nav-links"> 
        {/* <a href='http://localhost:3000/'><li className="nav-item nav-link"><Link id='menu1' style={{...navStyle,marginRight:'50vw'}} >Home</Link></li>    </a> */}
            {/* <li className="nav-item nav-link"><Link style={navStyle} to='/'>Low Carbon App</Link></li>     */}
            {/* <li className="nav-item nav-link"><Link style={{...navStyle,marginRight:'20vw'}} to='/'>Grid Analytics App</Link></li>     */}
            {/* <li className="nav-item">         */}
              {/* <span > */}
                {/* <img src={isSolarFormPage ? userIconDark : userIcon} style={{width:'40px',padding:'10px',cursor:'pointer'}} /> */}
                {/* <img src={questionIcon} style={{width:'30px',padding:'10px',}} /> */}
              {/* </span> */}
            {/* </li> */}

            {/*}
           {isLoggedIn? 
            <li class="dropdown" style={{fontWeight:'400', fontSize:'16px',position:'absolute',right:'10px',}}>
                <div class="dropdown-toggle nav-links" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="true">
                  <span class="nav-label" > 
                    Hi {firstName}!
                    <span role="img" aria-label='smiley'>&#x1F600;</span>
                    <span class="caret">
                  </span>
                  </span>
                </div>
                <ul class="dropdown-menu" style={{cursor:'pointer',width:'50px',paddingLeft:'5px'}}>
                    <li><div onClick={this.props.logout}>Logout</div></li>
                </ul>
            </li>
            :
            
            <li className="nav-item nav-link"><a style={navStyle} href="https://lcappbeta.orxa.io/">Solar only version</a></li>
            
            }
             */}     

        </ul>
      </span>
    </nav> 
    );
  }

}


export default Nav;
