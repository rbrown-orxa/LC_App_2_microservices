import React, { PureComponent } from "react";
import { Line } from "react-chartjs-2";
// import {Bar, Line, Pie} from 'react-chartjs-2';
// import importExportData from './import_export.js';

const legend = {
    display: true,
    position: "bottom",
    labels: {
        fontColor: "#323130",
        fontSize: 12,
    },
};

const options = {
    scales: {
        yAxes: [
            {
                scaleLabel: {
                    display: true,
                    labelString: "Energy (kWh)",
                },
            },
        ],
        xAxes: [
            {
                // type: 'day',
                // distribution: 'series',
                scaleLabel: {
                    display: true,
                    labelString: "Date",
                },
                time: {
                    unit: "hour",
                    unitStepSize: 168,
                },
            },
        ],
        // animation: {
        //     duration: 0
        // }
    },
    maintainAspectRatio: false,
    responsive: true,
};

export default class ImportExportGraph extends PureComponent {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentWillMount() {
        let { graphData } = this.props;
        let generationValues = graphData.Generation;
        let loadValues = graphData.Load;
        let importValues = graphData.Import;
        let exportValues = graphData.export;
        let generationValuesWeek = generationValues.slice(
            generationValues.length - 168,
            generationValues.length
        );
        let loadValuesWeek = loadValues.slice(
            loadValues.length - 168,
            loadValues.length
        );
        let importValuesWeek = importValues.slice(
            importValues.length - 168,
            importValues.length
        );
        let exportValuesWeek = exportValues.slice(
            exportValues.length - 168,
            exportValues.length
        );

        // console.log('generationValuesWeek',generationValuesWeek);
        // console.log('loadValuesWeek',loadValuesWeek);
        // console.log('importValuesWeek',importValuesWeek);
        // console.log('exportValuesWeek',exportValuesWeek);
        // let startDate = new Date(new Date().setFullYear(new Date().getFullYear() - 1));
        let startDate = new Date("2018-12-31");
        Date.prototype.addHours = function (h) {
            var copiedDate = new Date(this.getTime());
            copiedDate.setHours(copiedDate.getHours() + h);
            return copiedDate;
        };
        // console.log('startDate',startDate,generationValues.length)
        let datesArray = [];
        for (let i = 0; i < generationValues.length; ++i) {
            // console.log('startDate++',startDate.addHours(i))
            let nextDate = startDate.addHours(i);
            // console.log('nextDate',nextDate)
            datesArray.push(nextDate.toLocaleDateString("en-GB"));
        }
        // let datesArrayWeek = datesArray.slice(datesArray.length-168,datesArray.length)
        let datesArrayWeek = datesArray.slice(0, 168);

        let borderColors = ["#DCB63C", "#3E88F3", "#BA403D", "#323232"];
        // console.log('datesArray',datesArray)
        let dataToPlot =
            //Bring in data
            {
                labels: this.props.week ? datesArrayWeek : datesArray, //[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                datasets: [
                    {
                        label: "Generation",
                        data: this.props.week
                            ? generationValuesWeek
                            : generationValues,
                        fill: false,
                        borderColor: borderColors[0],
                        borderWidth: 1,
                        pointStyle: "line",
                        pointRadius: 0.1,
                    },
                    {
                        label: "Load Values",
                        data: this.props.week ? loadValuesWeek : loadValues,
                        fill: false,
                        borderColor: borderColors[1],
                        borderWidth: 1,
                        pointStyle: "line",
                        pointRadius: 0.1,
                    },
                    {
                        label: "Import",
                        data: this.props.week ? importValuesWeek : importValues,
                        fill: false,
                        borderColor: borderColors[2],
                        borderWidth: 1,
                        pointStyle: "line",
                        pointRadius: 0.1,
                    },
                    {
                        label: "Export",
                        data: this.props.week ? exportValuesWeek : exportValues,
                        fill: false,
                        borderColor: borderColors[3],
                        borderWidth: 1,
                        pointStyle: "line",
                        pointRadius: 0.1,
                    },
                ],
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
            };

        this.setState({ data: dataToPlot });
    }

    render() {
        let { data } = this.state;
        return (
            <div className="Chart">
                <Line
                    data={data}
                    width={300}
                    height={250}
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
