import pandas as pd
import streamlit as st
import numpy as np
import time
from datetime import date, datetime
from calendar import monthrange
import plotly.express as px
from dateutil.relativedelta import relativedelta
from os import path

st.set_page_config(
    layout = 'wide',
    page_title = f'Aplicativo CGOV'
)

def tela_inicial():

    col1, col2, col3 = st.columns([0.35, 0.3, 0.35])
    with col2:
        st.image(r'docs/logo.png')

    st.markdown("<h1 style='text-align: center; color: black;'>Coordenadoria de Governança</h1>", unsafe_allow_html=True)

lista_modulos = ['Diferença SILOMS SIAFI', 'Acompanhamento PTA DIRAD', 'Acompanhamento PLANSET']

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown('''
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    ''', unsafe_allow_html=True
)

st.sidebar.image(r'docs/domDiradCinza.jpg', use_container_width = False)

modulos = st.sidebar.selectbox(
    'Módulos',
    lista_modulos,
)

if modulos == 'Diferença SILOMS SIAFI':

    dicionario_meses = {
        '01' : 'JAN',
        '02' : 'FEV',
        '03' : 'MAR',
        '04' : 'ABR',
        '05' : 'MAI',
        '06' : 'JUN',
        '07' : 'JUL',
        '08' : 'AGO',
        '09' : 'SET',
        '10' : 'OUT',
        '11' : 'NOV',
        '12' : 'DEZ'
    }

    uploaded_file = st.sidebar.file_uploader('Faça o upload do arquivo.')

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)
        df.drop(0, inplace = True)
        df.reset_index(drop = True, inplace = True)
        lista_colunas = list(df.columns)
        df[lista_colunas[1]] = df[lista_colunas[1]].astype(int)
        df[lista_colunas[1]] = df[lista_colunas[1]].astype(str)
        df['ANO'] = df[lista_colunas[1]].str[0:4]
        df['MÊS'] = df[lista_colunas[1]].str[4:]
        
        for i in range(df.shape[0]):
            df.loc[i, lista_colunas[1]] = dicionario_meses[df.loc[i, 'MÊS']] + '/' + df.loc[i, 'ANO']
            df.loc[i, 'CONSUMO'] = df.loc[i, lista_colunas[2]] - df.loc[i, lista_colunas[3]]
            df.loc[i, 'BMP'] = df.loc[i, lista_colunas[5]] - df.loc[i, lista_colunas[6]]
            df.loc[i, 'INTANGÍVEL'] = df.loc[i, lista_colunas[8]] - df.loc[i, lista_colunas[9]]
        df = df.drop([lista_colunas[2], lista_colunas[3], lista_colunas[4], lista_colunas[5], lista_colunas[6], lista_colunas[7], lista_colunas[8], lista_colunas[9], lista_colunas[10], 'MÊS', 'ANO'], axis = 1)

        lista_opcoes_unidades = sorted(list(df[lista_colunas[0]].value_counts().index))
        lista_opcoes_meses = list(df[lista_colunas[1]].value_counts().index)
        
        with st.sidebar.form("my_form"):
            opcoes_unidades = st.multiselect(
                'UG',
                lista_opcoes_unidades,
                placeholder = 'Selecione uma ou mais UG'
            )
            opcoes_meses = st.multiselect(
                'Meses',
                lista_opcoes_meses,
                placeholder = 'Selecione uma ou mais meses'
            )
            gerar_relatorio = st.form_submit_button("Gerar Relatório")

        if gerar_relatorio:

            for unidade in opcoes_unidades:
                df2 = df.loc[(df['UGE'] == unidade) & (df['PERIODO'].isin(opcoes_meses)), ['PERIODO', 'CONSUMO', 'BMP', 'INTANGÍVEL']]
                df_melt = pd.melt(df2, id_vars = 'PERIODO', var_name = 'DIFERENÇA', value_name = 'SILOMS - SIAFI')
                fig = px.line(df_melt, x = "PERIODO", y = 'SILOMS - SIAFI', color = 'DIFERENÇA', title = unidade, color_discrete_sequence=["#0099C6", "red", "rgb(166, 216, 84)"])
                fig.update_xaxes(tickfont_size = 14, tickfont_color = 'black', title_font = dict(color = 'black', size = 14))
                fig.update_yaxes(tickfont_size = 14, tickfont_color = 'black', title_font = dict(color = 'black', size = 14))
                st.plotly_chart(fig, theme="streamlit")
                df2_set = df2.set_index('PERIODO')
                df2_set_t = df2_set.T
                df2_set_t_style = df2_set_t.style.format('{:,.2f}')
                st.write(df2_set_t_style.to_html(), unsafe_allow_html=True)

    else:

        tela_inicial()

