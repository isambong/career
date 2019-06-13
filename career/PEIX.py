
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
mg_client = MongoClient()

from career import db명, data_path
db = mg_client[db명]



def PEIX_practica():
    tbl명='PEIX'

    r = requests.get('https://www.inf.upv.es/int/peix/alumnos/listado_ofertas.php')

    soup = BeautifulSoup(r.text, 'html.parser')
    df = 파싱(soup)

    # 저장, 중복제거, 백업
    db[tbl명].insert_many(df.to_dict('records'))
    mg.테이블의_중복제거(db명, tbl명, subset=['오퍼코드'])
    mg.테이블의_백업csv_생성(db명, tbl명, data_path)

def 파싱(soup):
    # 파싱-1
    tbls_bs = soup.find_all("table", class_="tabla_base")
    tbls_str = str(tbls_bs)
    df_li = pd.read_html( tbls_str )
    dic_li = []
    for df in df_li:
        df_1 = df.loc[:,[0,1]]
        df_1 = df_1.rename(columns={0:'key', 1:'val'})
        df_2 = df.loc[:,[2,3]]
        df_2 = df_2.rename(columns={2:'key', 3:'val'})
        df_3 = pd.concat([df_1, df_2]).dropna(axis=0, how='all')
        df_3.key = df_3.key.apply(lambda x: str(x).replace(' ','_') )
        df_3.key = df_3.key.apply(lambda x: str(x).replace(':','') )
        df_3.index = df_3.key
        del(df_3['key'])
        dic_li.append( df_3.val.to_dict() )

    # 파싱-2
    df = pd.DataFrame(dic_li)
    df = df.fillna('_')
    df.Titulaciones_ = df.Titulaciones_.combine(df.Titulación_, lambda x1, x2: x1 if x1 != '_' else x2)
    del(df['Titulación_'])
    df = df.rename(columns={
        'Bolsa':'월급',
        'Código_Oferta':'오퍼코드',
        'Empresa':'기업명',
        'Fecha_Inicio':'근무시작날짜',
        'Fecha_Oferta':'오퍼날짜',
        'Horas_al_Dia':'일근무시간',
        'Localidad':'근무지역',
        'Perfil_de_la_Oferta':'요구능력',
        'Posibilidad_PFC':'PFC_가능성',
        'Tareas':'업무',
        'Titulaciones_':'요구학력'})

    df.월급 = df.월급.str.replace(' Euros','')
    df.월급 = df.월급.apply(lambda x: float(x))
    df.일근무시간 = df.일근무시간.apply(lambda x: float(x))

    df.근무시작날짜 = df.근무시작날짜.apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))
    df.오퍼날짜 = df.오퍼날짜.apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))
    return df
