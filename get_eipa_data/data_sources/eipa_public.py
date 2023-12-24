import requests
import pandas as pd

# Get stations from EIPA
def eipa_public_data(endpoint_pools, endpoint_stations):

    # Get stations from EIPA public
    headers = {
        "Content-Type": "application/json"
    }
    
    # GET pools and stations from api
    get_eipa_public_pools = requests.get(endpoint_pools, headers=headers).json()
    get_eipa_public_stations = requests.get(endpoint_stations, headers=headers).json()

    # Convert to dataframe and merge
    df_eipa_pools = pd.json_normalize(get_eipa_public_pools, record_path=['data'])
    df_eipa_stations = pd.json_normalize(get_eipa_public_stations, record_path=['data'])

    df_eipa_public_api = pd.merge(df_eipa_pools, df_eipa_stations, how='right', left_on='id', right_on='pool_id')

    # Replace name to get Friendly Code
    df_eipa_public_api['code'] = df_eipa_public_api['code'].str.replace(r'PL-7R5-P', '')
    
    return df_eipa_public_api