elif modulos == 'Acompanhamento PTA DIRAD':

    lista_titulos = ['CAPÍTULO', 'Seção', 'Subseção']

    lista_corte_1 = ['PROJETO:', 'Item de Controle:']

    lista_corte_2 = ['Atividade:']

    uploaded_file = st.sidebar.file_uploader('Faça o upload do arquivo.')

    st.write('')
    
    gerar_relatorio = st.sidebar.button("Gerar Relatório")

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)

        df.columns = [
            'Executado(%)', 
            'Tarefa', 
            'Prioridade', 
            'Físico Planejado(%)',
            'Responsável', 
            'Designados', 
            'Status', 
            'Tipo', 
            'Código', 
            'Início',
            'Término', 
            'Dur./8.0h', 
            'Dur./Dias', 
            'P. Custo Hoje', 
            'M.O Hoje',
            'Recurso Hoje', 
            'Total Estimado', 
            'P. Gasto', 
            'M.O Gasto',
            'Recurso Gasto', 
            'Total Gastos'
        ]
        
        def verifica_df_temp(df_temp):
            if not df_temp[(df_temp['Atrasado'] == 'Amarelo') | (df_temp['Atrasado'] == 'Vermelho')].empty:
                return True

        def imprime_df_temp(df_temp):
            if not df_temp[df_temp['Atrasado'] == 'Amarelo'].empty:
                st.table(df_temp[df_temp['Atrasado'] == 'Amarelo'].drop(['Filtro', 'Início_datatime', 'Término_datatime', 'Atrasado'], axis = 1).style.set_properties(**{'background-color' : 'yellow'}))
            if not df_temp[df_temp['Atrasado'] == 'Vermelho'].empty:
                st.table(df_temp[df_temp['Atrasado'] == 'Vermelho'].drop(['Filtro', 'Início_datatime', 'Término_datatime', 'Atrasado'], axis = 1).style.set_properties(**{'background-color' : 'red', 'color' : 'white'}))
        
        df = df[['Tarefa', 'Responsável', 'Físico Planejado(%)', 'Executado(%)', 'Início', 'Término']]

        df['Tarefa'] = df['Tarefa'].str.encode('latin-1').str.decode('utf-8')       

        df['Filtro'] = df['Tarefa'].str.split().str[0]

        for i in range(df.shape[0]):
            if df.loc[i, 'Filtro'] == 'Item':
                if 'Item de Controle:' in df.loc[i, 'Tarefa']:
                    df.loc[i, 'Filtro'] = 'Item de Controle:'
            elif df.loc[i, 'Filtro'] == 'Art.':
                if 'PROJETO:' in df.loc[i, 'Tarefa']:
                    df.loc[i, 'Filtro'] = 'PROJETO:'
                elif 'Atividade:' in df.loc[i, 'Tarefa']:
                    df.loc[i, 'Filtro'] = 'Atividade:'
            
        df['Início_datatime'] = pd.to_datetime(df['Início'], format = '%d/%m/%Y %H:%M:%S')

        df['Término_datatime'] = pd.to_datetime(df['Término'], format = '%d/%m/%Y %H:%M:%S')

        for i in range(df.shape[0]):
            if df.loc[i, 'Filtro'] not in (lista_titulos + lista_corte_1 + lista_corte_2):
                if ((df.loc[i, 'Executado(%)'] < 100) and (df.loc[i, 'Término_datatime'] < datetime.now())):
                    df.loc[i, 'Atrasado'] = 'Vermelho'
                elif ((df.loc[i, 'Executado(%)'] == 0) and (df.loc[i, 'Início_datatime'] < datetime.now())):
                    df.loc[i, 'Atrasado'] = 'Amarelo'
                else:
                    df.loc[i, 'Atrasado'] = 'Verde'
            else:
                df.loc[i, 'Atrasado'] = 'Sem cor'

        if gerar_relatorio:
            df_temp = pd.DataFrame()
            lista_capitulo = []
            lista_secao = []
            lista_subsecao = []
            for i in range(df.shape[0]):
                if df.loc[i, 'Filtro'] == 'CAPÍTULO':
                    capitulo = df.loc[i, "Tarefa"]
                elif df.loc[i, 'Filtro'] == 'Seção':
                    secao = df.loc[i, "Tarefa"]
                elif df.loc[i, 'Filtro'] == 'Subseção':
                    subsecao = df.loc[i, "Tarefa"]
                elif df.loc[i, 'Filtro'] in lista_corte_2:
                    filtro_tipo = 'Atividade:'
                    tipo = f'>>> {df.loc[i, "Tarefa"]}\n'
                elif df.loc[i, 'Filtro'] in lista_corte_1:
                    if df.loc[i, 'Filtro'] == 'PROJETO:':
                        filtro_tipo = 'PROJETO:'
                        tipo = f'>>> {df.loc[i, "Tarefa"]}\n'
                    elif df.loc[i, 'Filtro'] == 'Item de Controle:':
                        item_controle = f'>>>> {df.loc[i, "Tarefa"]}\n'
                    i = i + 1
                    while (i < df.shape[0] - 1) and (df.loc[i, 'Filtro'] not in (lista_titulos + lista_corte_1 + lista_corte_2)):
                        df_temp = pd.concat([df_temp, df.loc[i, :].to_frame().T])
                        i = i + 1
                    if (i < df.shape[0] - 1):
                        i = i - 1
                    verifica = verifica_df_temp(df_temp)
                    if verifica: 
                        if capitulo not in lista_capitulo:
                            st.write(f'**{capitulo}**')
                            lista_capitulo.append(capitulo)
                        if secao not in lista_secao:
                            st.write(f'> **{secao}**')
                            lista_secao.append(secao)
                        if subsecao not in lista_subsecao:
                            st.write(f'>> **{subsecao}**')
                            lista_secao.append(subsecao)
                        st.write(tipo)
                        if filtro_tipo == 'Atividade:':
                            st.write(item_controle)
                        imprime_df_temp(df_temp)
                    df_temp = pd.DataFrame()

    else:

        tela_inicial()

elif modulos == 'Acompanhamento PLANSET':

    uploaded_file = st.sidebar.file_uploader('Faça o upload do arquivo.')
    
    st.write('')
    
    gerar_relatorio = st.sidebar.button("Gerar Relatório")

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)

        df.columns = [
            'Executado(%)', 
            'Tarefa', 
            'Prioridade', 
            'Físico Planejado(%)',
            'Responsável', 
            'Designados', 
            'Status', 
            'Tipo', 
            'Código', 
            'Início',
            'Término', 
            'Dur./8.0h', 
            'Dur./Dias', 
            'P. Custo Hoje', 
            'M.O Hoje',
            'Recurso Hoje', 
            'Total Estimado', 
            'P. Gasto', 
            'M.O Gasto',
            'Recurso Gasto', 
            'Total Gastos'
        ]
        
        dirad = '.SEF03.'

        lista = ['ASGOV', 'DIREF', 'SIFARE', 'SISADM', 'SEFA QG', 'BREVET', 'CAE', 'FAYS', 'GALC', 'GAP-AF', 'GAP-BE', 'GAP-BR', 
                'GAP-CO', 'GAP-DF', 'GAP-GL', 'GAP-LS', 'GAP-MN', 'GAP-RF', 'GAP-RJ', 'GAP-SP', 'PAAF', 'PABE', 'PABR',
                'PACO', 'PAGL', 'PALS', 'PAMN', 'PARF', 'PASP', 'SISCONTAER', 'SISGI', 'SISPAER', 'IEFA', 'SISPROV', 'SISTENS',
                'IEFA', 'SUCONV', 'SISRI', 'SISCOMAER', 'SISCOMSAE', 'SEFA', 'SISCON', 'SISPAGAER', 'SISUB', 'SISICAMP']
        
        def verifica_df_temp(df_temp):
            if not df_temp[(df_temp['Atrasado'] == 'Amarelo') | (df_temp['Atrasado'] == 'Vermelho')].empty:
                return True

        def imprime_df_temp(df_temp):
            if not df_temp[df_temp['Atrasado'] == 'Amarelo'].empty:
                st.table(df_temp[df_temp['Atrasado'] == 'Amarelo'].drop(['Filtro', 'Início_datatime', 'Término_datatime', 'Atrasado'], axis = 1).style.set_properties(**{'background-color' : 'yellow'}))
            if not df_temp[df_temp['Atrasado'] == 'Vermelho'].empty:
                st.table(df_temp[df_temp['Atrasado'] == 'Vermelho'].drop(['Filtro', 'Início_datatime', 'Término_datatime', 'Atrasado'], axis = 1).style.set_properties(**{'background-color' : 'red', 'color' : 'white'}))
        
        df = df[['Tarefa', 'Designados', 'Físico Planejado(%)', 'Executado(%)', 'Início', 'Término']]

        df['Tarefa'] = df['Tarefa'].str.encode('latin-1').str.decode('utf-8')

        df['Filtro'] = df['Tarefa'].str.split().str[0]

        df['Início_datatime'] = pd.to_datetime(df['Início'], format = '%d/%m/%Y %H:%M:%S')

        df['Término_datatime'] = pd.to_datetime(df['Término'], format = '%d/%m/%Y %H:%M:%S')

        df['Designados'] = df['Designados'].str.replace('\n', ' | ')
        
        if gerar_relatorio:

            i = 0
            linha_inicio = 0
            linha_fim = 0
            df_resumo = pd.DataFrame()
            while i < df.shape[0]:
                if df.loc[i, 'Filtro'] == 'DIRAD':
                    linha_inicio = i + 1
                    while (df.loc[i, 'Filtro'] not in lista):
                        if (i < df.shape[0] - 1):
                            i += 1
                        else:
                            i += 1
                            break
                    linha_fim = i
                    df_resumo = pd.concat([df_resumo, df.iloc[linha_inicio:linha_fim,:]])
                else:
                    i += 1
            
            df_resumo.reset_index(drop = True, inplace = True)

            for i in range(df_resumo.shape[0]):
                if dirad not in df_resumo.loc[i, 'Filtro']:
                    if ((df_resumo.loc[i, 'Executado(%)'] < 100) and (df_resumo.loc[i, 'Término_datatime'] < datetime.now())):
                        df_resumo.loc[i, 'Atrasado'] = 'Vermelho'
                    elif ((df_resumo.loc[i, 'Executado(%)'] == 0) and (df_resumo.loc[i, 'Início_datatime'] < datetime.now())):
                        df_resumo.loc[i, 'Atrasado'] = 'Amarelo'
                    else:
                        df_resumo.loc[i, 'Atrasado'] = 'Verde'
                else:
                    df_resumo.loc[i, 'Atrasado'] = 'SemCor'
                    
            i = 0
            linha_inicio = 0
            linha_fim = 0
            while i < df_resumo.shape[0]:
                if dirad in df_resumo.loc[i, 'Filtro']:
                    tarefa = df_resumo.loc[i, 'Tarefa']
                    i = i + 1
                    linha_inicio = i
                    while (dirad not in df_resumo.loc[i, 'Filtro']):
                        if (i < df_resumo.shape[0] - 1):
                            i += 1
                        else:
                            i += 1
                            break
                    linha_fim = i
                    df_temp = df_resumo.iloc[linha_inicio:linha_fim,:]
                    if verifica_df_temp(df_temp):
                        st.write('')
                        st.write(f'**{tarefa}**')
                        imprime_df_temp(df_temp)
                else:
                    i += 1
        
    else:

        tela_inicial()