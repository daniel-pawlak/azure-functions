import logging, os

import azure.functions as func

from data_sources.get_stations_data import export_data


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    endpoint_pools = os.getenv('endpointpools')
    endpoint_stations = os.getenv('endpointstations')

    eipa_email = os.getenv('eipauser')
    eipa_password = os.getenv('eipapassword')
    eipa_token = os.getenv('eipatoken')
    
    data = export_data(endpoint_pools, endpoint_stations,
                       eipa_email, eipa_password, eipa_token
                       )


    return func.HttpResponse(
        data.getvalue(),
        headers={"Content-Disposition": 'attachment; filename="test.xlsx"'},
        mimetype='application/vnd.ms-excel',
        status_code=200,
    )