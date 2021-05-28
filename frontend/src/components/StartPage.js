import React,{Component} from 'react';
import rightArrow from '../img/right_arrow.png';

export default class StartPage extends Component{



    render(){
        //console.log(this.props)
        return(
          <div class="row">
            <div class="col-md-6 caption" >
              Low Carbon Planning
            </div>
            <div class="col-md-6 caption-a" style={{ borderRadius: (window.innerWidth > 500) ? '25px' : '0px' }}>
              Quickly and accurately calculate the optimal installation size of Solar,  Battery Storage or EV charging points. 
            </div>
            <div class="row">
              <div class="col-md-12 caption-a" >
                <br/>

                <a href='/ad'>                
                <img src={rightArrow} alt=''
                    style={{width:'35px',padding:'10px',background:'#4EA758',borderRadius:'50%',}} 
                />
                &nbsp;  
                
                GET STARTED

                </a>

            
              </div>
            </div>
          </div>
            );
    }

}



// <img src={require('../img/microsoft-logo-png-2402.png')} width="180px" alt='' />

// <a href='/b2c'><img src={require('../img/social1.png')} width="180px" alt='' />
// </a>
// {/* <a href='/ad' style={{cursor:'pointer'}}><img src={microsoftlogo} 
//     style={{width:'35px',padding:'10px',background:'#4EA758',borderRadius:'50%',}} 
// /></a>
// <a  href='/b2c' style={{cursor:'pointer'}}><img src={sociallogo} 
//     style={{width:'35px',padding:'10px',background:'#4EA758',borderRadius:'50%',}} 
// /></a> */


