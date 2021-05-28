import React,{Component} from 'react';
import deleteButton from '../img/deleteButton.png';

export default class SiteSummaryPage extends Component{

    constructor(props){
        super(props);
        this.state={
            address:'',
            isCompassVisible:true,
            building_data:[],           
          };     
          this.deleteBuilding=this.deleteBuilding.bind(this);

    }

    componentWillMount(){
        console.log('componentWillMount SSP')
        this.setState({building_data:this.props.building_data, 
                        address:this.props.address,
                        trigger:Math.random()})
    }
    
    getDirection = (angle) => {
      var directions = ['North', 'North-East', 'East', 'South-East', 'South', 'South-West', 'West', 'North-West'];
      return directions[Math.round(((angle %= 360) < 0 ? angle + 360 : angle) / 45) % 8];
  }

    deleteBuilding(buildingId){
        let {building_data}=this.state;
        console.log('delete building called')
        let new_building_data=building_data.filter(building=> building.building_id !== buildingId);
        console.log('new building_data',new_building_data)
        // let bname='B'+(parseInt(building_data.length)+1);
        // console.log('bname',bname)
        this.props.updateBuildingToParentPage(new_building_data)
        this.setState({building_data:new_building_data,trigger:Math.random()});//,building_name:bname})
        console.log('building_data state',this.state.building_data)
        // this.forceUpdate();
        // this.updateAllBuildingsToForm();
    }

    render(){
        let {building_data,showSiteSummary} = this.props;
        let buildingRows=[];
        let hasBldgFileHandle = false
        if(building_data!==undefined && building_data.length>0){
          for(let i=0;i<building_data.length;++i){
            hasBldgFileHandle = building_data[i].load_profile_csv_optional_bldg!==undefined
            if(hasBldgFileHandle) break;
          }

          for(let i=0;i<building_data.length;++i){
            //console.log('building_data',building_data)
            let consumption = building_data[i].annual_kwh_consumption_optional;
            //bldgFileHandle = building_data[i].load_profile_csv_optional_bldg;
            let bldgFileName = building_data[i].load_profile_csv_optional_bldg_fname;
            buildingRows.push(
              <tr  id={'row'+i+1}>
                <td >{i+1}</td>
                <td>{building_data[i].building_name}</td>
                <td>{building_data[i].building_type}</td>
                <td>{building_data[i].azimuth_deg}&deg;&nbsp;{this.getDirection(building_data[i].azimuth_deg)}</td>
                <td>{building_data[i].pitch_deg}&deg;</td>
                <td>{building_data[i].roof_size_m2} m<sup>2</sup></td>
                <td>{consumption} {consumption && <span>kWh</span>}</td>
                {hasBldgFileHandle && <td>{bldgFileName}</td> }
                <td>{building_data[i].num_ev_chargers}</td>
                <td><img src={deleteButton} style={{width:'20px'}} onClick={(e)=>{this.deleteBuilding(building_data[i].building_id);
                                                                                }} 
                        alt=''  />
                </td>
              </tr>
            );
          }
        }
        //console.log('buildingRows',buildingRows)
        return(
              <div class='col-lg-12' id='SiteSummary' style={{display:showSiteSummary?'block':'none',background:'transparent'}} >
                    <div class="row">
                    {this.props.address && 'Location : '+ this.props.address }
                      <div className='col-md-11 form-box'>
                        <div class="control-label-heading title-box">
                        Site Summary
                        </div>
                        <div class="table-responsive-md">
                          <table class='table table-sm table-light' >
                          <thead>
                          <th>#</th>
                              <th>Building Name</th>
                              <th>Type</th>
                              <th>Direction</th>
                              <th>Slope</th>
                              <th>Roof Size</th>
                              <th>Annual Consumption</th>
                              {hasBldgFileHandle && <th>Building Demand File</th> }
                              <th>No. EV Chargers</th>
                              <th>Action</th>
                          </thead>
                          <tbody>
                              {buildingRows}
                          </tbody>
                          </table>
                          </div>
                      </div>    
                <br/><br/><br/>
                </div>
              </div>
            );
    }
} 