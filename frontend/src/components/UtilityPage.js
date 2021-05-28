import React, { Component } from "react";
import SiteSummaryPage from "./SiteSummaryPage";
import rightArrow from "../img/right_arrow.png";
import leftArrow from "../img/left_arrow.png";
import Spinner from './Spinner';
import addFileButton from "../img/addFileButton.png";
import CustomSlider from "./CustomSlider";
import axios from "axios";
import { GENERIC_API_URL } from "../common/constants";
import LeftArrowButton from "../common/LeftArrowButton";
import RightArrowButton from "../common/RightArrowButton";
import AppBanner from "../common/AppBanner";
// import StartPage from './StartPage';
import HelpModal from './HelpModal';

export default class UtilityPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            address: "",
            isCompassVisible: true,
            building_data: [],
            hasDemandFile: false,
            hasDemandFileBldg: false,
            isUploadingDemandFile:false,
            isUploadingDemandFileBldg:false,
            fileHandle: "",
            fileHandleBldg: "",
            showSiteSummary: true,
            showBldgRemoveFileButton:false,
            annualConsumptionMarks: [
                {
                    value: 0,
                    label: `0 kWh`,
                },
                {
                    value: 10000,
                    label: "10,000 kWh",
                },
            ],
        };
        this.uploadProfile = this.uploadProfile.bind(this);
        this.removeFileAction = this.removeFileAction.bind(this);
        this.setAnnualConsumption = this.setAnnualConsumption.bind(this);
        this.updateBuilding = this.updateBuilding.bind(this);
        this.hasDemandFileChange = this.hasDemandFileChange.bind(this);
        this.hasDemandFileBldgChange = this.hasDemandFileBldgChange.bind(this);
        this.clearFileHandleBldg = this.clearFileHandleBldg.bind(this);
        this.updateBuildingDemand = this.updateBuildingDemand.bind(this);
        this.updateBuildingData = this.updateBuildingData.bind(this);
        this.removeBldgFileAction = this.removeBldgFileAction.bind(this);
    }

    componentWillMount() {
        if (
            this.props.load_profile_csv_optional !== undefined &&
            this.props.load_profile_csv_optional !== ""
        ) {
            this.setState({ hasDemandFile: true });
        }
        this.setState({ building_data: this.props.building_data });
        // setTimeout(()=>{
        // let AppHeader = document.getElementsByClassName('App-header')[0];
        // AppHeader.style.background='white';
        // },500);
    }

    toggleSiteSummary = () => {
        let { showSiteSummary } = this.state;
        this.setState({ showSiteSummary: !showSiteSummary });
    };
    
    populateAnnualConsOrDemandFile = (e) => {
        let {building_data} = this.state;
        let uplProMessageBldgEle = document.getElementById("load_profile_csv_optional_bldg_status");
        uplProMessageBldgEle.innerHTML = '';
        let datafileB1Ele= document.getElementById('datafileB1');
        let building = building_data.filter(function (building) {
            return building.building_name === e.target.value;
        });
        console.log('building found',building)
        if(building.length===0){
                uplProMessageBldgEle.innerHTML = "";
                datafileB1Ele.disabled='disabled';
                
        }else{
            console.log('building.annual_kwh_consumption_optional',building.annual_kwh_consumption_optional)
            console.log('load_profile_csv_optional_bldg_fname',building.load_profile_csv_optional_bldg_fname)
            datafileB1Ele.disabled='';
            if(building[0].annual_kwh_consumption_optional){
                document.getElementById('annual_kwh_consumption_optional').value='annual_kwh_consumption_optional'
            }
            if(building[0].load_profile_csv_optional_bldg_fname){
                uplProMessageBldgEle.innerHTML = "Uploaded "+ building[0].load_profile_csv_optional_bldg_fname;
                this.setState({showBldgRemoveFileButton:true})
            } 
        }
    }

    hasDemandFileChange = (e) => {
        //console.log('hasDemandFileChange',e.target.checked)
        this.setState({ hasDemandFile: e.target.checked });
    };

    hasDemandFileBldgChange = (e) => {
        //console.log('hasDemandFileChange',e.target.checked)
        this.setState({ hasDemandFileBldg: e.target.checked });
    };

    setAnnualConsumption(value) {
        let annualConEle = document.getElementById(
            "annual_kwh_consumption_optional"
        );
        if (annualConEle !== null) {
            annualConEle.value = value;
        }

        return value;
    }

    clearFileHandleBldg() {
        this.setState({ fileHandleBldg: "" });
    }

    async uploadProfile(e, type) {
        let isBuilding = type === "site" ? false : true;
        console.log("uploadprofile", this.props, isBuilding, type);
        // this.setState({isUploadingFile:true});
        var bodyFormData = new FormData();
        var fileEle ='';
        var fileToUpload = e.target.files[0]; //document.getElementById('datafile').value;
        var fileToUploadName = '';
        if(fileToUpload) {fileToUploadName = fileToUpload.name; }    
        // console.log('before upload fileToUpload',this.props,fileToUpload,e.target)
        bodyFormData.append("file", fileToUpload);
        bodyFormData.append("lat", this.props.latitude);
        bodyFormData.append("lon", this.props.longitude);
        // console.log('before upload form',bodyFormData)
        if (isBuilding) {
            this.setState({ isUploadingDemandFileBldg: true });
            fileEle = document.getElementById("load_profile_csv_optional_bldg")
        } else {
            this.setState({ isUploadingDemandFile: true });
            fileEle = document.getElementById("load_profile_csv_optional")
        }
        await axios({
            method: "post",
            url: GENERIC_API_URL + "upload",
            data: bodyFormData,
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(function (response) {
                //handle success
                console.log("upload response", response.data.handle);
                fileEle.value = response.data.handle;
                if (isBuilding) {
                    let uplProMessageBldgEle = document.getElementById(
                        "load_profile_csv_optional_bldg_status"
                    );
                    uplProMessageBldgEle.innerHTML = "Uploaded "+ fileToUploadName; //+response.data.handle;
                } else {
                    let uplProMessageEle = document.getElementById(
                        "load_profile_csv_optional_status"
                    );
                    uplProMessageEle.innerHTML = "Uploaded "+ fileToUploadName; //+response.data.handle;
                    let uplSiteFileNameEle = document.getElementById("load_profile_csv_optional_site_fname");
                    uplSiteFileNameEle.value=fileToUploadName;
                    document.getElementById('hasDemandFileBldg').disabled='disabled';
                }
            })
            .catch(function (error) {
                //handle error
                // console.log('upload response err',error.response);
                if (error.response !== undefined) {
                    if (isBuilding) {
                        let uplProMessageBldgEle = document.getElementById(
                            "load_profile_csv_optional_bldg_status"
                        );
                        uplProMessageBldgEle.innerHTML =
                            "Error Occurred! " + error.response.data.error;
                    } else {
                        let uplProMessageEle = document.getElementById(
                            "load_profile_csv_optional_status"
                        );
                        uplProMessageEle.innerHTML =
                            "Error Occurred! " + error.response.data.error;
                    }
                }
            });
        if (isBuilding) {
            this.setState({ fileHandleBldg: fileEle.value,fileBldgName:fileToUploadName,isUploadingDemandFileBldg:false,showBldgRemoveFileButton:true });
        } else {
            this.setState({ fileHandle: fileEle.value,fileSiteName:fileToUploadName,isUploadingDemandFile:false });
        }
        // this.forceUpdate();
        // console.log('upload success',this.state.fileHandle);
    }

    removeFileAction() {
        this.setState({ fileHandle: "" });
        document.getElementById("load_profile_csv_optional").value = "";
        this.props.handleChangeInput("load_profile_csv_optional");
        let uplProMessageEle = document.getElementById(
            "load_profile_csv_optional_status"
        );
        uplProMessageEle.innerHTML=''
    }

    removeBldgFileAction() {
        let {building_data} = this.state;        
        let uplProMessageEle = document.getElementById(
            "load_profile_csv_optional_bldg_status"
        );
        uplProMessageEle.innerHTML=''
        console.log("upd building_data", building_data);
        var building = building_data.filter(function (building) {
            let selectedBuildingEle = document.getElementById(
                "building_list_up"
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
        delete building[0].load_profile_csv_optional_bldg;
        delete building[0].load_profile_csv_optional_bldg_fname;
        this.setState({building_data:building_data,showBldgRemoveFileButton:false,fileHandleBldg:''});
        console.log('bldg with removed file',building,building_data)
        this.updateBuildingData(building_data);

    }

    updateBuildingData(newBuildingData){
        this.setState({building_data:newBuildingData});
        this.props.sendBuildingsDataToForm(newBuildingData);
    }

    updateBuildingDemand() {
        let { fileHandleBldg } = this.state;
        if (fileHandleBldg !== "") {
            this.updateBuilding("load_profile_csv_optional_bldg", fileHandleBldg);
            this.updateBuilding("load_profile_csv_optional_bldg_fname", this.state.fileBldgName);
        } else {
            let annualConEle = document.getElementById(
                "annual_kwh_consumption_optional"
            );
            if (annualConEle !== null) {
                this.updateBuilding(
                    "annual_kwh_consumption_optional",
                    annualConEle.value
                );
            }
        }
        this.updateAllBuildingsToForm();
    }

    updateBuilding(field, value) {
        let { building_data } = this.props;
        console.log("upd building_data", building_data);
        var building = building_data.filter(function (building) {
            let selectedBuildingEle = document.getElementById(
                "building_list_up"
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
        // console.log("building", building);
        if (building !== null && building.length > 0) {
            building[0][field] = value;
        }
    }

    updateAllChangesToForm() {
        this.props.handleChangeInput("import_cost_kwh");
        this.props.handleChangeInput("export_price_kwh");
        this.props.handleChangeInput("load_profile_csv_optional");
        this.props.handleChangeInput("load_profile_csv_optional_site_fname");
    }

    updateAllBuildingsToForm() {
        console.log("UP updating all building to form");
        let { building_data } = this.state;
        this.props.sendBuildingsDataToForm(building_data);
    }

    render() {
        let { hasDemandFile, hasDemandFileBldg } = this.state;
        let {
            building_data,
            resolveApiError,
            resolveApiResponseStatus,
            free_calls,
            max_free_calls,
        } = this.props;
        // console.log('utility step',this.props,this.state)
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
        // console.log('buildingOptions',buildingOptions)
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
                    <h3>Now, tell us about your existing utilities. </h3>
                </div>

                <div class="col-lg-12" style={{ background: "transparent" }}>
                    <div class="row">
                        <div
                            className="col-md-3 form-box"
                            style={{ marginRight: "10px" }}
                        >
                            <div class="control-label-heading title-box">
                                Electricity Costs
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col form-question">
                                    <div>
                                        What is electricity cost per unit?&nbsp;
                                        <HelpModal
                                            info='Enter the price you pay your electricity supplier per unit in your local currency. You can find this information on your energy bills. If you pay a dual or variable tariff, then enter an average estimated value here.'
                                        />
                                    </div>
                                    <input
                                        type="number"
                                        id="import_cost_kwh"
                                        step="0.01"
                                        defaultValue={
                                            this.props.import_cost_kwh !==
                                                undefined
                                                ? this.props.import_cost_kwh
                                                : 0.14
                                        }
                                    />
                                    <br />
                                    &nbsp;
                                    <div>
                                        What is your export tariff?&nbsp;
                                        <HelpModal
                                            info='Export tariff is a bonus payment for every unit of surplus electricity your system exports to the electricity grid'
                                        />
                                    </div>
                                    <input
                                        type="number"
                                        id="export_price_kwh"
                                        placeholder="1.0"
                                        step="0.01"
                                        defaultValue={
                                            this.props.export_price_kwh !==
                                                undefined
                                                ? this.props.export_price_kwh
                                                : 0.04
                                        }
                                    />
                                </div>
                            </div>
                        </div>
                        {/* <div className='col-md-1'>
                            &nbsp;
                        </div>     */}
                        <div
                            className="col-md-4 form-box"
                            style={{ marginRight: "10px" }}
                        >
                            <div class="control-label-heading title-box">
                                Electricity Demand for entire site
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col">
                                    <div class="form-question">
                                        Do you have your site demand file?&nbsp;
                                        <HelpModal
                                            info='If you have a smart meter installed by your energy supplier at your site, then you can obtain a csv file of your energy consumption from the meter and upload here. Your energy supplier can help you get this file in case you do not have it. Most standard half-hourly billing formats are accepted.'
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
                                                id="hasDemandFile"
                                                onChange={
                                                    this.hasDemandFileChange
                                                }
                                                defaultChecked={
                                                    this.state.hasDemandFile
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
                                    <div
                                        class="demandFileBox"
                                        style={{
                                            display: hasDemandFile
                                                ? "block"
                                                : "none",
                                        }}
                                    >
                                        <input
                                            type="file"
                                            style={{ display: "none" }}
                                            id="datafileB"
                                            name="datafileB"
                                            onChange={(e) => {
                                                this.uploadProfile(e, "site");
                                            }}
                                        />
                                        <label
                                            id="uploadBuildingProfileBtn"
                                            style={{
                                                width: "100%",
                                                margin: "0px",
                                                padding: "0px",
                                                cursor: "pointer",
                                            }}
                                            htmlFor="datafileB"
                                        >
                                            <input
                                                id="load_profile_csv_optional"
                                                type="text"
                                                defaultValue={
                                                    this.props
                                                        .load_profile_csv_optional
                                                }
                                                style={{ display: "none" }}
                                            />
                                            <input
                                                id="load_profile_csv_optional_site_fname"
                                                type="text"
                                                defaultValue={
                                                    this.props
                                                        .load_profile_csv_optional_site_fname
                                                }
                                                style={{ display: "none" }}
                                            />
                                            <img
                                                src={addFileButton}
                                                style={{ width: "100px" }}
                                                alt=""
                                            />
                                            <br />
                                            Add your site demand file
                                        </label>
                                        <span id="load_profile_csv_optional_status">
                                            {this.props
                                                .load_profile_csv_optional !==
                                                undefined &&
                                                this.props
                                                    .load_profile_csv_optional !==
                                                ""
                                                ? "File Already Uploaded " + this.props
                                                .load_profile_csv_optional_site_fname
                                                : ""}
                                        </span>
                                        {this.state.fileHandle &&
                                            <div>
                                                <button
                                                    class="btn btn-sm btn-success pull-right"
                                                    onClick={this.removeFileAction}
                                                >
                                                    Remove File
                                                </button>
                                            </div>
                                        }
                                        <Spinner 
                                        isLoading={this.state.isUploadingDemandFile}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                        {/* <div className='col-md-1'>
                            &nbsp;
                        </div>     */}
                        <div className="col-md-4 form-box">
                            <div class="control-label-heading title-box">
                                Electricity Demand for each building
                            </div>

                            <div class="row" style={{ padding: "10px" }}>
                                <div class="col">
                                    <div class="form-question">
                                        Do you have your building demand
                                        file?&nbsp;
                                        <label
                                            class="switch"
                                            style={{
                                                position: "absolute",
                                                right: "10px",
                                            }}
                                        >
                                            <input
                                                type="checkbox"
                                                id="hasDemandFileBldg"
                                                onChange={
                                                    this.hasDemandFileBldgChange
                                                }
                                                disabled={this.props
                                                    .load_profile_csv_optional}
                                            />
                                            <span
                                                class="slider"
                                                style={{ color: "white" }}
                                            >
                                                &nbsp;&#10004;
                                            </span>
                                        </label>
                                    </div>
                                    {/* <input type='text' id='building_name' /> */}
                                    &nbsp;&nbsp;
                                    <HelpModal
                                            info='Upload electricity consumption files for each of your buildings if available, as a csv file. Most standard half-hourly billing formats are accepted.'
                                    />
                                    <br />
                                    
                                    &nbsp;
                                    <div class="form-question">
                                        Select your building&nbsp;
                                        <HelpModal
                                            info='If you don’t have the smart meter demand files for your site or your buildings, then enter your approximate annual consumption for each building. Select the relevant building from dropdown and then click Add.'
                                        />
                                    </div>
                                    <select id="building_list_up"
                                        onChange={this.populateAnnualConsOrDemandFile}
                                    >
                                        <option value="">
                                            --Please Select--
                                        </option>
                                        {buildingOptions}
                                    </select>
                                    <div
                                        class="form-question"
                                        style={{
                                            display: !hasDemandFileBldg
                                                ? "block"
                                                : "none",
                                        }}
                                    >
                                        Annual Consumption
                                        <br />
                                        <input
                                            id="annual_kwh_consumption_optional"
                                            type="number"
                                            style={{ width: "70px" }}
                                            defaultValue={
                                                this.props
                                                    .annual_kwh_consumption_optional !==
                                                    undefined
                                                    ? this.props
                                                        .annual_kwh_consumption_optional
                                                    : 2400
                                            }
                                        />{" "}
                                        kWh
                                        <div style={{ width: "100%" }}>
                                            {/* <span style={{width:'10%'}}>0 kWh</span> */}
                                            <span>
                                                <div
                                                    style={{
                                                        width: "65%",
                                                        marginLeft: "20px",
                                                        marginTop: "40px",
                                                    }}
                                                >
                                                    <CustomSlider
                                                        defaultValue={2400}
                                                        getAriaValueText={
                                                            this
                                                                .setAnnualConsumption
                                                        }
                                                        aria-labelledby="track-false-range-slider"
                                                        step={10}
                                                        marks={
                                                            this.state
                                                                .annualConsumptionMarks
                                                        }
                                                        min={0}
                                                        max={10000}
                                                        valueLabelDisplay="on"
                                                        onChange={
                                                            this
                                                                .clearFileHandleBldg
                                                        }
                                                    />
                                                </div>
                                            </span>
                                        </div>
                                    </div>
                                    <div
                                        class="demandFileBoxForBuilding"
                                        style={{
                                            display: hasDemandFileBldg
                                                ? "block"
                                                : "none",
                                        }}
                                    >
                                        <br />
                                        <input
                                            type="file"
                                            style={{ display: "none" }}
                                            id="datafileB1"
                                            name="datafileB1"
                                            disabled='disabled'
                                            onChange={(e) => {
                                                this.uploadProfile(
                                                    e,
                                                    "building"
                                                );
                                            }}
                                        />
                                        <label
                                            id="uploadBuildingProfileBtn1"
                                            style={{
                                                width: "100%",
                                                margin: "0px",
                                                padding: "0px",
                                                cursor: "pointer",
                                            }}
                                            htmlFor="datafileB1"
                                        >
                                            <input
                                                id="load_profile_csv_optional_bldg"
                                                type="text"
                                                // defaultValue={
                                                //     this.props
                                                //         .load_profile_csv_optional
                                                // }
                                                style={{ display: "none" }}
                                            />
                                            <img
                                                src={addFileButton}
                                                style={{ width: "100px" }}
                                                alt=""
                                            />
                                            <br />
                                            Add your building demand file
                                        </label>
                                        <span id="load_profile_csv_optional_bldg_status"></span>
                                    <Spinner 
                                        isLoading={this.state.isUploadingDemandFileBldg}
                                        />
                                        {this.state.showBldgRemoveFileButton &&
                                            <div>
                                                <button
                                                    class="btn btn-sm btn-success pull-right"
                                                    onClick={this.removeBldgFileAction}
                                                >
                                                    Remove File
                                                </button>
                                            </div>
                                        }    
                                    </div>
                                    <button
                                        class="btn btn-sm btn-success pull-right"
                                        onClick={this.updateBuildingDemand}
                                    >
                                        Add
                                    </button>
                                    <br />
                                </div>
                            </div>
                        </div>
                    </div>
                    <SiteSummaryPage
                        showSiteSummary={this.state.showSiteSummary}
                        address={this.props.address}
                        page={'Utility'}
                        building_data={this.state.building_data}
                        updateBuildingToParentPage={this.updateBuildingData}
                    />

                    <br />
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
                            onButtonClick={(e) => {
                                this.updateAllChangesToForm();
                                this.updateAllBuildingsToForm();
                                this.props.prevStep();
                            }}
                        />
                        {/* <img src={leftArrow} alt='' onClick={(e)=>{
                    }}
                style={{width:'35px',padding:'10px',background:'#FAFAFA',border:'1px solid #F1F9FF',borderRadius:'20%',cursor:'pointer',
                      }}
            /> */}
                        &nbsp;
                        <RightArrowButton
                            onButtonClick={(e) => {
                                this.updateAllChangesToForm();
                                this.updateAllBuildingsToForm();
                                this.props.nextStep();
                            }}
                        />
                        {/* <img src={rightArrow} alt='' onClick={(e)=>{ this.updateAllChangesToForm();this.updateAllBuildingsToForm()
                        this.props.nextStep()
                    }}
                style={{width:'35px',padding:'10px',background:'#4DA858',borderRadius:'20%',cursor:'pointer',
                      }}
            /> */}
                    </div>
                </div>
            </div>
        );
    }
}
