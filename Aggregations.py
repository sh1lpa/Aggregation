'''
Author : Shilpa Shinde

python Aggregation.py --formula <formula>
'''
import io
import argparse
import requests     
import pandas as pd 
import numpy as np

def url_request(identifier):

    ''' Building blocks for the URL 
    https://sdw-wsrest.ecb.europa.eu/service/data/BP6/{identifier}?detail=dataonly
    
    '''

    entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
    resource = 'data'           # The resource for data queries is always'data'
    flowRef ='BP6'              # Dataflow describing the data that needs to be returned, exchange rates in this case
    key = identifier   # Defining the dimension values, explained below

    parameters = {
        'detail':'dataonly', 
    }

    # Construct the URL: https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.CHF.EUR.SP00.A
    request_url = entrypoint + resource + '/'+ flowRef + '/' + key

    # Make the HTTP request
    response = None
    try:
            
        response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})

        response.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        
    # Check if the response returns succesfully with response code 200
    # print(response)

    return response

def get_transactions(identifier: str) :

    '''
    This function is fetching the transaction data from 
    the appropriate URL and convert it to a pandas DataFrame, 
    with columns IDENTIFIER, TIME_PERIOD and OBS_VALUE.
    
    '''
    response = url_request(identifier)

    # io.StringIO method is used to parse the text/csv response data 
    # further converted into pandas Dataframe using pd.read_csv method

    response_df = pd.read_csv(io.StringIO(response.text))
    
    # renaming the KEY column to IDENTIFIER
    response_df.rename(columns= {'KEY':'IDENTIFIER'}, inplace=True)

    # returning only the required columns of the resulting df
    return response_df[['IDENTIFIER', 'TIME_PERIOD' ,'OBS_VALUE']]


def pivot_table(dfs, s, sign):
    '''
    this function will help achieve the aggregation depending 
    on the operator sign in formula i.e. + or - '''

    # if sign == True, we alter the sign of all the column values of df['OBS_VALUE] 
    # it is done using lambda function in else part

    if not sign:
        df = get_transactions(s)
    else:
        df = get_transactions(s)
        df['OBS_VALUE'] = df['OBS_VALUE'].map(lambda x:-x)

    # pd.pivot_table is used to reframe the structure of existing df using IDENTIFIER column 

    dfs.append(pd.pivot_table(df,index =['TIME_PERIOD'],
                                     values =['OBS_VALUE'],columns=['IDENTIFIER'], aggfunc ='sum'))

def get_formula_data(formula):

    '''
        Function returns a DataFrame with TIME_PERIOD column as the index, 
        and have as many columns as there are identifiers, 
        each containing values of the OBS_VALUE column from the appropriate DataFrame.
    '''

    dfs = []
    if len(formula.split("=")[1].split("+"))>=1:
        for i in formula.split("=")[1].split("+"):

            if len(i.split("-")) > 1:
                for ind, j in enumerate(i.split("-")):
                    if ind ==0:
                        pivot_table(dfs,j.strip(),False)
                    else:
                        pivot_table(dfs,j.strip(),True)
            else:
                pivot_table(dfs,i.strip(),False)
    return pd.concat([pd.pivot_table(i,index =['TIME_PERIOD'],values =['OBS_VALUE'], aggfunc ='sum') for i in dfs],axis=1)

def compute_aggregates(formula: str):
    '''
        computing the aggregate by summing up the values 
        indicated by the operation sign
    '''
    left = formula.split("=")[0]
    df = get_formula_data(formula)
    df[left] = df.apply(np.sum, axis = 1)

    return df[left].to_frame()

def main():
    '''
    main function will take formula string as a command line argument and 
    resulting df will be printed on screen along with
    the file is created with resulting df
    '''
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--formula", required=True,
	help="give the Formula string :")
    args = vars(ap.parse_args())

    formula = args['formula']
    
    df_final = compute_aggregates(formula)
    
    df_final.to_csv('./aggregate.csv')

    print(df_final.head())

if __name__ == '__main__':
    main()

