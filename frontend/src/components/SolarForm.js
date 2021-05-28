import React,{Component} from 'react';
import ResultsPage from './ResultsPage';
import StartSitePage from './StartSitePage';
import LocationDetailsPage from './LocationDetailsPage';
import UtilityPage from './UtilityPage';
import PlannedInstallationPage from './PlannedInstallationPage';
import axios from 'axios';
import {GENERIC_API_URL} from '../common/constants'
import SpinnerIcon from '../img/Ripple.gif';
//import test_result from './test_result.json' // testing only

export default class SolarForm extends Component{

    constructor(props){
        super(props);
        this.state={
          step:1,
          maxReachedStep:0,
          address:'',
          sub:' ',//'bfb2f43c-38c0-4cd4-b35e-246e8236e29d',
          oid:' ',//'bfb2f43c-38c0-4cd4-b35e-246e8236e29d',
          sub_id:' ',//'f6219eaa-7789-7762-7afe-1826d6bdfe54',
          plan_id:null,
          jwtIdToken:'',//'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ilg1ZVhrNHh5b2pORnVtMWtsMll0djhkbE5QNC1jNTdkTzZRR1RWQndhTmsifQ.eyJpc3MiOiJodHRwczovL2RlcmFwcC5iMmNsb2dpbi5jb20vNmIwYzlmYTYtODBmMS00NzA2LTg3ZmUtMzliNWI4NDZhYjY3L3YyLjAvIiwiZXhwIjoxNjA0MDY4OTUyLCJuYmYiOjE2MDQwNjUzNTIsImF1ZCI6ImIyNDliZjllLTk1NjktNGMxNC1iMTJhLTQ2YjI1NjNiMjA5MCIsImlkcCI6ImxpbmtlZGluLmNvbSIsIm5hbWUiOiJIYXJpc2ggSXllciIsIm9pZCI6ImRhODQ1MDdhLWRhMWUtNDgzYy1iNGExLWJkOTEzYzA3ZGIwYiIsInN1YiI6ImRhODQ1MDdhLWRhMWUtNDgzYy1iNGExLWJkOTEzYzA3ZGIwYiIsImVtYWlscyI6WyJoYXJpc2gub2lzdEBnbWFpbC5jb20iXSwidGZwIjoiQjJDXzFfc2lnbl91cF9zaWduX2luIiwic2NwIjoiZGVtby5yZWFkIiwiYXpwIjoiYjI0OWJmOWUtOTU2OS00YzE0LWIxMmEtNDZiMjU2M2IyMDkwIiwidmVyIjoiMS4wIiwiaWF0IjoxNjA0MDY1MzUyfQ.BUZWYUhNeSC7FhFaFxeDorirwPKzT4Vy42-RfIAlawwtoo7m5bTCSq4C08hnR9zCdAk0a14CF6dYG70ekXgKYYhK1oZjqwehUcyamhqbefkzfuPkeWYyGWzY7yzlRz4dysKEyb8lQSSL6S7ikHum8bQiwYQmP9t16vAGvbUY62BQv6nMTP234WMS8vKLxAAW3eY39uEYQcaXG7gveU89H8u3JpacOLosB7a9lVYWBU5BWITXfgJQTeGLorSVnf5hIzuAANBLyhMjrNuFhrG34Oe8_tJjlRNBhHrKR8qtpqMesSMh47G7uhBa-hgLfxmcb9efRh51bowEK4f8SEVIeA',
          isCompassVisible:true,
          building_data:[],
          results:{},//test_result,
          firstName: 'John',
          resolveApiResponseStatus:'',
          resolveApiError: '',
          isLoadingResults:false,
        };      
        this.updateBuildingsData = this.updateBuildingsData.bind(this);
        this.handleSubNavigation = this.handleSubNavigation.bind(this);
        this.validateAnnualConsumptionOrBldgDemand = this.validateAnnualConsumptionOrBldgDemand.bind(this);
        // this.resolveUserInfo=this.resolveUserInfo.bind(this);
    }

    
    componentWillMount(){
      let {accountInfo} = this.props;
      let firstName=' ';
      let sub=' ';
      let oid=' ';
      let jwtIdToken='';
      if(accountInfo!==undefined && accountInfo.account!==undefined){
        if(accountInfo.account.name!==undefined)
        firstName=accountInfo.account.name.split(' ')[0];
        jwtIdToken=accountInfo.jwtIdToken;
        sub=accountInfo.account.idToken.sub;
        oid=accountInfo.account.idToken.oid;
        setTimeout(  
        this.resolveUserInfo(jwtIdToken)
        ,3000);
      
      }
      this.setState({accountInfo:accountInfo,
        firstName:firstName,
        jwtIdToken:jwtIdToken,
        sub:sub,
        oid:oid,

      });
      
      
    }

