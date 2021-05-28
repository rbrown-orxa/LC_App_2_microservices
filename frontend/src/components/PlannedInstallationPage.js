import React, { Component } from "react";
import rightArrow from "../img/right_arrow.png";
import leftArrow from "../img/left_arrow.png";
import SiteSummaryPage from "./SiteSummaryPage";
// import CustomSlider from './CustomSlider';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import LeftArrowButton from "../common/LeftArrowButton";
import AppBanner from "../common/AppBanner";
import HelpModal from './HelpModal';

export default class PlannedInstallationPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            step: 1,
            address: "",
            isCompassVisible: true,
            building_data: [],
            hasBatterySystem: false,
            hasEvChargers: false,
            showSiteSummary: true,
            evChargersMarks: [
                {
                    value: 0,
                    label: "0",
                },
                {
                    value: 100,
                    label: "100",
                },
                {
                    value: 500,
                    label: "500",
                },
                {
                    value: 1000,
                    label: "1000",
                },
            ],
        };

        // this.hasBatterySystemChange = this.hasBatterySystemChange.bind(this);
        this.hasEvChargersChange = this.hasEvChargersChange.bind(this);
        this.updateBuilding = this.updateBuilding.bind(this);
        this.updateBuildingEVC = this.updateBuildingEVC.bind(this);
        this.updateBuildingData = this.updateBuildingData.bind(this);
        this.submitAction = this.submitAction.bind(this);
    }

    componentWillMount() {
        // setTimeout(()=>{
        // let AppHeader = document.getElementsByClassName('App-header')[0];
        // AppHeader.style.background='white';
        // },500);
        this.setState({ building_data: this.props.building_data });
    }

    toggleSiteSummary = () => {
        let { showSiteSummary } = this.state;
        this.setState({ showSiteSummary: !showSiteSummary });
    };

    setNumEVChargers(value) {
        let numEVCEle = document.getElementById("num_ev_chargers");
        if (numEVCEle !== null) {
            numEVCEle.value = value;
        }
        return value;
    }

    updateBuildingEVC() {
        let numEVCEle = document.getElementById("num_ev_chargers");
        if (numEVCEle !== null) {
            this.updateBuilding("num_ev_chargers", numEVCEle.value);
        }
    }

    updateBuildingData(newBuildingData){
        this.setState({building_data:newBuildingData});
        // this.props.sendBuildingsDataToForm(newBuildingData);
        this.updateAllBuildingsToForm();

    }

    updateBuilding(field, value) {
        let { building_data } = this.props;
        console.log("upd building_data", building_data);
        var building = building_data.filter(function (building) {
            let selectedBuildingEle = document.getElementById(
                "building_list_ip"
            ); //.options.selected.value;
            let buildingOptions = [];
            let selectedBuilding = "";
            if (selectedBuildingEle !== null) {
                buildingOptions = selectedBuildingEle.options;
                selectedBuilding =
                    buildingOptions[selectedBuildingEle.selectedIndex];
                console.log("selectedBuilding", selectedBuilding.value);
            }
            return building.building_name === selectedBuilding.value;
        });
        console.log("building", building);
        if (building !== null && building.length > 0) {
            building[0][field] = value;
        }

        this.updateBuildingData(building_data);
    }

    // hasBatterySystemChange = (e) =>{
    //   this.setState({hasBatterySystem:e.target.checked,
    //   });
    // }

    hasEvChargersChange = (e) => {
        this.setState({ hasEvChargers: e.target.checked });
    };

    updateAllChangesToForm() {
        this.props.handleChangeInput("pv_life_yrs");
        this.props.handleChangeInput("pv_cost_kwp");
        this.props.handleChangeInput("battery_life_cycles");
        this.props.handleChangeInput("battery_cost_kwh");
    }

    updateAllBuildingsToForm() {
        console.log("IP updating all building to form");
        let { building_data } = this.state;
        this.props.sendBuildingsDataToForm(building_data);
    }

    submitAction() {
        this.updateAllChangesToForm();
        this.updateAllBuildingsToForm();
        this.props.submitAction();
    }

    render() {
        let {
            //hasBatterySystem,
            hasEvChargers,
        } = this.state;
        let {
            building_data,
            resolveApiError,
            resolveApiResponseStatus,
            free_calls,
            max_free_calls,
        } = this.props;
        //console.log('render step',step,this.state)
        let buildingOptions = [];
        if (building_data !== undefined && building_data.length > 0) {
            for (let i = 0; i < building_data.length; ++i) {
                buildingOptions.push(
                    <option value={building_data[i].building_name}>
                        {building_data[i].building_name}
                    </option>
                );
            }
        }
        console.log("buildingOptions", buildingOptions);
        return (
            <div>
                {resolveApiError !== undefined && resolveApiError.length > 0 ? (
                    <div id="AppBanner">
                        <div class="alert alert-danger" role="alert">
                            {resolveApiError}
                        </div>
                    </div>
                ) : (
                    ""
                )}
                {resolveApiResponseStatus === 200 &&
                    <AppBanner free_calls={max_free_calls-free_calls} max_free_calls={max_free_calls} />}
                <div
                    class=""
                    style={{
                        marginTop: "-30px",
                        marginBottom: "30px",
                        textAlign: "center",
                    }}
                >
                    <h3>Now, tell us about your planned installation </h3>
                </div>
                <div class="col-lg-12" style={{ background: "transparent" }}>
                    <div class="row">
                        <div
                            className="col form-box"
                            style={{ marginRight: "10px" }}
                        >
                            <div class="control-label-heading title-box">
                                Planned Solar Panel Costs
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col form-question">
                                    <div >
                                        What would be the expected life of your
                                        solar setup in years?&nbsp;
                                        <HelpModal
                                            info='Enter the local Solar PV system lifetime in years. Many solar systems can produce electricity for 25 or more years, but we have put 20 years as the default. As you explore different system providers, you can enter and change the expected years to see how much you can save over different time periods.'
                                        />
                                    </div>
                                    <input
                                        type="number"
                                        id="pv_life_yrs"
                                        defaultValue={
                                            this.props.pv_life_yrs !== undefined
                                                ? this.props.pv_life_yrs
                                                : 20
                                        }
                                    />
                                    <br />
                                    &nbsp;
                                    <div>
                                        What is the cost per kWp of solar
                                        installation for a PV installer in your
                                        area?&nbsp;
                                        <HelpModal
                                            info='Enter the standard rate for 1kW of solar panels and installation in your local currency. If you have quotes from installers in your area, then you could enter the amount here or you could leave it as default.'
                                        />    
                                    </div>
                                    <input
                                        id="pv_cost_kwp"
                                        type="number"
                                        placeholder="1.0"
                                        defaultValue={
                                            this.props.pv_cost_kwp !== undefined
                                                ? this.props.pv_cost_kwp
                                                : 1840
                                        }
                                    />
                                    <br />
                                    &nbsp;
                                </div>
                            </div>
                        </div>
                        {/* <div className='col-md-1'>
                        </div>     */}
                        <div
                            className="col form-box"
                            style={{ marginRight: "10px" }}
                        >
                            <div class="control-label-heading title-box">
                                Planned Battery System
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col">
                                    {/* <div class="form-question">Do you plan to install a battery system?
                  <label class="switch" style={{position:'absolute',right:'24px'}}>
                    <input type="checkbox" id="hasBatterySystem"
                          onChange={this.hasBatterySystemChange} defaultChecked={this.state.hasBatterySystem}
                    />
                    <span class="slider" style={{color:'white'}}>&nbsp;&#10004;</span>
                  </label>
                </div> */}
                                    <div
                                        id="batterySystemBox" //style={{display:hasBatterySystem?'block':'none'}}
                                    >
                                        <div class="form-question">
                                            What would be the maximum life
                                            cycles of your battery setup?
                                            &nbsp;
                                            <HelpModal
                                                info='Enter the local Battery Energy Storage system lifetime in charging cycles or accept the default values.'
                                            />    
                                            <br />
                                            <input
                                                id="battery_life_cycles"
                                                type="number"
                                                placeholder="1.0"
                                                defaultValue={
                                                    this.props
                                                        .battery_life_cycles
                                                        ? this.props
                                                              .battery_life_cycles
                                                        : 6000
                                                }
                                            />
                                            &nbsp;
                                        </div>
                                        <br />
                                        <div class="form-question">
                                            What is the cost per kWh of Battery
                                            installation in your area?
                                            &nbsp;
                                            <HelpModal
                                                info='Enter the standard rate for 1kWh of battery storage and installation in your local currency. If you have quotes from installers in your area, then you could enter the amount here or you could leave it as default.'
                                            />
                                            <br />
                                            <input
                                                id="battery_cost_kwh"
                                                type="number"
                                                placeholder="1.0"
                                                defaultValue={
                                                    this.props.battery_cost_kwh
                                                        ? this.props
                                                              .battery_cost_kwh
                                                        : 407
                                                }
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="col-md-4 form-box">
                            <div class="control-label-heading title-box">
                                Planned EV Chargers
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col">
                                    <div class="form-question">
                                        Do you plan to install EV
                                        chargers?&nbsp;
                                        <HelpModal
                                            info='If you plan to install Electric Vehicle Charging Points, specify the number of chargers for each applicable building, clicking ‘Add’ each time.'
                                        />
                                        <label
                                            class="switch"
                                            style={{
                                                position: "absolute",
                                                right: "24px",
                                            }}
                                        >
                                            <input
                                                type="checkbox"
                                                id="hasEvChargers"
                                                onChange={
                                                    this.hasEvChargersChange
                                                }
                                            />
                                            <span
                                                class="slider"
                                                style={{ color: "white" }}
                                            >
                                                &nbsp;&#10004;
                                            </span>
                                        </label>
                                    </div>
                                    <br />
                                    &nbsp;
                                    <div
                                        id="evChargersBox"
                                        style={{
                                            display: hasEvChargers
                                                ? "block"
                                                : "none",
                                        }}
                                    >
                                        <div class="form-question">
                                            Select your building&nbsp;
                                            <span class="help-icon">i</span>
                                            <br />
                                            <select id="building_list_ip">
                                                <option value="">
                                                    --Please Select--
                                                </option>
                                                {buildingOptions}
                                            </select>
                                        </div>
                                        <div class="form-question">
                                            How Many?
                                            <br />
                                            <input
                                                id="num_ev_chargers"
                                                type="number"
                                                style={{ width: "70px" }}
                                                defaultValue = {0}
                                            />
                                            <br />
                                            <div style={{ width: "100%" }}>
                                                <span></span>
                                            </div>
                                        </div>
                                        <button
                                            class="btn btn-sm btn-success"
                                            onClick={this.updateBuildingEVC}
                                        >
                                            Add
                                        </button>
                                        <br />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <SiteSummaryPage
                        showSiteSummary={this.state.showSiteSummary}
                        address={this.props.address}
                        building_data={this.state.building_data}
                        updateBuildingToParentPage={this.updateBuildingData}
                    />

                    <br />
                    <br />
                    <br />
                    <div class="arrowButtons">
                        <div
                            class="btn btn-success"
                            onClick={(e) => {
                                this.updateAllChangesToForm();
                                this.updateAllBuildingsToForm();
                                this.toggleSiteSummary();
                            }}
                        >
                            Site Summary
                        </div>
                        &nbsp;
                        <LeftArrowButton
                            onButtonClick={(e) => {
                                this.updateAllChangesToForm();
                                this.updateAllBuildingsToForm();
                                this.props.prevStep();
                            }}
                        />
                        {/* <img src={leftArrow} alt=''
            onClick={(e)=>{ this.updateAllChangesToForm();this.updateAllBuildingsToForm()
                        this.props.prevStep()
                    }}
                style={{width:'35px',padding:'10px',background:'#FAFAFA',border:'1px solid #F1F9FF',borderRadius:'20%',cursor:'pointer',
                      }}
            /> */}
                        &nbsp;
                        <button
                            class="btn btn-success"
                            onClick={this.submitAction}
                            disabled={
                                resolveApiError.length > 0 ? "disabled" : ""
                            }
                        >
                            &nbsp;&nbsp;See your output&nbsp;
                            <FontAwesomeIcon icon={faArrowRight} />
                            {/* <img
                                src={rightArrow}
                                alt=""
                                style={{
                                    width: "35px",
                                    padding: "10px",
                                    background: "#4DA858",
                                    borderRadius: "20%",
                                    cursor: "pointer",
                                }}
                            /> */}
                        </button>
                    </div>
                </div>
            </div>
        );
    }
}
