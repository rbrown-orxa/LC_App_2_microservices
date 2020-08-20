

def list_buildings(query):
    building_loads = {}
    print(type(query))
    print('number of buildings: ',  len(query['building_data']) )
    for building in query['building_data']:
        # print('\n', building, end='\n\n')
        if building['load_profile_csv_optional']:
            print( f"building: {building['name']} refers to a load file:",
                    f" {building['load_profile_csv_optional']} ")
            building_loads[ building['name'] ] = building['load_profile_csv_optional']
        else:
            print( f"building: {building['name']} needs generic load:",
                    f" profile type: {building['building_type']} ",
                    f" annual consumption in kWh: "
                    f"{building['annual_kwh_consumption_optional']}")
            # make a temporary file from get_consumption_profile()

            # store it's handle in building_loads
    return building_loads

