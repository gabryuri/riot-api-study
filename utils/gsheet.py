import json
import pandas as pd 
import os 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SERVICE_ACCOUNT_FILE = 'svc.json'
def get_service_client():
    """
    Return google sheet service client
    """
    creds = None
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    return sheet

def get_dataset(logger,
                spreadsheet_id: str,
                range: str,
                schema=None):

    """
    Return a dataframe from google sheet.
    Remember do share the spreadsheet with openreports@ifood-data-platform.iam.gserviceaccount.com
    :param spreadsheet_id: Spreadsheet ID
                          (ex: 1fyR1J5N-NJj6dzvMGxHuzhFM0PAy6RCS5TXv9mumylk)
    :param range: Tab name and range (ex: Tabname!A:C)
    :param schema: StructType or Array with headers.
                   If none provided, will fetch header from first row
    :return: Dataframe containing specified data
    """
    sheet = get_service_client()

    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range).execute()
                         
        values = result.get('values', [])

        if (len(values) <= 1 and schema is None) or (len(values) == 0):
            return pd.DataFrame({'A' : []})

        logger.info(f'Schema: {schema}')
        norm_values = normalize_dataset(dataset=values, schema=schema)

        if schema is not None:
            df = pd.DataFrame(norm_values)
        else:
            df = pd.DataFrame(norm_values[1:], columns=norm_values[0])

        logger.info('Read %s rows' % len(values))
        logger.info('Schema:')

    except Exception as e:
        logger.info('Error: %', str(e))
        raise e

    return df


def normalize_dataset(dataset, schema):
    """
    Return a new dataset with fixed columns
    """
    values = dataset[:]

    if schema is not None:
        dataset_length = len(schema)
    else:
        dataset_length = len(values[0])  # header

    # print('Schema length: %s' % dataset_length)

    for val in values:
        while len(val) < dataset_length:
            val.append(u'')

    return values


def sheet_exists(spreadsheet_id: str, sheet_title: str) -> bool:
    sheet = get_service_client()
    tabs = sheet.get(spreadsheetId=spreadsheet_id, fields='sheets.properties').execute()
    for t in tabs['sheets']:
        if t['properties']['title'] == sheet_title:
            return True
    return False


def create_tab(spreadsheet_id: str, sheet_title: str) -> str:
    sheet = get_service_client()
    if sheet_exists(spreadsheet_id, sheet_title):
        return 'Sheet already exists'
    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheet_title
                }
            }
        }]
    }  
    return str(sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute())

def to_string(u):
    if u is None:
        u = 0
    if isinstance(u, int) or isinstance(u, float):
        return u
    else:
        return str(u)


def gsheets_data_dump(
    df: pd.DataFrame, spreadsheet_id: str, range_sheet: str,
        ord_cols= None, title: bool = True, clear: bool = True, create_sheet: bool = False) -> int:
    """
    Função de data dump em uma planilha do Google Spreadsheets
    COMPARTILHAR SHEET COM openreports@ifood-data-platform.iam.gserviceaccount.com com permissão para editar.
    gsheets_data_dump(
    df -> spark dataframe que vai ser carregado no Sheets
    spreadsheet_id -> string contendo sheet id, hash que fica após o /d
    range_sheet -> string com aba!range da primeira célula onde serão carregados os dados, exemplo: "Página1!A1"
    ord_cols -> lista com os nomes das colunas para a ordenacao desejada do dataframe (default None)
    title -> booleano indicando se deseja titulo das colunas na primeira linha (default True)
    clear -> booleano indicando se deseja se toda a planilha seja limpa antes de receber os dados (default True)
    create_sheet -> booleano indicando se deseja que seja criada uma nova sheet, caso não exista (default False)
    )
    """
    ord_cols = ord_cols or []
    colunas = df.columns

    # verificacao parametros
    if len(ord_cols) > 0:
        for c in ord_cols:
            if c not in colunas:
                print(c + ' nao faz parte do df')
                return -1

    sheet = get_service_client()

    sheet_name = range_sheet.split('!')[0]

    sheet_exists_res = sheet_exists(spreadsheet_id, sheet_name)
    
    # verificação sheet exists
    if (sheet_exists_res == False) and (create_sheet == False):
        print('Sheet {} não existe.'.format(sheet_name))
        return -1
    elif sheet_exists_res == False:
        print(create_tab(spreadsheet_id, sheet_name))

    # limpeza da sheet a ser feito o update
    if clear:
        clear_values_request_body = {}
        request = sheet.values().clear(spreadsheetId=spreadsheet_id, range=range_sheet +
                                       ':ZZ', body=clear_values_request_body).execute()
    else:
        print('Não será limpo seu sheet, cuidado com valores indesejados!!')

    ordenacao = False
    win = []
    if len(ord_cols) > 0:
        ordenacao = True
        for c in ord_cols:
            win.append(col(c).asc())

    if ordenacao:
        df = df.orderBy(win)

    lista = eval(json.dumps([list(to_string(val) for val in row) for row in df.values]))

    if title:
        lista = [df.columns.tolist()] + lista

    body = {
        "values": lista
    }


    result = sheet.values().update(spreadsheetId=spreadsheet_id, range=range_sheet,
                                   valueInputOption='RAW', body=body).execute()
    print(result)

    return 0