    componentDidMount(){
    }

    componentDidUpdate(){
      if(this.state.step>0 && this.state.step < 4){
        setTimeout(()=>{
        let AppHeader = document.getElementsByClassName('App-header')[0];
        AppHeader.style.background='white';
        // let AppMenu = document.getElementById('menu1');
        // AppMenu.style.color='#2B2B2B';
        },500);
      }else{
        setTimeout(()=>{
          let AppHeader = document.getElementsByClassName('App-header')[0];
          AppHeader.style.background='transparent';
          // let AppMenu = document.getElementById('menu1');
          // AppMenu.style.color='white';
          },500);
          console.log('cdu solar form props',this.props)
      }
    }

    async resolveUserInfo(jwtIdToken){
      let sub_id=null;
      let plan_id=null;
      let free_calls=0;
      let max_free_calls=0;
      let resolveApiError= '';
      let resolveApiResponseStatus=0;
      let headers = {
        'authorization': 'Bearer ' + jwtIdToken,
      };
        await axios.post(GENERIC_API_URL+'resolve', {}, {headers:headers})
        .then(function (response) {
            //handle success
            console.log('resolve response',response,response.data);
            resolveApiResponseStatus=response.status;
            if(response.data!==undefined){
              free_calls=response.data.free_calls;
              max_free_calls=response.data.max_free_calls;
              sub_id=response.data.subscription_id;
              plan_id=response.data.plan_id;
            }
  
          })
          .catch(function (error) {
            //handle error
            console.log('ressolve response err',error,error.response.status,error.response.data.error);   
            resolveApiResponseStatus=error.response.status;
            resolveApiError=error.response.data.error;
          });   

          if(resolveApiResponseStatus===200){
            this.setState({
              free_calls:free_calls,
              max_free_calls:max_free_calls,
              sub_id:sub_id,
              plan_id:plan_id,
              resolveApiResponse:true,
              resolveApiResponseStatus:resolveApiResponseStatus,
            });    
          } else {
            this.setState({
              resolveApiResponseStatus:resolveApiResponseStatus,
              resolveApiError:resolveApiError,
              free_calls:free_calls,
              max_free_calls:max_free_calls,
              sub_id:sub_id,
              plan_id:plan_id,
            });  
          }

    }

    validateAnnualConsumptionOrBldgDemand(){
      let {building_data} = this.state;
      console.log('validateAnnualConsumptionOrBldgDemand',building_data)
      for(let i=0;i<building_data.length;++i){
          if(building_data[i].annual_kwh_consumption_optional || building_data[i].load_profile_csv_optional_bldg){
              continue;
          }else {
              alert('Please select annual consumption or demand file for building '+building_data[i].building_name);
              return false;
          }
      }
      return true
  }

    nextStep = () => {
      // alert('got here')
      // alert(window)
      // console.log('window: ', window._env_)
      console.log('GENERIC_API_URL: ', GENERIC_API_URL)
      // alert('done')
      const {step} = this.state;
      let {maxReachedStep} = this.state;
      if(maxReachedStep<step) maxReachedStep=step;
      if(step===2){
        if(!this.validateAnnualConsumptionOrBldgDemand()){
          return;
        }
      }
      this.setState({
        step : step + 1,
        address:'',
        maxReachedStep:maxReachedStep,
      });
    }
  
