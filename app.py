import streamlit as st
import plotly as px
from dataset import df
from utils import  format_number
from graficos import *
from app2 import filtrar_dados, graficos_rotas, grafico_rec_diaria, grafico_rec_mensal, grafico_rec_remetente, grafico_map_estado, grafico_rec_cidade, grafico_peso_rotas

st.set_page_config(
    page_title="Cotralti T&L",
    page_icon="images/cotralti_logo.png",
    layout="wide",
  
)
# Filtros aplicados na sidebar
filtro_remetente = st.sidebar.multiselect(
    label="Remetente",
    options=df['Remetente'].unique(),
    default=df['Remetente'].unique()
)

filtro_mes = st.sidebar.multiselect(
    label="Mês",
    options=df['Data'].dt.strftime('%B').unique(),  # nomes dos meses
    default=df['Data'].dt.strftime('%B').unique()
)

df_filtrado = filtrar_dados(df, filtro_remetente, filtro_mes)
#-------------------------------------------------------------------------------------------

st.header("Dasboard de :blue[Vendas] :shopping_trolley:", divider='green')
st.write("""&copy; 2025 - Luis Felipe A. David. Todos os direitos reservados""")

aba1 , aba2, aba3 = st.tabs(['Dataset','Receitas','Tabela de Preço'])

with aba1:
    st.dataframe(df, use_container_width=True,
                 column_config={
                     "Data": st.column_config.DateColumn("Data", format="DD.MM.YYYY"),
                 })
with aba2:
    col1, col2, col3, col4 = st.columns(4)
    graf1, graf2, = st.columns(2)
    with col1:
        #valor = df['Frete Peso'].sum()
        st.metric(":green-background[**Receita Total (Frete Peso)**]", format_number(df['Frete Peso'].sum(), 'R$'))
    with graf1:
        st.plotly_chart(grafico_map_estado, use_container_width=True)
        st.plotly_chart(grafico_rec_cidade, use_container_width=True)
    with col2:
        qtdNf = df.shape[0]
        st.metric(":green-background[**Qtd NF**]",f'{qtdNf:_.0f}'.replace('.',',').replace('_','.') )
    with graf2:
        st.plotly_chart(grafico_rec_mensal, use_container_width=True)
        st.plotly_chart(grafico_rec_remetente, use_container_width=True)
    with col3:
        peso = df['Peso Taxado'].sum()
        st.metric(":green-background[**Peso Total**]",f'{peso:_.2f} ton'.replace('.',',').replace('_','.') )
    with col4:
        valortransportado = df['Valor N.F.'].sum()
        st.metric(":green-background[**Valor Transportado**]",format_number(df['Valor N.F.'].sum(), 'R$'))
with aba3:
    col1 , col2 = st.columns(2)
    with col1:
        st.plotly_chart(graficos_rotas)
    with col2:
        st.plotly_chart(grafico_peso_rotas)
    st.plotly_chart(grafico_rec_diaria, use_container_width=True) 
