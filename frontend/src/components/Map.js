import React, { Component } from 'react';
import mapStyles from "./mapStyles";
// import {GoogleMap,withScriptjs,withGoogleMap,Marker,InfoWindow,handleLocationError} from 'react-google-maps';
import {GoogleMap,Marker} from 'react-google-maps';
import Geocode from 'react-geocode';
Geocode.setApiKey("AIzaSyCdXNN5iv5yl77PGwZpG5GPjZk_epT_U5Y");
const defaultMapOptions = {
  // fullscreenControl: false,
  // zoomControlOptions:false,
  styles:mapStyles,
  // streetViewControl: false,
  maxZoom:19,
  disableDefaultUI: true,
  defaultZoom:16
};
export default class Map extends Component{

  constructor(props){
    super(props);
    this.state={
      position : {},//{lat:51.507351,lng:-0.127758},
      initialPosition : {lat:51.507351,lng:-0.127758},
    }

    this.handleMapClick = this.handleMapClick.bind(this);

  }

  componentWillReceiveProps(nextProps){
    // //console.log('Map CWRP',nextProps.selectedLatLng)
    if(nextProps.selectedLatLng===undefined) return
    this.setState({
      position:nextProps.selectedLatLng
    });
    let map  = this._map ;
    let bounds  = new window.google.maps.LatLngBounds();
    let loc = new window.google.maps.LatLng(nextProps.selectedLatLng.lat, nextProps.selectedLatLng.lng);
    bounds.extend(loc)
    // //console.log('boundscenter',bounds)
    map.fitBounds(bounds); //      # auto-zoom
    map.panToBounds(bounds);
    document.getElementById('latitude').value=nextProps.selectedLatLng.lat;
    document.getElementById('longitude').value=nextProps.selectedLatLng.lng;
  }

  componentDidMount(){
    navigator.geolocation.getCurrentPosition((position)=>{
      // //console.log('position',position.coords.latitude,position.coords.longitude);
      // //console.log('state',this.state)
      this.setState({ initialPosition:{ lat:position.coords.latitude,
                                        lng:position.coords.longitude,
                                      }
      })
      Geocode.fromLatLng(position.coords.latitude,position.coords.longitude).then(
        response => {
          const address = response.results[0].formatted_address;
          //console.log('auto address',address);
          document.getElementById('pac-input').value=address;
          let map  = this._map ;
          let bounds  = new window.google.maps.LatLngBounds();
          let loc = new window.google.maps.LatLng(position.coords.latitude, position.coords.longitude);
          bounds.extend(loc)
          map.fitBounds(bounds); //      # auto-zoom
          map.panToBounds(bounds);
          document.getElementById('latitude').value=position.coords.latitude;
          document.getElementById('longitude').value=position.coords.longitude;
        },
        error => {
          console.error(error);
        });
    });
    //console.log('initialPosition',this.state.initialPosition)

  }

  handleMapClick(event){
    // //console.log(event.latLng.lat(),event.latLng.lng())
    // //console.log('geocoder',Geocode)

    //console.log('handlemapclick',this.props,event.latLng.lat(),event.latLng.lng())
    Geocode.fromLatLng(event.latLng.lat(), event.latLng.lng()).then(
      response => {
        const address = response.results[0].formatted_address;
        //console.log(address);
        document.getElementById('pac-input').value=address;
        document.getElementById('latitude').value=event.latLng.lat();
        document.getElementById('longitude').value=event.latLng.lng();
        // let sideDetailsNextButton = document.getElementById('sideDetailsNextButton');
        // sideDetailsNextButton.disabled=false;
        // sideDetailsNextButton.addEventListener('click',this.props.handleNextClick);
        //console.log('handlemapclick',sideDetailsNextButton,this.props)

        let map  = this._map ;
        let bounds  = new window.google.maps.LatLngBounds();
        let loc = new window.google.maps.LatLng(event.latLng.lat(), event.latLng.lng());
        bounds.extend(loc)
        // //console.log('boundscenter onmapclick',bounds)
        map.fitBounds(bounds); //      # auto-zoom
        map.panToBounds(bounds);
        map.getHeading();
        // this.props.handleChangeLatLngFromMap(event.LatLng)
        // let nextButton = document.getElementById('sideDetailsNextButton');
        // nextButton.disabled=false;
      },
      error => {
        console.error(error);
      }
    );

    this.setState({
      position:{ lat:event.latLng.lat(),lng:event.latLng.lng() }
    });
    this.forceUpdate();
  }
  
  
  render(){
  let {position,initialPosition} = this.state;
  // let {initialPosition,} = this.state;
  return (<GoogleMap 
          defaultZoom={10} 
          // center={position!==undefined?position:initialPosition}
          defaultCenter={initialPosition}
          // defaultCenter={{lat:initialPosition.lat,lng:initialPosition.lng}} // London
          defaultOptions={defaultMapOptions}
          onClick={ this.handleMapClick }
          ref={(map) => this._map = map}
          mapTypeId = {window.google.maps.MapTypeId.HYBRID}
          
          >
            {
            position!==undefined ? <Marker  position={{lat:parseFloat(position.lat),lng:parseFloat(position.lng) }} /> : ''
            } 
            
            {/* <Marker position={{lat:state.markerPos.lat,lng:state.markerPos.lng}} /> */}
          </GoogleMap>);

}

}