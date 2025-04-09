import streamlit as st
import plotly.express as px
import pandas as pd
from dataset import df
from utils import format_number, filtrar_dados
from graficos import graficos_rotas, grafico_rec_diaria, grafico_rec_mensal, grafico_rec_remetente, grafico_map_estado, grafico_rec_cidade, grafico_peso_rotas

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
    options=df['Data'].dt.strftime('%B').unique(),
    default=df['Data'].dt.strftime('%B').unique()
)

# Filtra o DataFrame usando a função definida em utils.py
df_filtrado = filtrar_dados(df, filtro_remetente, filtro_mes)

# Recalcula os dados necessários para os gráficos após os filtros
dc_rec_estado = df_filtrado.groupby('Cidade Destino')[['Frete Peso']].sum()
dc_rec_estado = df_filtrado.drop_duplicates(subset='Cidade Destino')[['Cidade Destino', 'lat', 'lon']].merge(dc_rec_estado, left_on='Cidade Destino', right_index=True).sort_values('Frete Peso', ascending=False)

dc_rec_mensal = df_filtrado.set_index('Data').groupby(pd.Grouper(freq='ME'))['Frete Peso'].sum().reset_index()
dc_rec_mensal['Mes'] = dc_rec_mensal['Data'].dt.month_name()
dc_rec_mensal['Ano'] = dc_rec_mensal['Data'].dt.year

# Recalcule os dados para outros gráficos
dc_rec_remetente = df_filtrado.groupby('Remetente')[['Frete Peso']].sum()
dc_rec_remetente = df_filtrado.drop_duplicates(subset='Remetente')[['Remetente', 'lat', 'lon']].merge(dc_rec_remetente, left_on='Remetente', right_index=True).sort_values('Frete Peso', ascending=False)

df_rotas = pd.DataFrame(df_filtrado.groupby('Tabela de Preço')['Frete Peso'].agg(['sum','count']))
df_rotas_peso = pd.DataFrame(df_filtrado.groupby('Tabela de Preço')['Peso Taxado'].agg(['sum','count']))
dc_rec_diaria = df_filtrado.set_index('Data').groupby(pd.Grouper(freq='D'))['Frete Peso'].sum().reset_index()
dc_rec_diaria_peso = df_filtrado.set_index('Data').groupby(pd.Grouper(freq='D'))['Peso Taxado'].sum().reset_index()
df_cliente = pd.DataFrame(df_filtrado.groupby('Cliente')['Frete Peso'].agg(['sum','count']))
df_cliente_peso = pd.DataFrame(df_filtrado.groupby('Cliente')['Peso Taxado'].agg(['sum','count']))

# Adiciona nome do dia da semana em português
dc_rec_diaria['Dia'] = dc_rec_diaria['Data'].dt.strftime('%A')

# Graficar métricas com base no DataFrame filtrado
st.header("Oráculo :green[Cotralti] - Dashboard de :blue[Distribuição] :shopping_trolley:", divider='green')
st.write("""&copy; 2025 - Luis Felipe A. David. Todos os direitos reservados""")

# Dicionário de tradução de meses (inglês completo para português)
traducao_meses = {
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
    'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
    'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
    'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
}

# Substitui os nomes dos meses para português
dc_rec_mensal['Mes'] = dc_rec_mensal['Mes'].replace(traducao_meses)

