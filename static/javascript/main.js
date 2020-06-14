function showLoading()    {
    document.getElementById("loading").style.display='block';
    document.getElementById("submitBtn").style.visibility='hidden';            
}

function fileChanged() {
    console.log('file changed')
    document.getElementById('uploadedFileName').innerHTML=document.getElementById('file').files[0].name;
}

// Open Source https://github.com/bgrins/ui.anglepicker
// Angle picker
function printDegrees(log, deg) {
    //log.html(deg + '&deg;');
    log.val(deg);
}
// function printGradient(deg) {
//     $("body").css("background-image", "-webkit-linear-gradient("+deg+"deg, #afa, #fff)");
//     $("body").css("background-image", "linear-gradient("+(deg - 90)+"deg, #afa, #fff)");
// }

$(function() {

    $("#anglepicker").anglepicker({
        value: 0,
        clockwise: false,
        change: function(e, ui) {
            //console.log('azmimuth',$(this).parent().find("#azimuth"));
            ui.value = ui.value + 90;
            if(ui.value < 0) {ui.value = ui.value + 360 }
            if(ui.value >= 360) {ui.value = ui.value - 360 }
            printDegrees($("#azimuth"), ui.value);
            //printGradient(ui.value);
        },
        start: function(e, ui) {
            printDegrees($("#azimuth"), ui.value);
            $("em").fadeIn('fast');
        },
        stop: function() {
            $("em").hide();
        }
    });

    $("#anglepicker-counter").anglepicker({
        value: 0,
        clockwise: true,
        change: function(e, ui) {
            let roofPtr = document.getElementsByClassName('ui-anglepicker-pointer')[1]
            if(ui.value>90 && ui.value<240) {
                //console.log(ui.value,' greater than 90')
                printDegrees($(this).parent().find("#roofpitch"), 90); 
                // console.log('pointer',roofPtr);
                roofPtr.style.display='none';
                return; 
            }else if(ui.value>240 && ui.value<360){
                    printDegrees($("#roofpitch"), 0); 
                    roofPtr.style.display='none';
                return; 
            }else{
                roofPtr.style.display='block';
            }
            printDegrees($("#roofpitch"), ui.value);
            //printGradient(ui.value);
        },
        start: function(e, ui) {
            printDegrees($("#roofpitch"), ui.value);
            //console.log('started');
            $("em").fadeIn('fast');
        },
        stop: function(ui) {
            //console.log('stopped');
            // if(ui.value>90) {
            //   $("#anglepicker-counter").anglepicker("value", 90)
            // }
            $("em").hide();
        }
    });

    $("#anglepicker").anglepicker("value", -270);
    $("#anglepicker-counter").anglepicker("value", 45);
});

// for Quarter Dial
function makeQuarterDail(){
    console.log('makequarterdail');
    var ac = document.getElementById("anglepicker-counter");
    ac.style.borderTopLeftRadius= 0;
    ac.style.borderTopRightRadius='100%';
    ac.style.borderBottomRightRadius= 0;
    ac.style.borderBottomLeftRadius= 0;
    let ptr;
    setTimeout(() =>{
    ptr = document.getElementsByClassName('ui-anglepicker-pointer')[1]
    ptr.style.position='relative';
    ptr.style.left='2px';
    ptr.style.top='47px';
    ptr.style.width='45px';
    // console.log('child',ptr.style);
    },1000);
}

function getPdf() {
    window.print()
}
// Map Related

// This sample requires the Places library. Include the libraries=places
// parameter when you first load the API. For example:
// <script
// src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

function initMap() {
    var map = new google.maps.Map(
        document.getElementById('map'),
        {center: {lat: -33.8688, lng: 151.2195}, zoom: 13});
  
    var input = document.getElementById('pac-input');
  
    var autocomplete = new google.maps.places.Autocomplete(input);
  
    autocomplete.bindTo('bounds', map);
  
    // Specify just the place data fields that you need.
    autocomplete.setFields(['place_id', 'geometry', 'name', 'formatted_address']);
  
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
  
    var infowindow = new google.maps.InfoWindow();
    var infowindowContent = document.getElementById('infowindow-content');
    infowindow.setContent(infowindowContent);
  
    var geocoder = new google.maps.Geocoder;
  
    var marker = new google.maps.Marker({map: map});
    marker.addListener('click', function() {
      infowindow.open(map, marker);
    });
  
    autocomplete.addListener('place_changed', function() {
      infowindow.close();
      var place = autocomplete.getPlace();
  
      if (!place.place_id) {
        return;
      }
  
      console.log(place.place_id);
  
      var place_ID_box = document.getElementById('placeID');
      var lat_box = document.getElementById('lat');
      var lon_box = document.getElementById('lon');
  
  
      console.log(place_ID_box)
      place_ID_box.value = place.place_id;
  
      var location_api_base = "https://maps.googleapis.com/maps/api/geocode/json?place_id="
  
      var key_option = "&key="
  
      var key = "AIzaSyCdXNN5iv5yl77PGwZpG5GPjZk_epT_U5Y"
  
      var fetch_url = location_api_base + place.place_id + key_option + key
  
      console.log(fetch_url)
  
      fetch(fetch_url)
        .then(response => response.json())
        .then(data => {
          console.log(data.results[0].geometry.location)
          lat_box.value = data.results[0].geometry.location.lat
          lon_box.value = data.results[0].geometry.location.lng
      });
  
  
      geocoder.geocode({'placeId': place.place_id}, function(results, status) {
        if (status !== 'OK') {
          window.alert('Geocoder failed due to: ' + status);
          return;
        }
  
        map.setZoom(11);
        map.setCenter(results[0].geometry.location);
  
        // Set the position of the marker using the place ID and location.
        marker.setPlace(
            {placeId: place.place_id, location: results[0].geometry.location});
  
        marker.setVisible(true);
  
        infowindowContent.children['place-name'].textContent = place.name;
        infowindowContent.children['place-id'].textContent = place.place_id;
        infowindowContent.children['place-address'].textContent =
            results[0].formatted_address;
  
        // infowindow.open(map, marker);
      });
    });
  }

// progress bar 
function showProgress() {
 console.log('show progress called');
  var i = 0;
  if (i == 0) {
    i = 1;
    var progress = document.getElementById("progress");
    progress.style.display='block';
    var elem = document.getElementById("progressBar");
    elem.style.display='block';
    var width = 1;
    var id = setInterval(frame, 100);
    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
        progress.style.display='none';
        elem.style.display='none';
      } else {
        width++;
        elem.style.width = width + "%";
      }
    }
  }
}