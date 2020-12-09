#!/usr/bin/env python
# coding: utf-8

# # Calculation of new load profile: base load + EV load

# In[1]:


#import notebook
import nbimporter
import load_allocation
import ev_profile
import pv_optimiser
import pandas as pd


# In[ ]:





# # Functions

# In[2]:


def optimise_aggregated_load(req,method="aggr"):
    """
    Sum base load optimised for each building based on the PV size and aggregate base load with ev load for each building
    request: the dict-like request object passed by Flask
    method: String with value 1) aggr: Optimisation by aggregated load 2) roofeff: optimisation by roof efficiency
    Returns: sum of aggregated loads
    
    """
    
    fixed_fields = ['lon', 'lat', 'cost_per_kWp', 'import_cost', 'export_price','expected_life_yrs']
    variable_fields = ['roof_size_m2', 'azimuth', 'roofpitch']
    
    #Initialise form data
    form_data = {}
    
    #Get form data dictionary items
    form_data = load_allocation.get_form_data(req,fixed_fields,variable_fields)
    
    if method == "aggr":
        optimal_size,base_load,building_type,no_of_charge_points = load_allocation.pv_aggregated_load_profile_optimiser(req)
    else:
        optimal_size,base_load,building_type,no_of_charge_points = load_allocation.pv_allocate_size_by_roof_eff_optimiser(req)
    aggr_load_kw = []
    
    for load, charge_points in zip(base_load, no_of_charge_points):
        start_date = load.sort_index(ascending=True).index[0].date()
        ev_load = ev_profile.get_ev_profile(building_type,0.2,start_date,charge_points)
        tmp_aggr_load = load.add(ev_load,fill_value=0)
        aggr_load_kw.append(tmp_aggr_load)
      
    #Optimse aggregated load
    
    #Get generation for 1Kw
    generation_1kw = _generation_1kw(aggr_load_kw,form_data)
    
    #Get optimsed PV size
    optimal_size = _optimise_pv_size(generation_1kw,aggr_load_kw,form_data)
    
    return(optimal_size,generation_1kw,aggr_load_kw)    


# In[2]:


def aggregate_building_load_and_generation(req):
    """
    Sum aggregated load of all building and PV generation
    request: the dict-like request object passed by Flask
    Returns: Pandas dataframe Total building load as p_load and Total generation as p_gen
    
    """
    #Call function to get list of optimal pv size, generation 1kw, aggregated load for each building
    optimal_pv_size_kwp,generation_1kw,aggregated_load_kw = optimise_aggregated_load(req)
    
    #Initailise pandas dataframe
    p_load = pd.DataFrame()
    p_gen_1k_sum = pd.DataFrame()
    
    #Iterate over aggregated_load_kw
    for load in aggregated_load_kw:
        p_load = load.add(p_load,fill_value=0)
        
    #Iterate over generation_1kw
    for gen in generation_1kw:
        p_gen_1k_sum = gen.add(p_gen_1k_sum,fill_value=0)
        
    #calculate mean of p_gen_1k
    p_gen_1k_mean = p_gen_1k_sum /len(generation_1kw)
    
    #calculate total generation
    p_gen = p_gen_1k_mean * sum(optimal_pv_size_kwp)
    
    #Rename the column
    p_gen = p_gen.rename(columns={'1kWp_generation_kw':f'{round(sum(optimal_pv_size_kwp),2)}_1kWp_generation_kwh'})
    
    return(p_load,p_gen)
    


# # Helper Functions

# In[3]:


def _generation_1kw(aggr_load,form_data):
    
    """
    Generation 1Kw based on the aggregated load
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    #Get lat/lon
    lat, lon = float(form_data['lat']), float(form_data['lon'])
    
    #Get list of roof size, roof pitch, azimuth
    roof_size_m2, roofpitch, azimuth = ( form_data['roof_size_m2'].copy(),
                                        form_data['roofpitch'].copy(),
                                        form_data['azimuth'].copy() )
    generation_1kw = [] # list of df
    
    for load, roofpitch, azim in zip(aggr_load, roofpitch, azimuth): 
        tmp_gen = pv_optimiser.generation_1kw(lat, lon, load, roofpitch, azimuth=azim)
        generation_1kw.append(tmp_gen) # list of df
        
    return(generation_1kw)


# In[4]:


def _optimise_pv_size(generation_1kw,aggr_load,form_data):
    
    """
    optimise PV size based on the aggregated load
    
    generation_1kw: hourly generation in kWh per kWp installed capacity
    form_data: the dict-like data processed from request
    aggr_load: list of Sum of base load and aggregated load
    Returns: Generation 1kw
    
    """
    
    cost_per_kWp = float(form_data['cost_per_kWp'])
    import_cost = float(form_data['import_cost'])
    export_price = float(form_data['export_price'])
    expected_life_yrs = float(form_data['expected_life_yrs'])
    panel_efficiency = 0.18 # https://www.solar.com/learn/solar-panel-efficiency/
    
    roof_size_m2 = form_data['roof_size_m2'].copy()

    optimal_size = []

    # for index in range(num):
    for gen_1_kw, load_kw, roof_size_m2 in zip(
            generation_1kw, aggr_load, roof_size_m2):
        df_cost_curve = pv_optimiser.cost_curve(
                                generation_1kw=gen_1_kw,
                                load_kwh=load_kw,
                                cost_per_kWp=cost_per_kWp,
                                import_cost=import_cost,
                                export_price=export_price,
                                expected_life_yrs=expected_life_yrs,
                                roof_size_kw=roof_size_m2 * panel_efficiency)

        tmp_opt_size, optimal_revenue = pv_optimiser.optimise(df_cost_curve) #float, float        
        optimal_size.append(tmp_opt_size)  
    
    return(optimal_size)


# In[ ]:





# optimise_aggregated_load()

# In[ ]:




