import React, {Component} from 'react';
import $ from 'jquery';
import 'jquery-ui-bundle';
import 'jquery-ui-bundle/jquery-ui.css';

export default class RangeBar extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount(){
        // const range = document.getElementById('range'),
        //       rangeV = document.getElementById('rangeV'),
        //       setValue = ()=>{
        //                 const newValue = Number( (range.value - range.min) * 100 / (range.max - range.min) ),
        //                      newPosition = 10 - (newValue * 0.2);
        //                      rangeV.innerHTML = `<span>${range.value}</span>`;
        //                      let leftPos =`calc(${newValue}% + (${newPosition}px))`;
        //                      rangeV.style.left = `calc(${newValue}% + (${newPosition}px))`;
        //                     //  var style = document.querySelector('input[type=range]');
        //                     //  style.style = "input[type=range]::-webkit-slider-thumb { left: " + leftPos  + " !important;}";
        //                     //  //console.log('style',style)
        //                     };
        // document.addEventListener("DOMContentLoaded", setValue);
        // range.addEventListener('input', setValue);
    }

    handleRangeChange(e){

        document.getElementById('roof_size_m2').value=e.target.value;

    }

    render(){

        return(             
              <input id="range" type="range" min="50" max="1000" defaultValue="250" // value="200"
              onChange={this.handleRangeChange}
              step="10"
            //   style={{width:'100%'}}
              />
            );

    }

}    
