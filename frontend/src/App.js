import React,{PureComponent} from 'react';
import 'bootstrap/dist/css/bootstrap.css';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './components/HomePage';
import SolarForm from './components/SolarForm';
import {BrowserRouter as Router, Switch, Route} from 'react-router-dom';

class App extends PureComponent {

  constructor(props){
    super(props); // depricated ?
    this.state={togglerStyleClass:' navbar-dark',
               isSolarFormPage:false,
              navStyle:{color:'',textDecoration:'none'}
    };
    this.setMenuStyle = this.setMenuStyle.bind(this)
  }

  componentDidMount(){
    this.setMenuStyle();

  }

  render(){      
    let {isSolarFormPage,togglerStyleClass,navStyle} = this.state;
    console.log('app props',this.props)
    let props = this.props;
    return (
        <Router onUpdate={this.setMenuStyle}>
          <div className="App" >
            <Header togglerStyleClass={togglerStyleClass} isSolarFormPage={isSolarFormPage} navStyle={navStyle} 
            logout={this.props.logout} accountInfo={this.props.accountInfo}
            />            
            <Switch>
              <Route path="/" exact component={HomePage} />
              <Route path="/ad" render={(routeProps) => (<SolarForm  {...routeProps}  {...props} />)} />
              <Route path="/b2c" render={(routeProps) => (<SolarForm  {...routeProps}  {...props} />)} />
              {/* <Route path="/SolarPVForm" render={(routeProps) => (<SolarForm  {...routeProps}  {...props} />)} /> */}
              {/* <Route path="/SolarPVForm" component={SolarForm}  /> */}
            </Switch>
          </div>
          <Footer/>
        </Router>
    );
  }

  setMenuStyle(){
    const location = window.location.href;//useLocation();
    //console.log('setMenuStyle location',location);
    if(location.includes('SolarPVForm')){
      this.setState({
        isSolarFormPage:true,
        togglerStyleClass:' navbar-light',
        navStyle:{color:'#2B2B2B',textDecoration:'none'}
      });
    }else{
      this.setState({togglerStyleClass:' navbar-dark',
                    isSolarFormPage:false,
                    navStyle:{color:'white',textDecoration:'none'}});
    }
  }


}

export default App;
