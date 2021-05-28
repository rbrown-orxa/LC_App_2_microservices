import React,{PureComponent} from 'react';
import {Line} from 'react-chartjs-2';
// import {Bar, Line, Pie} from 'react-chartjs-2';
// import graphData from './pv_cost_curve.js';

const legend = {
    display: true,
    position: "bottom",
    labels: {
      fontColor: "#323130",
      fontSize: 12
    }
};

const options={
    scales: {
        yAxes: [{
            scaleLabel: {
                display: true,
                labelString: 'Profit PA'
              }
        }],
        xAxes: [{
            scaleLabel: {
                display: true,
                labelString: 'Size (kWp)'
              }
        }]
    },
    maintainAspectRatio: false,
};

export default class PVCostCurveGraph extends PureComponent{

    constructor(props){
        super(props);
        this.state={
           
        }
    }

    componentWillMount(){
        let {graphData} = this.props;
        let sizekWpValues =  graphData.Size_kWp;
        sizekWpValues = sizekWpValues.map(function(each_element){
            return Number(each_element.toFixed(2));
        });
        let profitPAValues = graphData.Profit_PA;
        profitPAValues = profitPAValues.map(function(each_element){
            return Number(each_element.toFixed(2));
        });
        // console.log('sizekWpValues',sizekWpValues);
        // console.log('profitPAValues',profitPAValues);
        let dataToPlot = 
            //Bring in data
            {
            labels: sizekWpValues,//[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            datasets: [{
                label : "Profit PA",
                data  : profitPAValues,
                fill  : false,
                borderColor : "#3E88F3",
                borderWidth : 1,
                pointStyle: 'circle',
            },
            ]
            }

            this.setState({data:dataToPlot})
    }

    render(){
        let {data} = this.state;
        return(
            <div className='Chart'>
                <Line
                    data={data}
                    width={100}
                    height={300}
                    legend={legend}
                    options={options}
                />
            </div>
        );

    }

}