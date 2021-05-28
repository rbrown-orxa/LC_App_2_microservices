import React, { Component } from "react";
import ReactGoogleMap from "./ReactGoogleMap";
import PlacesAutocomplete from "react-places-autocomplete";
import { geocodeByAddress, getLatLng } from "react-places-autocomplete";
import AnglePicker from "./AnglePicker";
import AnglePickerQuarter from "./AnglePickerQuarter";
import deleteButton from "../img/deleteButton.png";
import CustomSlider from "./CustomSlider";
// import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import {
//     faInfoCircle,
//     faArrowRight,
//     faArrowLeft,
// } from "@fortawesome/free-solid-svg-icons";
import LeftArrowButton from "../common/LeftArrowButton";
import RightArrowButton from "../common/RightArrowButton";
import AppBanner from "../common/AppBanner";
import SiteSummaryPage from "./SiteSummaryPage";
import HelpModal from './HelpModal';

export default class LocationDetailsPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            address: "",
            isCompassVisible: true,
            building_data: [],
            showSiteSummary:true,
            roofDirectionText:'',
            roofSizeMarks: [
                {
                    value: 0,
                    label: `0 \u33A1`,
                },
                {
                    value: 1000,
                    label: "1000 \u33A1",
                },
            ],
        };
        this.addBuilding = this.addBuilding.bind(this);
        this.deleteBuilding = this.deleteBuilding.bind(this);
        this.getNextBuildingId = this.getNextBuildingId.bind(this);
        this.updateBuildingData = this.updateBuildingData.bind(this);
        this.azimuthRef = React.createRef();
        this.handleAzimuthChange = this.handleAzimuthChange.bind(this);
    }

    componentWillMount() {
        console.log("componentWillMount LDP");
        this.setState({
            building_data: this.props.building_data,
            address: this.props.address,
            trigger: Math.random(),
        });
        this.handleAddressSetting(this.props.address);
    }

    componentDidMount(){

    }

    componentWillReceiveProps(nextProps) {
        // console.log('next props',nextProps)
        this.setState({
            address: nextProps["pac-input"],
        });
        this.handleAddressSetting(nextProps.address);
    }

    toggleSiteSummary = () => {
        let { showSiteSummary } = this.state;
        this.setState({ showSiteSummary: !showSiteSummary });
    };

    getDirection = (angle) => {
        var directions = ['North', 'North-East', 'East', 'South-East', 'South', 'South-West', 'West', 'North-West'];
        return directions[Math.round(((angle %= 360) < 0 ? angle + 360 : angle) / 45) % 8];
    }

    handleAzimuthChange() {
        let directionText = this.getDirection(this.azimuthRef.current.value)
        this.setState({roofDirectionText:directionText})
        // console.log('handle azumuth',directionText,this.state.roofDirectionText,this.azimuthRef)
    }

    getNextBuildingId() {
        let { building_data } = this.state;
        // //console.log('getnextbuildingid ',building_data)
        if (building_data.length === 0) return 1;
        let buldingIds = [];
        for (let i = 0; i < building_data.length; ++i) {
            buldingIds.push(building_data[i].building_id);
        }
        // //console.log('buldingIds',buldingIds,Math.max(...buldingIds))
        return parseInt(Math.max(...buldingIds) + 1);
    }

    addBuilding() {
        if (this.state.building_data.length >= 6) {
            alert("Already uploaded required building data");
            return;
        }
        let { building_data } = this.state;
        // //console.log('add called')
        let building_name = document.getElementById("building_name");
        if(building_name.value==='' ) {
            alert('Please enter your building name.');
            window.scrollTo(0, 200);
            return;
        }
        let building_type = document.getElementById("building_type");
        if(building_type.value==='' ) {
            alert('Please select the type of building.');
            window.scrollTo(0, 200);
            return;    
        }

        const existinBuilding = building_data.find(building => building.building_name === building_name.value);
        if(existinBuilding && existinBuilding.building_id){
            alert('Please select a new name for the building.')
            window.scrollTo(0, 200);
            return; 
        }
        // let num_ev_chargers = document.getElementById('num_ev_chargers');
        // let pv_size_kwp_optional = document.getElementById('pv_size_kwp_optional');
        // let annual_kwh_consumption_optional = document.getElementById('annual_kwh_consumption_optional');
        let roof_size_m2 = document.getElementById("roof_size_m2");
        let azimuth = document.getElementById("azimuth");
        let roofpitch = document.getElementById("roofpitch");
        // let load_buildling_profile_csv = document.getElementById('load_buildling_profile_csv');

        let building = {
            building_id: this.getNextBuildingId(),
            building_name: building_name.value,
            building_type: building_type.value,
            // num_ev_chargers:num_ev_chargers.value,
            // pv_size_kwp_optional:pv_size_kwp_optional.value,
            // annual_kwh_consumption_optional:annual_kwh_consumption_optional.value,
            roof_size_m2: roof_size_m2.value,
            azimuth_deg: azimuth.value,
            pitch_deg: roofpitch.value,
            // load_profile_csv:load_buildling_profile_csv.value,
        };
        building_data.push(building);
        // let bname='B'+(parseInt(building_data.length)+1);
        // //console.log('bname',bname)
        this.setState({ building_data: building_data });
    }

    updateBuildingData(newBuildingData){
        this.setState({building_data:newBuildingData});
        this.props.sendBuildingsDataToForm(newBuildingData);
    }

    deleteBuilding(buildingId) {
        let { building_data } = this.state;
        console.log("delete building called");
        let new_building_data = building_data.filter(
            (building) => building.building_id !== buildingId
        );
        console.log("new building_data", new_building_data);
        // let bname='B'+(parseInt(building_data.length)+1);
        // console.log('bname',bname)
        this.props.sendBuildingsDataToForm(new_building_data);
        this.setState({
            building_data: new_building_data,
            trigger: Math.random(),
        }); //,building_name:bname})
        console.log("building_data state", this.state.building_data);
        // this.forceUpdate();
        // this.updateAllBuildingsToForm();
    }

    toggleCompass = () => {
        let { isCompassVisible } = this.state;
        this.setState({ isCompassVisible: !isCompassVisible });
    };

    handleChange = (address) => {
        this.setState({ address });
    };

    handleSelect = (address) => {
        geocodeByAddress(address)
            .then((results) => getLatLng(results[0]))
            .then((latLng) => {
                //console.log('Success', latLng)
                this.setState({
                    address: address,
                    latLng: latLng,
                });
            })
            .catch((error) => console.error("Error", error));
    };

    handleAddressSetting = (address) => {
        geocodeByAddress(address)
            .then((results) => getLatLng(results[0]))
            .then((latLng) => {
                console.log("Success", latLng);
                this.setState({
                    address: address,
                    latLng: latLng,
                });
                document.getElementById("latitude").value = latLng.lat;
                document.getElementById("longitude").value = latLng.lng;
                this.props.handleChangeInput("pac-input");
                this.props.handleChangeInput("latitude");
                this.props.handleChangeInput("longitude");
                // let sideDetailsNextButton = document.getElementById('sideDetailsNextButton');
                // sideDetailsNextButton.disabled=false;
                // sideDetailsNextButton.addEventListener('click',this.handleNextClick);
                // //console.log('prop fun end')

                // this.props.handleChange(document.getElementById('pac-input'))
                // //console.log('address',address,latLng);
            })
            .catch((error) => console.error("Error", error));
    };

    setRoofSize(value) {
        let roofSizeEle = document.getElementById("roof_size_m2");
        //console.log('roofSizeEle',roofSizeEle)
        if (roofSizeEle !== null) {
            roofSizeEle.value = value;
        }

        return value;
    }

    updateAllChangesToForm() {
        this.props.handleChangeInput("pac-input");
        this.props.handleChangeInput("latitude");
        this.props.handleChangeInput("longitude");
    }

    updateAllBuildingsToForm() {
        console.log("LDP updating all building to form");
        let { building_data } = this.state;
        this.props.sendBuildingsDataToForm(building_data);
    }

    render() {
        let { latLng } = this.state;
        let {
            resolveApiError,
            resolveApiResponseStatus,
            free_calls,
            max_free_calls,
        } = this.props;
        let { building_data } = this.state;
        console.log(
            "location render",
            this.state,
            resolveApiResponseStatus,
            free_calls,
            max_free_calls
        );
        
        // let buildingRows = [];
        // if (building_data !== undefined && building_data.length > 0) {
        //     for (let i = 0; i < building_data.length; ++i) {
        //         //console.log('building_data',building_data)
        //         buildingRows.push(
        //             <tr id={"row" + i + 1}>
        //                 <td>{i + 1}</td>
        //                 <td>{building_data[i].building_name}</td>
        //                 <td>{building_data[i].building_type}</td>
        //                 <td>{building_data[i].azimuth_deg}&deg;</td>
        //                 <td>{building_data[i].pitch_deg}&deg;</td>
        //                 <td>
        //                     {building_data[i].roof_size_m2} m<sup>2</sup>
        //                 </td>
        //                 <td>
        //                     <img
        //                         src={deleteButton}
        //                         style={{ width: "20px" }}
        //                         onClick={(e) => {
        //                             this.deleteBuilding(
        //                                 building_data[i].building_id
        //                             );
        //                         }}
        //                         alt=""
        //                     />
        //                 </td>
        //             </tr>
        //         );
        //     }
        // }
        //console.log('buildingRows',buildingRows)
        return (
            <div>
                {resolveApiError !== undefined && resolveApiError.length > 0 && (
                    <div id="AppBanner">
                        <div class="alert alert-danger" role="alert">
                            {resolveApiError}
                        </div>
                    </div>
                )}
                {resolveApiResponseStatus === 200 &&
                    <AppBanner free_calls={max_free_calls-free_calls} max_free_calls={max_free_calls} />}
                <div class="text-center mb-4">
                    <h3>To start, tell us about your site. </h3>
                </div>
                <div class="col-lg-12">
                    <div class="row">
                        <div className="col-md-5 form-box">
                            <div class="control-label-heading title-box">
                                Site Details
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col form-question">
                                    <div>
                                        What is your address?&nbsp;
                                        <HelpModal 
                                            info={'Enter your site location using an address or post code / zip code, or select your site on the map'}
                                        />
                                    </div>

                                    <PlacesAutocomplete
                                        value={this.state.address}
                                        onChange={this.handleChange}
                                        onSelect={this.handleAddressSetting}
                                    >
                                        {({
                                            getInputProps,
                                            suggestions,
                                            getSuggestionItemProps,
                                            loading,
                                        }) => (
                                            <div>
                                                <div //id="addressInput"
                                                    className=""
                                                    style={{ width: "100%" }}
                                                >
                                                    <input
                                                        id="pac-input" //id="pac-input"
                                                        style={{
                                                            marginBottom:
                                                                "14px",
                                                        }}
                                                        {...getInputProps({
                                                            placeholder:
                                                                "Enter address here..",
                                                            className:
                                                                "location-search-input",
                                                        })}
                                                    />
                                                    {/* <span><img src={locationImg} style={{position:'absolute',right:'5px',width:'20px',}} /></span> */}
                                                </div>
                                                <div className="autocomplete-dropdown-container">
                                                    {loading && (
                                                        <div>Loading...</div>
                                                    )}
                                                    {suggestions.map(
                                                        (suggestion) => {
                                                            const className = suggestion.active
                                                                ? "suggestion-item--active"
                                                                : "suggestion-item";
                                                            // inline style for demonstration purpose
                                                            const style = suggestion.active
                                                                ? {
                                                                      backgroundColor:
                                                                          "#193A55",
                                                                      color:
                                                                          "#fff",
                                                                      cursor:
                                                                          "pointer",
                                                                  }
                                                                : {
                                                                      backgroundColor:
                                                                          "#ffffff",
                                                                      cursor:
                                                                          "pointer",
                                                                  };
                                                            return (
                                                                <div
                                                                    {...getSuggestionItemProps(
                                                                        suggestion,
                                                                        {
                                                                            className,
                                                                            style,
                                                                        }
                                                                    )}
                                                                >
                                                                    <span>
                                                                        {
                                                                            suggestion.description
                                                                        }
                                                                    </span>
                                                                </div>
                                                            );
                                                        }
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </PlacesAutocomplete>
                                    <input
                                        id="latitude"
                                        name="latitude"
                                        type="text"
                                        defaultValue={
                                            latLng !== undefined
                                                ? latLng.lat
                                                : ""
                                        }
                                        style={{ display: "none" }}
                                    />
                                    <input
                                        id="longitude"
                                        name="longitude"
                                        type="text"
                                        defaultValue={
                                            latLng !== undefined
                                                ? latLng.lng
                                                : ""
                                        }
                                        style={{ display: "none" }}
                                    />

                                    <ReactGoogleMap
                                        selectedLatLng={this.state.latLng}
                                        handleNextClick={this.handleNextClick}
                                    />
                                    <AnglePicker
                                        isCompassVisible={
                                            this.state.isCompassVisible
                                        }
                                    />
                                </div>
                            </div>
                        </div>
                        {/* <div className="col-md-1">&nbsp;</div> */}
                        <div className="col-md-6 form-box">
                            <div class="control-label-heading title-box">
                                Building Details
                            </div>

                            <div class="row pt-2">
                                <div class="col-lg-8 col-md-10 col-sm-10 col-xs-12 pl-4">
                                    <div class="form-question">
                                        What is your building name?&nbsp;
                                        <HelpModal 
                                            info={'Enter a name of each of your buildings.'}
                                        />
                                    </div>
                                    <input
                                        type="text"
                                        id="building_name"
                                        required
                                        placeholder="Enter a building name e.g. (B1, S1, Tower-1)"
                                    />
                                    <br />
                                    &nbsp;
                                    <div class="form-question">
                                        What type of building is it?&nbsp;
                                        <HelpModal 
                                            info={'Select what is the building typically used for.'}
                                        />
                                    </div>
                                    <select id="building_type" required>
                                        <option value="">
                                            --Please Select--
                                        </option>
                                        <option value="domestic">
                                            Domestic
                                        </option>
                                        <option value="work">Work</option>
                                        <option value="public">Public</option>
                                        <option value="commercial">
                                            Commercial
                                        </option>
                                        <option value="delivery">
                                            Delivery
                                        </option>
                                    </select>
                                    <br />
                                    &nbsp;
                                    <div class="form-question">
                                        Select your roof direction.&nbsp;
                                        <HelpModal 
                                            info={'Using the compass tool on the map, select the direction in which the best roof of the building is facing (prefer south-facing roofs).'}
                                        />&nbsp;<br/>
                                        <button
                                            class="btn btn-success"
                                            onClick={this.toggleCompass}
                                        >
                                            {this.state.isCompassVisible
                                                ? "Hide"
                                                : "Show"}{" "}
                                            Compass on Map
                                        </button>
                                        <br />
                                        &nbsp;
                                    </div>
                                    <input
                                        type="number"
                                        id="azimuth"
                                        ref={this.azimuthRef}
                                        onChange={this.handleAzimuthChange}
                                        style={{ width: "50px" }}
                                    />
                                    &nbsp;&deg;&nbsp;&nbsp;
                                    {this.state.roofDirectionText}
                                    <br />
                                    &nbsp;
                                    <div class="form-question">
                                        Select your roof slope.&nbsp;
                                        <HelpModal 
                                            info={'Enter the roof slope (or pitch), measured in degrees from the horizontal, using the roof angle tool.'}
                                        />
                                    </div>
                                    <div class="empty-box">
                                        <AnglePickerQuarter />
                                        <span
                                            style={{
                                                position: "relative",
                                                bottom: "10px",
                                            }}
                                        >
                                            <input
                                                id="roofpitch"
                                                type="number"
                                                style={{ width: "40px" }}
                                            />
                                            &nbsp;&deg;
                                        </span>
                                    </div>
                                    <br />
                                    &nbsp;
                                    <div class="form-question">
                                        Select your roof Size.(in m<sup>2</sup>
                                        )&nbsp; 
                                        <HelpModal 
                                            info={'Enter approximate roof size in square meters using the slider bar, then click ‘Add Building’'}
                                        />
                                    </div>
                                    <input
                                        type="number"
                                        id="roof_size_m2"
                                        defaultValue={250}
                                    />
                                    <input
                                        id="roofpitch"
                                        type="number"
                                        style={{ display: "none" }}
                                    />
                                    <div
                                        style={{
                                            width: "55%",
                                            marginLeft: "20px",
                                            marginTop: "40px",
                                        }}
                                    >
                                        <CustomSlider
                                            defaultValue={250}
                                            getAriaValueText={this.setRoofSize}
                                            aria-labelledby="track-false-range-slider"
                                            step={10}
                                            marks={this.state.roofSizeMarks}
                                            min={50}
                                            max={1000}
                                            valueLabelDisplay="on"
                                        />
                                    </div>
                                    {/* <RangeBar/> */}
                                    <br />
                                </div>
                                <div className="col-md-12">
                                    <button
                                        class="btn btn-success float-right"
                                        onClick={this.addBuilding}
                                    >
                                        Add Building
                                    </button>
                                    <br/>&nbsp;
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-1">&nbsp;</div>


                    <SiteSummaryPage 
                    showSiteSummary={this.state.showSiteSummary}
                    address={this.props.address}
                    page={'Location'}
                    building_data={this.state.building_data}
                    updateBuildingToParentPage={this.updateBuildingData}
                    />
                    {/* <div class="row">
                        <div className="col-md-12 form-box">
                            <div class="control-label-heading title-box">
                                Site Summary
                            </div>
                            <div class="table-responsive-md">
                                <table class="table table-sm table-light">
                                    <thead>
                                        <th>#</th>
                                        <th>Building Name</th>
                                        <th>Type</th>
                                        <th>Direction</th>
                                        <th>Slope</th>
                                        <th>Roof Size</th>
                                        <th>Action</th>
                                    </thead>
                                    <tbody>{buildingRows}</tbody>
                                </table>
                            </div>
                        </div>
                    </div> */}
                    <br />
                    <br />
                    <br />
                    <div class="arrowButtons">
                        <div
                            class="btn btn-success"
                            onClick={(e) => {
                                //this.updateAllChangesToForm();
                                //this.updateAllBuildingsToForm();
                                this.toggleSiteSummary();
                            }}
                        >
                            Site Summary
                        </div>
                        &nbsp;
                        <LeftArrowButton
                            onButtonClick={() => this.props.prevStep()}
                        />
                        &nbsp;
                        <RightArrowButton
                        onButtonClick={() => {
                            this.updateAllChangesToForm();
                            this.updateAllBuildingsToForm();
                            if (document.getElementById('pac-input').value==='') {
                                alert('Please select your address.'); return;
                            }
                            if (this.state.building_data.length > 0) {
                                this.props.nextStep();
                            } else {
                                window.scrollTo(0, 200);
                                document.getElementById(
                                    "building_name"
                                ).style.border = "1px solid red";}
                        }} />
                    </div>
                </div>
            </div>
        );
    }
}
