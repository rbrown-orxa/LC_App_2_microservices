import React, {Component} from 'react';
import $ from 'jquery';
import 'jquery-ui-bundle';
import 'jquery-ui-bundle/jquery-ui.css';
import {quarterDialWidgetCreator} from '../common/commonFunctions';
class AnglePickerQuarter extends Component{

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
       
        quarterDialWidgetCreator()
        setTimeout(() => {
            let dial=document.getElementsByClassName('ui-anglepicker')[1];
            dial.style.width='52px';
            dial.style.height='52px';
        }, 100);
        $("#anglepicker-counter").anglepicker({
            value: 0,
            clockwise: true,
            change: function(e, ui) {
                let roofPtr = document.getElementsByClassName('ui-anglepicker-pointer')[1]
                if(ui.value>90 && ui.value<240) {
                    ////console.log(ui.value,' greater than 90')
                    printDegrees($(this).parent().find("#roofpitch"), 90); 
                    // //console.log('pointer',roofPtr);
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
                ////console.log('started');
                $("em").fadeIn('fast');
            },
            stop: function(ui) {
                ////console.log('stopped');
                // if(ui.value>90) {
                //   $("#anglepicker-counter").anglepicker("value", 90)
                // }
                $("em").hide();
            }
        });
        $("#anglepicker-counter").anglepicker("value", 30);
        // //console.log('makequarterdail');
        var ac = document.getElementById("anglepicker-counter");
        ac.style.borderTopLeftRadius= 0;
        ac.style.borderTopRightRadius='100%';
        ac.style.borderBottomRightRadius= 0;
        ac.style.borderBottomLeftRadius= 0;
        let ptr;
        setTimeout(() =>{
        ptr = document.getElementsByClassName('ui-anglepicker-pointer')[1]
        // //console.log(ptr)
        ptr.style.position='relative';
        ptr.style.left='0px';
        ptr.style.top='45px';
        ptr.style.width='45px';
        // //console.log('child',ptr.style);
        },100);
    }

    render(){

        return(                
            <span class="col-sm"  style={{}}>
            {/* <table class="" style={{textAlign: 'center',border:'none'}} > */}
                {/* <tr><td style={{fontSize:'10px',fontWeight: 'bold',position:'fixed', top:'20px', left:'-20px'}}>90&deg;</td><td></td></tr> */}
                {/* <tr> */}
                {/* <td> */}
                <span class='container1'>
                    <span class='angle-container'/>
                    <span id="anglepicker-counter" ></span>
                    <span class='log'></span>
                </span>
                {/* </td><td class="align-middle" style={{fontSize:'10px',fontWeight:'bold',position:'relative', left:'-5px',top:'20px'}}>0&deg;</td> */}
                {/* </tr> */}
            {/* </table> */}
        </span>
   

        );

    }

} 

function printDegrees(log, deg) {
    //log.html(deg + '&deg;');
    log.val(deg);
}

// for Quarter Dial
// function makeQuarterDail(){
//     //console.log('makequarterdail');
//     var ac = document.getElementById("anglepicker-counter");
//     ac.style.borderTopLeftRadius= 0;
//     ac.style.borderTopRightRadius='100%';
//     ac.style.borderBottomRightRadius= 0;
//     ac.style.borderBottomLeftRadius= 0;
//     let ptr;
//     setTimeout(() =>{
//     ptr = document.getElementsByClassName('ui-anglepicker-pointer')[1]//0
//     ptr.style.position='relative';
//     ptr.style.left='2px';
//     ptr.style.top='47px';
//     ptr.style.width='45px';
//     // //console.log('child',ptr.style);
//     },2000);
// }
export default AnglePickerQuarter;