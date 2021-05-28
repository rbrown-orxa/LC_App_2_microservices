import React, { Component } from "react";
import Footer from "./Footer";
import "../App.css";
import rightArrow from "../img/right_arrow.png";
//import Helper from './Helper';
import BatteryCostCurveGraph from "./charts/BatteryCostCurveGraph";
// import battery_cost_curve_data from './charts/battery_cost_curve.js';
import ImportExportGraph from "./charts/ImportExportGraph";
// import import_export_data from './charts/import_export.js';
import PVCostCurveGraph from "./charts/PVCostCurveGraph";
import { AZURE_MARKET_PLACE_URL } from "../common/constants";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
// import pv_cost_curve_data from './charts/pv_cost_curve.js';

class ResultsPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            results: {
                site: {
                    success: false,
                    battery_size_kwh: 0,
                    annual_import_site_kwh: 0,
                    annual_import_ev_kwh: 0,
                    annual_import_total_kwh: 0,
                    annual_import_with_pv_kwh: 0,
                    annual_import_with_pv_and_battery_kwh: 0,
                    original_import_cost: 0,
                    with_ev_import_cost: 0,
                    with_battery_optimised_import_cost: 0,
                    total_import_cost: 0,
                },
                buildings: [
                    {
                        name: "N/A",
                        pv_size_kw: 0,
                        num_of_chargers: 0,
                    },
                ],
                charts: {},
            },
        };
    }

    componentWillMount() {
        console.log("willmount", this.props.results);
        if (this.props.results) {
            this.setState({
                results: this.props.results,
                charts: this.props.charts,
            });
        }
        // using test js
        // console.log('willmount',this.props.results.results);
        //   if(this.props.results){
        //     this.setState({
        //       results:this.props.results.results,
        //       charts:this.props.results.charts,
        //     });
        //   }
    }

    render() {
        let { results, charts } = this.state;
        // if(results===undefined) return(<div>loading...</div>)
        // if(charts===undefined) return(<div>loading charts...</div>)
        console.log("results,", results);
        let siteResult = results.site;
        let battery_cost_curve_data = charts.site.battery_cost_curve;
        let import_export_data = charts.site.import_export;
        let buildingsResult = results.buildings;
        let pv_cost_curve_data1 = charts.buildings;
        for (let i = 0; i < buildingsResult.length; ++i) {
            for (let j = 0; j < pv_cost_curve_data1.length; ++j) {
                if (buildingsResult[i].name === pv_cost_curve_data1[j].name) {
                    buildingsResult[i].pv_cost_curve =
                        pv_cost_curve_data1[j].pv_cost_curve;
                }
            }
        }
        // console.log('state buildings',buildingsResult,pv_cost_curve_data1)

        return (
            <div class="row">
                <div
                    class="result-contents col-md-6 col-sm-6"
                    style={{ fontWeight: "400", background: "white" }}
                >
                    <div class="row" style={{ background: "white" }}>
                        <div class="col">
                            <div>
                                <h5 style={{ textAlign: "center" }}>
                                    Optimisation Results
                                </h5>
                                <br />
                            </div>
                            <div
                                class="col"
                                style={{
                                    fontSize: "14px",
                                    textAlign: "center",
                                    color: "#464755",
                                }}
                            >
                                <div class="row">
                                    <div class="col">
                                        Battery Size (kWh)
                                        <br />
                                        <label id="battery_size_kwh">
                                            {siteResult.battery_size_kwh}
                                        </label>
                                    </div>
                                    <div class="col">
                                        Annual Import Site (kWh)
                                        <br />
                                        <label
                                            id="annual_import_site_kwh"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.annual_import_site_kwh}
                                        </label>
                                    </div>
                                    <div class="col">
                                        Annual Import EV (kWh)
                                        <br />
                                        <label
                                            id="annual_import_ev_kwh"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.annual_import_ev_kwh}
                                        </label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        Annual Import Total (kWh) ​ <br />
                                        <label id="annual_import_total_kwh">
                                            {siteResult.annual_import_total_kwh}
                                        </label>
                                    </div>
                                    <div class="col">
                                        Annual Import with PV (kWh)
                                        <br />
                                        <label id="annual_import_with_pv_kwh">
                                            {
                                                siteResult.annual_import_with_pv_kwh
                                            }
                                        </label>
                                    </div>
                                    <div class="col">
                                        Annual Import with PV and Battery (kWh)
                                        ​​
                                        <br />
                                        <label
                                            id="annual_import_with_pv_and_battery_kwh"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {
                                                siteResult.annual_import_with_pv_and_battery_kwh
                                            }
                                        </label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        Original Import Cost
                                        <br />
                                        <label
                                            id="original_import_cost"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.original_import_cost}
                                        </label>
                                    </div>
                                    <div class="col">
                                        With EV Import Cost​
                                        <br />
                                        <label
                                            id="with_ev_import_cost"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.with_ev_import_cost}
                                        </label>
                                    </div>
                                    <div class="col">
                                        Total Import Cost
                                        <br />
                                        <label
                                            id="total_import_cost"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.total_import_cost}
                                        </label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        With PV Optimised Import Cost
                                        <br />
                                        <label id="with_pv_optimised_import_cost">
                                            {
                                                siteResult.with_pv_optimised_import_cost
                                            }
                                        </label>
                                    </div>
                                    {/* <div class="col"></div> */}
                                    <div class="col">
                                        With Battery Optimised Import Cost
                                        <br />
                                        <label id="with_battery_optimised_import_cost">
                                            {
                                                siteResult.with_battery_optimised_import_cost
                                            }
                                        </label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        Lifetime profit
                                        <br />
                                        <label
                                            id="lifetime_profit"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.lifetime_profit}
                                        </label>
                                    </div>
                                    <div class="col">
                                        ROI
                                        <br />
                                        <label
                                            id="roi"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.roi}
                                        </label>
                                    </div>
                                    <div class="col">
                                        Payback period
                                        <br />
                                        <label
                                            id="payback_period"
                                            style={{ fontWeight: "normal" }}
                                        >
                                            {siteResult.payback_period}
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-12">
                                    <hr />
                                    <h5>Cost vs Battery Size</h5>
                                    <BatteryCostCurveGraph
                                        graphData={battery_cost_curve_data}
                                    />
                                    <hr />
                                    <h5>Import/Export Yearly Overview</h5>
                                    <ImportExportGraph
                                        graphData={import_export_data}
                                    />
                                    <hr />
                                    <h5>Import/Export Weekly Sample</h5>
                                    <ImportExportGraph
                                        graphData={import_export_data}
                                        week={true}
                                    />
                                </div>
                            </div>
                            <hr />
                            <div class="row">
                                <div class="col">
                                    <div class="row">
                                        <div class="col-md-4">
                                            Building Name
                                        </div>
                                        <div class="col-md-4">PV Size (kW)</div>
                                        <div class="col-md-4">
                                            No. of Chargers
                                        </div>
                                    </div>
                                    {buildingsResult.map((building) => (
                                        <div>
                                            <div
                                                class="row"
                                                style={{
                                                    background: "#F2E9F0",
                                                }}
                                            >
                                                <div class="col-md-4">
                                                    {building.name}
                                                </div>
                                                <div class="col-md-4">
                                                    {building.pv_size_kw}
                                                </div>
                                                <div class="col-md-4">
                                                    {building.num_of_chargers}
                                                </div>
                                            </div>
                                            {/* <div class="row"> */}
                                            {/* <div class="col"> */}
                                            <h5>Size(kWp) vs Profit PA</h5>
                                            <PVCostCurveGraph
                                                graphData={
                                                    building.pv_cost_curve
                                                }
                                            />
                                            {/* <div> */}
                                            {/* </div> */}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-1">
                    <button
                        class="btn btn-success btn-sm"
                        onClick={this.props.prevStep}
                    >
                        Back
                    </button>
                </div>
                <div
                    class="contents col-md-2"
                    style={{
                        marginTop: "10vh",
                        verticalAlign: "middle",
                        height: "250px",
                        background: "white",
                    }}
                >
                    <div className="col control-label-heading">
                        <a href={AZURE_MARKET_PLACE_URL}>
                            <button className="arrow-round-btn">
                                <FontAwesomeIcon
                                    icon={faArrowRight}
                                    color={"#fff"}
                                />
                            </button>
                        </a>
                        &nbsp; UPGRADE
                        <br />
                        <ul
                            style={{
                                fontSize: "14px",
                                fontWeight: "200",
                                marginTop: "20px",
                                listStyle: "none",
                            }}
                        >
                            <li>
                                &#10004;&nbsp;Run unlimited results for all your
                                sites
                            </li>
                            <li>
                                &#10004;&nbsp;Download detailed site report to
                                analyse solar, storage, and EV potential
                            </li>
                            <li>&#10004;&nbsp;Custom input support</li>
                        </ul>
                    </div>
                </div>
                <br />

                {/* </div> */}
                {/* column splits here */}
                {/* </div> */}
                {/* <div class="col" style={{width:'100%',}}>
                  <button class="btn btn-success btn-sm float-lg-left" name="back-button"
                  style={{position:'fixed',left:'1vw',bottom:'5vh'}}
                  onClick={(e)=>{ this.props.prevStep()
                  }}>Back</button>
            </div> */}

                <Footer />
            </div>
        );
    }
}

export default ResultsPage;
