import React,{PureComponent} from 'react';
import {Line} from 'react-chartjs-2';
// import {Bar, Line, Pie} from 'react-chartjs-2';
// import graphData from './battery_cost_curve.js';

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
                labelString: 'Cost'
              }
        }],
        xAxes: [{
            scaleLabel: {
                display: true,
                labelString: 'Battery Size'
              }
        }]
    },
    maintainAspectRatio: false,
};

export default class BatteryCostCurveGraph extends PureComponent{

    constructor(props){
        super(props);
        this.state={
           
        }
    }

    componentWillMount(){
       let  {graphData} = this.props 
        let labelsMonthArray =  graphData.batt_size;
        let totalCostValues = graphData.total_cost;
        // console.log('labelsMonthArray',labelsMonthArray);
        // console.log('totalCostValues',totalCostValues);
        let dataToPlot = 
            //Bring in data
            {
            labels: labelsMonthArray,//[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            datasets: [{
                label : "Total Cost",
                data  : totalCostValues,
                fill  : false,
                borderColor : "#DCB63C",
                borderWidth : 1,
                pointStyle: 'cross',
            },
            ]
            //     [
            //     {
            //         label: "Battery Cost",
            //         data: [0.0, 24.7591666667, 49.5183333333, 74.2775, 99.0366666667, 123.7958333333, 148.555,
            //             173.3141666667, 198.0733333333, 222.8325, 247.5916666667],
            //         fill: false,
            //         borderColor: "#DCB63C",
            //         borderWidth: 0.5,
            //     },
            //     {
            //         label: "Import Cost",
            //         data: [2015.6654497132, 1972.6819997263, 1933.5181649786, 1899.3971684855, 1870.5477381637, 1845.9393435238,
            //             1824.2019197983, 1805.1354345698, 1789.7646757517, 1777.4370026968, 1766.9087646337],
            //         fill: false,
            //         borderColor: "#3E88F3",
            //         borderWidth: 0.5,
            //         // showLine: false,
            //     }
            //     ,
            //     {
            //         label: "Export Revenue",
            //         data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            //         fill: false,
            //         borderColor: "#BA403D",
            //         borderWidth: 0.5,
            //     }
            //     ,
            //     {
            //         label: "Total Cost",
            //         data: [2015.6654497132, 1997.441166393, 1983.0364983119, 1973.6746684855, 1969.5844048304, 1969.7351768572
            //                 ,1972.7569197983, 1978.4496012365, 1987.8380090851, 2000.2695026968, 2014.5004313004],
            //         fill: false,
            //         borderColor: "#9FAA3A",
            //         borderWidth: 0.5,
            //     }
        //    ],

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
                    // options={{
                    //     maintainAspectRatio: false,
                    // }}
                />
            </div>
        );

    }

}