# Cria uma nova coluna com o valor formatado
dc_rec_estado['Frete Peso Formatado'] = dc_rec_estado['Frete Peso'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

aba1, aba2, aba3 = st.tabs(['Dataset', 'Informações Financeiras', 'Informações Gerais'])

with aba1:
    st.dataframe(df_filtrado, use_container_width=True,
                 column_config={
                     "Data": st.column_config.DateColumn("Data", format="DD.MM.YYYY"),
                 })
with aba2:
    col1, col2, col3, col4 = st.columns(4)
    graf1, graf2 = st.columns(2)
    with col1:
        st.metric(":green-background[**Receita Total (Frete Peso)**]", format_number(df_filtrado['Frete Peso'].sum(), 'R$'))
    with graf1:
        # Atualize os gráficos com os dados filtrados
        grafico_map_estado = px.scatter_geo(
            dc_rec_estado,
            lat='lat',
            lon='lon',
            size='Frete Peso',
            scope='south america',
            color='Frete Peso',
            color_continuous_scale=px.colors.sequential.Plasma,
            template='seaborn',
            hover_name='Cidade Destino',
             hover_data={
              'lat': False,
              'lon': False,
              'Frete Peso Formatado': True,
              'Frete Peso': False
          },
            title='Receita por Cidade de Destino'
        )
        st.plotly_chart(grafico_map_estado, use_container_width=True)
        
        # Manter apenas as 7 cidades com maior receita
        top_cidades = dc_rec_estado.sort_values(by='Frete Peso', ascending=False).head(7)
        grafico_rec_cidade = px.bar(
            dc_rec_estado.head(7),  # Top 7 cidades
            x='Cidade Destino', 
            y='Frete Peso',
            color='Frete Peso',  # necessário para a escala de cores funcionar
            text='Frete Peso Formatado',
            labels={'Frete Peso': 'Receita (R$)'},
            color_continuous_scale=px.colors.sequential.Plasma,
            template='seaborn',
            title='Top 7 Cidades por Receita'
            
        )
        #grafico_rec_cidade.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(grafico_rec_cidade, use_container_width=True)
    with col2:
        qtdNf = df_filtrado.shape[0]
        st.metric(":green-background[**Qtd NF**]", f'{qtdNf:_.0f}'.replace('.', ',').replace('_', '.'))
    with graf2:
              #GRAFICO DE LINHA
        # Certifique-se de que a coluna 'Data' está no formato correto
        dc_rec_mensal['Ano'] = dc_rec_mensal['Data'].dt.year  # Adiciona coluna de ano
        dc_rec_mensal['Mes_Numero'] = dc_rec_mensal['Data'].dt.month  # Adiciona coluna de número do mês

        # Ordenar corretamente por ano e mês
        dc_rec_mensal = dc_rec_mensal.sort_values(['Ano', 'Mes_Numero'])

        # Calcular crescimento percentual mês a mês por ano
        dc_rec_mensal['Variação (%)'] = dc_rec_mensal.groupby('Ano')['Frete Peso'].pct_change() * 100

        # Formatar a variação percentual
        dc_rec_mensal['Variação Formatada'] = dc_rec_mensal['Variação (%)'].apply(
            lambda x: f"{x:+.1f}%" if pd.notnull(x) else ""
        )

        # Formatar valor em reais
        dc_rec_mensal['Frete Peso Formatado'] = dc_rec_mensal['Frete Peso'].apply(
            lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        grafico_rec_mensal = px.line(
            dc_rec_mensal,
            x='Mes',
            y='Frete Peso',
            range_y=(0, dc_rec_mensal['Frete Peso'].max()),
            color='Ano',
            markers=True,
            template='seaborn',
            line_dash='Ano',
            line_shape='spline',
            title='Receita Mensal',
            hover_name='Mes',
            hover_data={'Frete Peso Formatado': True,
            'Variação Formatada': True,
            'Frete Peso': False,
            'Variação (%)': False
            }
        )
      

      # Ajustando o tamanho da fonte dos dados do hover
        grafico_rec_mensal.update_traces(
          hoverlabel=dict(
              font=dict(
                  size=14  # Ajuste o tamanho da fonte do hover data conforme desejado
              )
          )
      )
        st.plotly_chart(grafico_rec_mensal, use_container_width=True)
        # Cores suaves
        dc_rec_remetente['Frete Peso Formatado'] = dc_rec_remetente['Frete Peso'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        cores_personalizadas = px.colors.qualitative.Pastel
        grafico_rec_remetente = px.pie(
            dc_rec_remetente,
            values='Frete Peso',
            names='Remetente',
            template='seaborn',
            color_discrete_sequence=cores_personalizadas,
            hole=0.4,
            hover_data=['Frete Peso Formatado'],
            title='Distribuição de Receita por Remetente',
        )
        
                  # Estilizar os rótulos com texto em negrito
        grafico_rec_remetente.update_traces(
              textinfo='percent+label',
              pull=[0.05] * len(dc_rec_remetente),
              marker=dict(line=dict(color='#FFFFFF', width=2)),
              textfont=dict(size=14, family='Arial Black', color='black')  # Negrito forte
          )

        grafico_rec_remetente.update_layout(
              height=500,
              showlegend=True,
              legend_title_text='Remetente'
          )
        st.plotly_chart(grafico_rec_remetente, use_container_width=True)
    with col3:
        peso = df_filtrado['Peso Taxado'].sum()
        st.metric(":green-background[**Peso Total**]", f'{peso:_.2f} ton'.replace('.', ',').replace('_', '.'))
    with col4:
        valortransportado = df_filtrado['Valor N.F.'].sum()
        st.metric(":green-background[**Valor Transportado**]", format_number(df_filtrado['Valor N.F.'].sum(), 'R$'))
with aba3:
    col1, col2 = st.columns(2)
    with col1:
      top_rotas = df_rotas[['sum']].sort_values('sum', ascending=False).head(7)

        # Criar gráfico de barras
      graficos_rotas = px.bar(
              top_rotas,
              x='sum',
              y=top_rotas.index,
              text=top_rotas['sum'],
              title='Top 7 Rotas com Maior Fluxo',
              color_discrete_sequence=['#1f77b4']  # azul padrão
          )
            # Personalização dos rótulos de dados: dentro da barra, negrito, em reais
      graficos_rotas.update_traces(
          texttemplate='<b>R$ %{text:,.2f}</b>',
          textposition='inside',
          insidetextanchor='start',
          textfont=dict(color='white', size=13)  # cor branca pra destacar dentro da barra
      )

      # Layout formatado
      graficos_rotas.update_layout(
          title_x=0.5,
          title_font_size=20,
          xaxis_title='Valor Total (R$)',
          yaxis_title='Rotas',
          uniformtext_minsize=8,
          uniformtext_mode='hide',
          plot_bgcolor='white',
          xaxis=dict(
              showgrid=True,
              gridcolor='lightgrey',
              tickprefix='R$ ',
              tickformat=',.2f'
          ),
          yaxis=dict(showgrid=False)
      )
     
      st.plotly_chart(graficos_rotas)
      # Ordena os dados
      top_rotas_clientes = df_cliente[['sum']].sort_values('sum', ascending=False).head(7)
      
      
        # Formata os valores como moeda (R$) para exibir como texto
      top_rotas_clientes['sum_formatado'] = top_rotas_clientes['sum'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

        # Cria o gráfico de barras
      grafico_cliente = px.bar(
            top_rotas_clientes,
            x='sum',
            y=top_rotas_clientes.index,
            text='sum_formatado',  # usa os valores formatados
            template='seaborn',
            title='Top 7 Maiores Clientes com Maior Fluxo',
            color_discrete_sequence=['#1f77b4']  # azul padrão
        )

        # Estiliza os rótulos dentro da barra, em negrito e branco
      grafico_cliente.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='inside',
            insidetextanchor='start',
            textfont=dict(color='white', size=13)
        )

        # Ajusta o layout visual
      grafico_cliente.update_layout(
            xaxis_title='Valor Total (R$)',
            yaxis_title='Rotas',
            plot_bgcolor='white'
        )   
      st.plotly_chart(grafico_cliente, use_container_width=True)
    with col2:
              
            # Função para formatar toneladas no estilo brasileiro (1.234,56 t)
        def formatar_toneladas(valor):
            return f"{valor:,.2f} t".replace(',', 'X').replace('.', ',').replace('X', '.')

        # Preparar os dados ordenados e formatar os rótulos
        top_peso_rotas = df_rotas_peso[['sum']].sort_values('sum', ascending=False).head(7)
        top_peso_rotas['sum_formatado'] = top_peso_rotas['sum'].apply(formatar_toneladas)
              # Criar gráfico de barras
        grafico_peso_rotas = px.bar(
            top_peso_rotas,
            #x='sum',
            y=top_peso_rotas.index,
            text='sum_formatado',
            title='Top 7 Rotas com Maior Peso (t)',
            color_discrete_sequence=['#1f77b4']
        )

        # Estilizar os rótulos dentro das barras
        grafico_peso_rotas.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='inside',
            insidetextanchor='start',
            textfont=dict(color='white', size=13)
        )

        # Layout refinado
        grafico_peso_rotas.update_layout(
            title_x=0.5,
            title_font_size=20,
            xaxis_title='Peso Total (toneladas)',
            yaxis_title='Rotas',
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                tickformat=',.2f'  # separador de milhar com ponto e decimal com vírgula
            ),
            yaxis=dict(showgrid=False)
        )
      
        st.plotly_chart(grafico_peso_rotas)
        def formatar_toneladas(valor):
            return f"{valor:,.2f} t".replace(',', 'X').replace('.', ',').replace('X', '.')

        # Preparar os dados ordenados e formatar os rótulos
        top_peso_cliente = df_cliente_peso[['sum']].sort_values('sum', ascending=False).head(7)
        top_peso_cliente['sum_formatado'] = top_peso_cliente['sum'].apply(formatar_toneladas)
          # Cria o gráfico de barras
        grafico_cliente_peso = px.bar(
              top_peso_cliente,
              x='sum',
              y=top_peso_cliente.index,
              text='sum_formatado',  # usa os valores formatados
              template='seaborn',
              title='Top 7 Maiores Clientes por peso',
              color_discrete_sequence=['#1f77b4']  # azul padrão
          )

          # Estiliza os rótulos dentro da barra, em negrito e branco
        grafico_cliente_peso.update_traces(
              texttemplate='<b>%{text}</b>',
              textposition='inside',
              insidetextanchor='start',
              textfont=dict(color='white', size=13)
          )

          # Ajusta o layout visual
        grafico_cliente_peso.update_layout(
              xaxis_title='Valor Total (R$)',
              yaxis_title='Rotas',
              plot_bgcolor='white'
          )   
        st.plotly_chart(grafico_cliente_peso, use_container_width=True)
        dc_rec_diaria['Frete Peso Formatado'] = dc_rec_diaria['Frete Peso'].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
        # Cores suaves
    cores_personalizadas = px.colors.qualitative.Pastel
    grafico_dia_frete_peso = px.bar(
        dc_rec_diaria,
        x='Data',
        y='Frete Peso',
        text='Frete Peso Formatado',
        template='seaborn',
        title='Faturamento de Frete Peso por dia', 
        color='Frete Peso',
        color_continuous_scale=px.colors.sequential.Plasma,
        hover_data={'Frete Peso Formatado': True, 'Frete Peso': False, 'Data': True}
       
    )
    # Estilizar os rótulos dentro das barras
    grafico_dia_frete_peso.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color='white', size=12)
    )
    # Ajustando o tamanho da fonte dos dados do hover
    grafico_dia_frete_peso.update_traces(
          hoverlabel=dict(
              font=dict(
                  size=16  # Ajuste o tamanho da fonte do hover data conforme desejado
              )
            )
        )
    # Layout refinado   
    st.plotly_chart(grafico_dia_frete_peso, use_container_width=True)
        
    def formatar_toneladas(valor):
        return f"{valor:,.2f} ton".replace(',', 'X').replace('.', ',').replace('X', '.')
    
        # Prepara os dados ordenados e formata os rótulos
    top_peso_dia = df_rotas_peso[['sum']].sort_values('sum', ascending=False).head(7)
    top_peso_dia['sum_formatado'] = top_peso_dia['sum'].apply(formatar_toneladas)
    
        # Adiciona coluna formatada ao df diário
    dc_rec_diaria_peso['Peso Taxado Formatado'] = dc_rec_diaria_peso['Peso Taxado'].apply(formatar_toneladas)
    
        # Gráfico com valores formatados
    grafico_dia_peso = px.bar(
            dc_rec_diaria_peso,
            x='Data',
            y='Peso Taxado',
            text='Peso Taxado Formatado',  # Usa texto formatado
            template='seaborn',
            title='Volume de Peso por Dia',
            color='Peso Taxado',
            color_continuous_scale=px.colors.sequential.Plasma,
            hover_data={'Peso Taxado Formatado': True, 'Peso Taxado': False, 'Data': True}
        )
    
        # Estilizar os rótulos dentro das barras
    grafico_dia_peso.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='inside',
            insidetextanchor='start',
            textfont=dict(color='white', size=12)
        )
    
        # Ajusta o tamanho da fonte do hover
    grafico_dia_peso.update_traces(
            hoverlabel=dict(
                font=dict(size=16)
            )
        )
    
        # Layout refinado
    st.plotly_chart(grafico_dia_peso, use_container_width=True)
