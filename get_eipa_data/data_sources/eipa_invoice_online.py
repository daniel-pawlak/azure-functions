import pandas as pd
import requests
import pdfplumber
import io

# Get stations from EIPA Invoice
def eipa_invoice_data(email, password, token):

    def authentication(headers, params, api_url):
        """
        This code is used to authenticate API Token and receive an access token together with refresh token. Access token is valid for 5 minutes,
        after that it has to be refreshed with usage of refresh token which is valid 30 minutes. Authentication allows user to use eUdt API.
        """

        response = requests.post(api_url, headers = headers, json=params)

        access_token = response.json()["accessToken"]
        authorization = f'Bearer {access_token}'

        refresh_token = response.json()["refreshToken"]

        return authorization, refresh_token

    def logging():
        """
        This code serves for keeping the logging credentials and headers in one place.
        """

        headers = {
        "Content-Type": "application/json",
        "X-Api-Token": token,
        }

        params = {
        "login": email,
        "password": password
        }

        return headers, params, token

    def get_access(api_url):
        """
        This code is created to get access to eUDT api.
        """
        headers, params, token = logging()

        authorization, refresh_token = authentication(headers, params, api_url)

        return authorization, refresh_token, token

    def refresh_the_token(api_url, refresh_token, token):
        """
        This code is used to refresh access_token. It is valid for 30 minutes, after that main token has to be authenticated again.
        """

        headers = {
        "Content-Type": "application/json",
        "X-Api-Token": token,
        }
        params = {
            "refreshToken" : refresh_token
        }

        response = requests.put(api_url, headers = headers, json=params)
        refreshed_access_token = response.json()['accessToken']
        authorization = f'Bearer {refreshed_access_token}'
        
        return authorization, refreshed_access_token

    def get_data_from_api(api_url, authorization, token):
        """
        This code is created to get data from eUDT API.
        """

        headers = {
                    "Authorization" : authorization,
                    "X-Api-Token": token
                    }
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.content
            return data
        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return None

    def open_site(authorization, url=None, querystring=""):
        """
        This code is created to take information about the devices from eUDT site.
        """

        payload = ""
        headers = {
        "authority": "api.eudt.gov.pl",
        "accept": "application/json, text/plain, */*",
        "accept-language": "pl,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "cache-control": "no-cache",
        "cookie": "",
        "expires": "0",
        "origin": "https://eudt.gov.pl",
        "pragma": "no-cache",
        "sec-ch-ua": "^\^Chromium^^;v=^\^112^^, ^\^Microsoft",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "^\^Windows^^",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "x-context": "32283",
        "x-xsrf-token": "YmRlM2ZmNThiMGVlYmE2NmUxN2FjNDZlZjkzMmQxOGQyMDk5MGQ0NjdjNjNmOGJjOTJiMTI4MWMxMmJlNzEwODthOGM1YzZlOS0xNTVjLTRmMTQtOTc4Ni1jNDcwYTVjMTg3ZDc=",
        "Authorization" : authorization
        }
        if url:
            url = url
        else:
            url = "https://api.eudt.gov.pl/Device"

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

        return response.json()['data']

    def get_invoice_id(api_url, refresh_token, token):
        """
        This is the main function which serves to get all invoices on specific requirements. User can choose how many invoices should be downloaded, 
        what is the minimum value on te invoice, how to sort the invoices.
        It takes just 3 positional arguments, api_url is predefined, refresh_token is taken from get_access function,
        token is given from eUDT.
        """

        # take data from eUDT site. Try to get it directly, if not available, then refresh the token, 
        # if token is not valid anymore, authorize it again
        # it t
        url = "https://api.eudt.gov.pl/FinancialDocument"
        querystring = {"sorting.fieldName":"Date","sorting.direction":"2","rowsRange.skip":"0","rowsRange.take":"25", "amount.value":"5000", "amount.operator": "2"}
        
        try:
            data = open_site(authorization, url, querystring)
        except:
            try:
                print("refreshing token")
                authorization = refresh_the_token(api_url, refresh_token, token)
                data = open_site(authorization, url, querystring)
            except:
                print("get the new token")
                authorization, refresh_token, token = get_access(api_url)
                data = open_site(authorization, url, querystring)   

        return data 

    def get_invoice(authorization, api_url, refresh_token, token, id):
        """
        This is the main function which serves to download latest invoice.
        It takes just 4 positional arguments, api_url is predefined, refresh_token is taken from get_access function,
        token is given from eUDT, id is a result of get_invoice_id function. Id is variable which contains the id of 
        document which will be downloaded.
        """
        # take data from eUDT site. Try to get it directly, if not available, then refresh the token, if token is not 
        # valid anymore, authorize it again
        url = f"https://api.eudt.gov.pl/FinancialDocument/{id}/File"

        try:
            print("refreshing token")
            authorization, refreshed_access_token = refresh_the_token(api_url, refresh_token, token)
            data = get_data_from_api(url, authorization, token)
        except:
            print("get the new token")
            authorization, refresh_token, token = get_access(api_url)
            data = get_data_from_api(url, authorization, token)  

        return data     

    def save_invoice():
        api_url = "https://api.eudt.gov.pl/token"
        authorization, refresh_token, token = get_access(api_url)

        data = get_invoice_id(api_url, refresh_token, token)
        id = data[0]['id']

        response = get_invoice(authorization, api_url, refresh_token, token, id)

        return response

    # Get stations from EIPA Invoice
    def extract_tables_from_pdf(pdf_path):
        with pdfplumber.open(io.BytesIO(pdf_path)) as pdf:
            all_tables = []

            for page in pdf.pages:

                shortest_line = [int(line["bottom"]) for line in page.lines]
                shortest_line = sorted(list(set(shortest_line)))

                if len(shortest_line) > 0:
                    tables = page.extract_tables({"explicit_horizontal_lines": [ shortest_line[-1]]})
                    
                    all_tables.extend(tables)
                
        return all_tables

    def convert_to_dataframe(all_tables):
        dfs = []
        for table in all_tables:
            df = pd.DataFrame(table[1:], columns=table[0])
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)

    def get_data_from_invoice(pdf_file_path):

        all_extracted_tables = extract_tables_from_pdf(pdf_file_path)
        df_eipa_invoice = convert_to_dataframe(all_extracted_tables)

        df_eipa_invoice.columns = ['Lp.', 'Nr oddz.', 'Usługa', 'Informacje dodatkowe', 'Zlecenie',
                                    'Czynność', 'Data wykonania', 'Ilość', 'J.M.', 'Stawka', 'Wartość']

        # replace NaN with empty value
        df_eipa_invoice['Data wykonania'] = df_eipa_invoice['Data wykonania'].fillna('')

        # clear data
        df_eipa_invoice = df_eipa_invoice.loc[~df_eipa_invoice['Data wykonania'].str.contains('wykonania')]

        # Prepare index - forward fill, change column type, and set as index
        df_eipa_invoice['Lp.'] = df_eipa_invoice['Lp.'].ffill()
        df_eipa_invoice['Lp.'] = df_eipa_invoice['Lp.'].astype(int)
        df_eipa_invoice.set_index('Lp.')

        # replace all NaN with empty value
        df_eipa_invoice.fillna('', inplace=True)

        # change column names to match these from invoice
        df_eipa_invoice = df_eipa_invoice.rename(columns={'Nr': 'Nr oddz.', 'Data': 'Data wykonania'})

        # change data types of columns to prepare them for aggregation in next steps
        df_eipa_invoice['Ilość'] = df_eipa_invoice['Ilość'].astype(str)
        df_eipa_invoice['Stawka'] = df_eipa_invoice['Stawka'].astype(str)
        df_eipa_invoice['Wartość'] = df_eipa_invoice['Wartość'].astype(str)

        # tell how columns should be aggregated
        agg_dict = {
            'Nr oddz.': ''.join, 
            'Informacje dodatkowe': ' '.join, 
            'Zlecenie': ''.join, 
            'Czynność': ''.join, 
            'Data wykonania': ' '.join,
            'Ilość': ''.join,
            'J.M.': ''.join,
            'Stawka': ''.join,
            'Wartość': ''.join,
        }

        # aggregate columns basing on index value
        df_EIPA_invoice = df_eipa_invoice.groupby('Lp.').agg(agg_dict)

        # Unhash if you want to extract Friendly Codes of your stations

        # # Create new column with EtrelFriendlyCode basing on data from Informacje dodatkowe column
        # df_EIPA_invoice['EtrelFriendlyCode'] = df_EIPA_invoice['Informacje dodatkowe'].str.replace('\n', ' ').str.replace(' ', '')
        # df_EIPA_invoice['EtrelFriendlyCode'] = df_EIPA_invoice['EtrelFriendlyCode'].str.extract(r'.*?\b(PL-7R5-EL?\d+\b)[^P]*$')
        # df_EIPA_invoice['EtrelFriendlyCode'] = df_EIPA_invoice['EtrelFriendlyCode'].str.replace(r'PL-7R5-EL', '<your prefix in Friendly Code>')
        # df_EIPA_invoice['EtrelFriendlyCode'] = df_EIPA_invoice['EtrelFriendlyCode'].str[:-2]

        # # Here you should adjust numbers in square brackets to match your Friendly Code. This one is design for codes of length 8 (prefix + location number).
        # df_EIPA_invoice['EtrelFriendlyCode'] = df_EIPA_invoice['EtrelFriendlyCode'].str[:8] + '-' + df_EIPA_invoice['EtrelFriendlyCode'].apply(lambda x: x[-1:] if len(x) == 9 else x[-2:])

        return df_EIPA_invoice
    
    pdf_file_path = save_invoice()
    df_EIPA_invoice = get_data_from_invoice(pdf_file_path)

    return df_EIPA_invoice