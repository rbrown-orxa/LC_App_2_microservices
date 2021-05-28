import React, { Component } from 'react';
// import {GoogleMap,withScriptjs,withGoogleMap,Marker,InfoWindow,handleLocationError} from 'react-google-maps';
import WrappedMap from './WrappedMap';
// import Geocode from 'react-geocode';
// Geocode.setApiKey('AIzaSyCdXNN5iv5yl77PGwZpG5GPjZk_epT_U5Y');
// source : https://www.youtube.com/watch?v=Pf7g32CwX_s&t=341s
export default class ReactGoogleMap extends Component {


    constructor(props){
        super(props);
        this.state={
          searchedLatLng : {}

        }

    }

    componentWillReceiveProps(nextProps){
      this.setState({
        searchedLatLng:nextProps.selectedLatLng,
      })

    }

    render() {
        return (
          <div  style={{width:'inherit', height:'50vh',opacity:0.95}}>
              <WrappedMap 
              googleMapURL="https://maps.googleapis.com/maps/api/js?key=AIzaSyCdXNN5iv5yl77PGwZpG5GPjZk_epT_U5Y&callback=initMap" 
              loadingElement={<div style={{height:'100%'}} />}
              containerElement={<div style={{height:'100%'}} />}
              mapElement={<div style={{height:'100%'}} />}
              selectedLatLng={this.state.searchedLatLng}
              handleNextClick={this.props.handleNextClick}
              />
          </div>
        );
    }
}

// function Map(){

//   return (<GoogleMap 
//           defaultZoom={10} 
//           defaultCenter={{lat:51.507351,lng:-0.127758}} // London
//           defaultOptions={{styles:mapStyles}}
//           onClick={ handleMapClick
//             // (event)=>{ //console.log(event.latLng.lat(),event.latLng.lng())
//                             // this.setState({markerPos: {lat:event.latLng.lat(),
//                             //                           lng:event.latLng.lng(),}
//                             //       }
//                             //   );
//           // }
//           }
//           >
//             {/* <Marker position={{lat:51.507351,lng:-0.127758}} /> */}
//             {/* <Marker position={{lat:state.markerPos.lat,lng:state.markerPos.lng}} /> */}
//           </GoogleMap>);

// }

// const WrappedMap = withScriptjs(withGoogleMap(Map));

