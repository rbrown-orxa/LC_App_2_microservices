import React,{PureComponent} from 'react';
import PlacesAutocomplete from 'react-places-autocomplete';
import {geocodeByAddress, getLatLng,} from 'react-places-autocomplete';
import locationImg from '../img/location.png';
import ReactGoogleMap from './ReactGoogleMap';
import AnglePicker from './AnglePicker';

export default class SiteDetails extends PureComponent{

    constructor(props){
        super(props);
        this.state={
            address:'',
          };
      
    }

    handleChange = address => {
        this.setState({ address });
      };
    
      handleSelect = address => {
        geocodeByAddress(address)
          .then(results => getLatLng(results[0]))
          .then(latLng => {
              
            //console.log('Success', latLng)
              this.setState({address:address,
                latLng:latLng,
              });
    
              // document.getElementById('latitude').value=latLng.lat;
              // document.getElementById('longitude').value=latLng.lng;
              // this.props.handleChangeInput('pac-input');
              // this.props.handleChangeInput('latitude');
              // this.props.handleChangeInput('longitude');
              // let sideDetailsNextButton = document.getElementById('sideDetailsNextButton');
              // sideDetailsNextButton.disabled=false;
              // sideDetailsNextButton.addEventListener('click',this.handleNextClick);
    
          }
          )
          .catch(error => console.error('Error', error));
      };

    render(){
        let {latLng} = this.state;
        
        return(<div class="container">
        <div class="row">
          <div class="col-md-6 caption" >
            Tell us about your site.
          </div>
          <div class="col-md-6 contents" style={{ borderRadius: (window.innerWidth > 500) ? '25px' : '0px' }}>
            <h4 style={{marginTop:'20px',}}>Location</h4>
            <span>Where would you setup your solar?</span>
          <PlacesAutocomplete
                          value={this.state.address}
                          onChange={this.handleChange}
                          onSelect={this.handleSelect}
                        >
                          {({ getInputProps, suggestions, getSuggestionItemProps, loading }) => (
                            <div>
                              <div id="addressInput" className='col-sm-12' style={{width:'100%',}} >
                              <input id="pac-input" //id="pac-input"
                                    
                                {...getInputProps({
                                  placeholder: 'Enter address here..',
                                  className: 'location-search-input',
                                })}
                              /><span><img src={locationImg} style={{position:'absolute',right:'5px',width:'20px',}} /></span>
                              </div>                        
                              <div className="autocomplete-dropdown-container">
                                {loading && <div>Loading...</div>}
                                {suggestions.map(suggestion => {
                                  const className = suggestion.active
                                    ? 'suggestion-item--active'
                                    : 'suggestion-item';
                                  // inline style for demonstration purpose
                                  const style = suggestion.active
                                    ? { backgroundColor: '#193A55',color:'#fff', cursor: 'pointer' }
                                    : { backgroundColor: '#ffffff', cursor: 'pointer' };
                                  return (
                                    <div
                                      {...getSuggestionItemProps(suggestion, {
                                        className,
                                        style,
                                      })}
                                    >
                                      <span>{suggestion.description}</span>
                                    </div>
                                  );
                                })}
                              </div>                                
                            </div>
                          )}
          </PlacesAutocomplete>
          <input id="latitude" name="latitude" type="text" 
                            defaultValue={latLng!==undefined?latLng.lat:''} 
                            style={{display:'none'}} 
          />
          <input id="longitude" name="longitude" type="text" 
                            defaultValue={latLng!==undefined?latLng.lng:''} 
                            style={{display:'none'}} 
          /> 

          <h4 style={{marginTop:'30px'}}>Roof direction</h4>
          <span>Where would your panels face?
            <input id="azimuth" type="number" style={{marginLeft:'20px',width:'50px'}}/>&deg;
            <br/>
          </span>
          <br/>
          <ReactGoogleMap
                    selectedLatLng={this.state.latLng}
                    handleNextClick={this.handleNextClick}
          />     
          <AnglePicker/>
          <hr/>
            <div class="text-center">
              <button type="button" class="btn btn-primary" onClick={()=>{ let roofDirection= document.getElementById("azimuth").value;
                                                                    this.props.nextStep(this.state.address,roofDirection)                                                                  
                                                                    }}>Calculate</button>
            </div>
          </div>
          
        </div>
      </div>);
    }

}