    prevStep = () => {
      const {step} = this.state;
      if (this.state.step === 1) { //Don't go back lower than step 1
        this.setState({
                step : 1,
                errorObj:undefined,
              })
      }
      else {
        this.setState({
          step : step - 1,
          errorObj:undefined,
        })

      }
    }

  
    handleChange = input => {
      // //console.log('solarPVForm handlechange',input)
      let inputEle = document.getElementById(input)
      // //console.log('found',inputEle)
      if(inputEle !== null){
        // //console.log('inputEle',inputEle.value)
        this.setState({
            [input]:inputEle.value,
        });
      }
    }

    updateBuildingsData(buildings){
      console.log('form updateBuildingsdata',buildings,this.state)
      if(this.state===undefined) return;
      console.log('form updateBuildingsData buildings only',buildings)
      let {building_data} = this.state;
      building_data=buildings;
      this.setState({building_data:building_data});
      console.log('form bldg updated',buildings,this.state)
    }

    submitAction = async() => {
      console.log('submit Action',this.state)
      // let {accountInfo} = this.state;
      // let jwtIdToken =  accountInfo.jwtIdToken;
      // let subid = accountInfo.account.idToken.sub;
      // let objid = accountInfo.account.idToken.oid;
      let {step,sub,oid,sub_id,plan_id,jwtIdToken}=this.state;
      let {latitude,longitude, import_cost_kwh,export_price_kwh,pv_cost_kwp,pv_life_yrs,
      battery_life_cycles,battery_cost_kwh,load_profile_csv_optional,building_data} = this.state;
      this.setState({isLoadingResults:true});  
      let building_data_formatted = [];
      for(let i=0;i<building_data.length;++i){
        console.log('building_data[i].num_ev_chargers,',building_data[i].num_ev_chargers,)
        let buildingItem ={
          name:building_data[i].building_name,
          building_type: building_data[i].building_type,
          roof_size_m2: parseInt(building_data[i].roof_size_m2),
          azimuth_deg: parseInt(building_data[i].azimuth_deg),
          pitch_deg: parseInt(building_data[i].pitch_deg),
          num_ev_chargers: building_data[i].num_ev_chargers!==undefined?parseInt(building_data[i].num_ev_chargers):0,
          pv_size_kwp_optional: building_data[i].pv_size_kwp_optional!==undefined?parseFloat(building_data[i].pv_size_kwp_optional):1,
          load_profile_csv_optional: building_data[i].load_profile_csv_optional_bldg!==undefined?building_data[i].load_profile_csv_optional_bldg:'',
          annual_kwh_consumption_optional: building_data[i].annual_kwh_consumption_optional!==undefined?parseFloat(building_data[i].annual_kwh_consumption_optional):2400
        }
        building_data_formatted.push(buildingItem);
      }
      // console.log('bat',battery_cost_kwh,battery_cost_kwh!==null,battery_cost_kwh!==null?parseInt(battery_cost_kwh):407)
      let bodyFormData = {
        "sub":sub,
        "oid":oid,
        "sub_id":sub_id,
        "plan_id":plan_id,        
        "lat":parseFloat(latitude),
        "lon":parseFloat(longitude),
        "import_cost_kwh":parseFloat(import_cost_kwh),
        "export_price_kwh":parseFloat(export_price_kwh),
        "pv_cost_kwp":parseInt(pv_cost_kwp!==undefined?pv_cost_kwp:1840),
        "pv_life_yrs":parseInt(pv_life_yrs!==undefined?pv_life_yrs:20),
        "battery_life_cycles":battery_life_cycles!==undefined?parseInt(battery_life_cycles):6000,
        "battery_cost_kwh":battery_cost_kwh!==undefined?parseInt(battery_cost_kwh):407,
        "load_profile_csv_optional":load_profile_csv_optional,
        "building_data":building_data_formatted
      };
      let headers = {
        'authorization': 'Bearer ' + jwtIdToken,
      };
  
      let results,charts,errorObj;
      let redirect_url = ''
      console.log('GENERIC_API_URL axios.post:', GENERIC_API_URL+'task_optimise')
      await axios.post(GENERIC_API_URL+'task_optimise', bodyFormData, {headers:headers})
        .then(function (response) {
            console.log('optimise status code:', response.status)
            console.log('202 response?', response.status === 202)
            console.log('optimize response',response,response.data);
            if(response.status === 202){
              redirect_url = GENERIC_API_URL+response.data.Location
            }else{
              results='Oops! Something went wrong! we\'ll analyze it soon'
            }

          })
          .catch(function (error) {
            console.log('submit response err',error,error.response);//,error.response.status,error.response.data.error);
            if(error.response!==undefined){
            errorObj = {errorStep:step,status: error.response.status,message:error.response.data.error};
            if(errorObj.status === 402){
                alert('You have not subscribed to our app. You will be redirected to Azure market place in order to subscribe to our app. Click Ok button!!!');
                // window.location.href = "https://azuremarketplace.microsoft.com/en-us/marketplace/apps/orxagrid1584097142796.lcappv2?tab=Overview";
              }
            } else{
              errorObj = {errorStep:step,status: 500,message:error.response}
            }
          });   


          console.log('redirect_url: ', redirect_url)
          let success = false
          let i = 0
          while (!success){
            await this.timeout(1000); //for 1 sec delay
            i++
            await axios.get(redirect_url).then(function(res){
              console.log('res:', res)
              console.log('i: ', i)
              if (res.status === 200){
                success = true
                results=res.data.results;
                charts=res.data.charts;
                step = step + 1;                
              }
            })
          }


          console.log('setting results state')
          this.setState({
            step : step,
            results:results,
            charts:charts,
            isLoadingResults:false,
            errorObj:errorObj,
          });
          // console.log('state after submit',this.state.step,this.state.results)
    }
    
