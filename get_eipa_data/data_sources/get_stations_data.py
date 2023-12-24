import pandas as pd
from io import BytesIO

from data_sources.eipa_invoice_online import eipa_invoice_data
from data_sources.eipa_public import eipa_public_data

# Export to Excel file - all sources
def export_data(
                endpoint_pools, endpoint_stations,
                eipa_email, eipa_password, eipa_token
                ):

    df_eipa_public_api = eipa_public_data(endpoint_pools, endpoint_stations)
    df_EIPA_invoice = eipa_invoice_data(eipa_email, eipa_password, eipa_token)

    # Create a BytesIO buffer to hold the Excel file
    excel_buffer = BytesIO()

    # Create an Excel writer object
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:

        # Write each DataFrame to a separate sheet
        df_eipa_public_api.to_excel(writer, sheet_name='EIPA Public API', index=False)
        df_EIPA_invoice.to_excel(writer, sheet_name='EIPA Invoice', index=False)

    return excel_buffer