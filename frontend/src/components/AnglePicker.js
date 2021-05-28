import React, {Component} from 'react';
import $ from 'jquery';
import 'jquery-ui-bundle';
import 'jquery-ui-bundle/jquery-ui.css';
import compassBgImg from '../img/compassbg.png'
import {dialWidgetCreator} from '../common/commonFunctions';
class AnglePicker extends Component{
    
/*
ui.anglepicker 
source : https://github.com/bgrins/ui.anglepicker
*/
    // constructor(props){
        // super(props);
        //  let jQuery = window.jQuery;
        //  //console.log('jQuery',jQuery) 

    // }

    componentDidMount(){
        dialWidgetCreator()
        $("#anglepicker").anglepicker({
            value: 0,
            clockwise: false,
            change: function(e, ui) {
                ////console.log('azmimuth',$(this).parent().find("#azimuth"));
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

        $("#anglepicker").anglepicker("value", -270);
    }

    render(){

        return(                
        <div class="col" >
                    <span class='container1'  style={{border:'none',
                                                    textAlign: 'center',
                                                    // width:'100%',   
                                                    background:'transparent',
                                                    color:'#FFF',
                                                    display:this.props.isCompassVisible ? 'block' : 'none',
                                                    // mixBlendMode:'hard-light',
                                                    userSelect:'none',
                                                    position:'absolute',
                                                    top:'-220px',
                                                    left:'30%', 
                                                    }}>                        
                        <span class='angle-container'/>
                        <span id="anglepicker"><img src={compassBgImg} alt=''
                                                    style={{width:'140px',
                                                            position:'absolute',
                                                            left:'0px',
                                                            top:'1.5px',
                                                            opacity:'1',
                                                            zIndex:100 ,}}/>
                        </span>
                    </span>      
        </div>
        );

    }

} 

function printDegrees(log, deg) {
    //log.html(deg + '&deg;');
    log.val(deg);
}

export default AnglePicker;