    timeout(delay: number) {
        return new Promise( res => setTimeout(res, delay) );
    }

    handleSubNavigation(stepName){
      switch(stepName){
        case 'Location':
          this.setState({step:1});
        break;
        case 'Utility':
          this.setState({step:2});
        break;
        case 'Installation':
          this.setState({step:3});
        break;
        default:
          this.setState({step:0});
        break;  
      }
    }

    render(){
        let {step,isLoadingResults,maxReachedStep} = this.state; 
        console.log('form state',this.state)
        switch(step){
          case 0:
            return(<div class="container">
                      <StartSitePage
                      firstName={this.state.firstName}
                      plan_id={this.state.plan_id}
                      max_free_calls={this.state.max_free_calls}
                      free_calls={this.state.max_free_calls-this.state.free_calls}
                      resolveApiResponseStatus={this.state.resolveApiResponseStatus}
                      resolveApiError={this.state.resolveApiError}
                      nextStep={this.nextStep}
                      />
                  </div>
                  );
            // break;
          case 1:
            return(<div class="jumbotron" style={{background:'white',height:'auto',borderTop:'2px solid #4DA858'}}>
                      <div class='FormNavigation'>
                      {/* <img src={homePageImg} style={{width:'24px'}} /> /  */}
                          <span className='formSubMenu' ><b> Location</b></span> / 
                          <span className='formSubMenu' onClick={(e)=> {if(maxReachedStep>=1) this.handleSubNavigation('Utility') }}>Utility</span> / 
                          <span className='formSubMenu' onClick={(e)=>{ if(maxReachedStep>=2) this.handleSubNavigation('Installation')}}>Installation</span>
                      </div>
                      <LocationDetailsPage 
                        address = {this.state['pac-input']}
                        building_data={this.state.building_data}
                        max_free_calls={this.state.max_free_calls}
                        free_calls={this.state.free_calls}
                        resolveApiResponseStatus={this.state.resolveApiResponseStatus}
                        resolveApiError={this.state.resolveApiError}
                        prevStep={this.prevStep}
                        nextStep={this.nextStep}
                        handleChangeInput={this.handleChange}
                        sendBuildingsDataToForm={this.updateBuildingsData}
                      />
                    </div>);
            //break;
          case 2: 
            return(<div class="jumbotron" style={{background:'white',height:'auto',borderTop:'2px solid #4DA858'}}>
                        <div class='FormNavigation'>
                        {/* <img src={homePageImg} style={{width:'24px'}} /> /  */}
                            <span className='formSubMenu' onClick={(e)=>this.handleSubNavigation('Location')}>Location</span> / 
                            <span className='formSubMenu' ><b>Utility</b></span> / 
                            <span className='formSubMenu' onClick={(e)=>{if(maxReachedStep>=2) this.handleSubNavigation('Installation')}}>Installation</span>
                        </div>
                        <UtilityPage 
                          address = {this.state['pac-input']}
                          building_data={this.state.building_data}
                          latitude = {this.state.latitude}
                          longitude = {this.state.longitude}
                          import_cost_kwh={this.state.import_cost_kwh}
                          export_price_kwh={this.state.export_price_kwh}
                          load_profile_csv_optional={this.state.load_profile_csv_optional}
                          load_profile_csv_optional_site_fname={this.state.load_profile_csv_optional_site_fname}
                          max_free_calls={this.state.max_free_calls}
                          free_calls={this.state.free_calls}
                          resolveApiResponseStatus={this.state.resolveApiResponseStatus}
                          resolveApiError={this.state.resolveApiError}
                          prevStep={this.prevStep}
                          nextStep={this.nextStep}
                          handleChangeInput={this.handleChange}
                          sendBuildingsDataToForm={this.updateBuildingsData}
                        />
                      </div>);
            // break;
            case 3: 
            return(<div class="jumbotron" style={{background:'white',height:'auto',borderTop:'2px solid #4DA858'}}>
                        <div class='FormNavigation' >
                        {/* <img src={homePageImg} style={{width:'24px'}} /> /  */}
                            <span className='formSubMenu' onClick={(e)=>this.handleSubNavigation('Location')}>Location</span> / 
                            <span className='formSubMenu' onClick={(e)=>this.handleSubNavigation('Utility')}>Utility</span> / 
                            <span className='formSubMenu' ><b>Installation</b></span>
                        </div>            
                        <div class="spinner" style={{ display:isLoadingResults?'block':'none'}}>
                            <img src={SpinnerIcon} style={{width:'12.5vw',}} alt='' />
                        </div> 
                        <PlannedInstallationPage 
                          address={this.state['pac-input']}
                          building_data={this.state.building_data}
                          pv_life_yrs={this.state.pv_life_yrs}
                          pv_cost_kwp={this.state.pv_cost_kwp}
                          battery_life_cycles={this.state.battery_life_cycles}
                          battery_cost_kwh={this.state.battery_cost_kwh}
                          max_free_calls={this.state.max_free_calls}
                          free_calls={this.state.free_calls}
                          resolveApiResponseStatus={this.state.resolveApiResponseStatus}
                          resolveApiError={this.state.resolveApiError}
                          prevStep={this.prevStep}
                          nextStep={this.nextStep}
                          handleChangeInput={this.handleChange}
                          sendBuildingsDataToForm={this.updateBuildingsData}
                          submitAction={this.submitAction}
                        />
                      </div>);
            //break;
            // case 4: 
            // return(<div class="jumbotron" style={{background:'white',height:'auto',borderTop:'2px solid #4EA758'}}>
            //           <SiteSummaryPage
            //               address={this.state['pac-input']}
            //               building_data={this.state.building_data}
            //               sendBuildingsDataToForm={this.updateBuildingsData}
            //               nextStep={this.nextStep}
            //               prevStep={this.prevStep}
            //               submitAction={this.submitAction}
            //           />
            // </div>

            // );
            //break;
            case 4: 
            return(
              <div   //style={{background:'white',marginLeft:'250px',width:'85%',height:'auto',borderTop:'2px solid #4EA758'}}
              > 
                <ResultsPage
                results={this.state.results}//{test_result}//{this.state.results}
                charts={this.state.charts}
                prevStep={this.prevStep}
                />
              </div>
              )
            //break;
          default:
            return(<div class="jumbotron" style={{background:'white',height:'auto',borderTop:'2px solid #4EA758'}}>
                       404 Page Not Found. Please contact Administrator
                      </div>);

            //break;  
        }

       
    }

}