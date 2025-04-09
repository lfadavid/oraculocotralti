import plotly.express as px
from utils import dc_rec_estado, dc_rec_mensal, dc_rec_remetente, df_rotas, df_rotas_peso,dc_rec_diaria,df_cliente
import pandas as pd


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

# Gera o gráfico com hover formatado
grafico_map_estado = px.scatter_geo(
    dc_rec_estado, 
    lat='lat', 
    lon='lon',
    scope='south america',
    size='Frete Peso',
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
    title='Receita por Cidade de Destino',
)

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

# Criar gráfico
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
    hover_data={
        'Frete Peso Formatado': True,
        'Variação Formatada': True,
        'Frete Peso': False,
        'Variação (%)': False
    }
)
# Formatação para o DataFrame dc_rec_estado (se necessário)
dc_rec_estado['Frete Peso Formatado'] = dc_rec_estado['Frete Peso'].apply(
    lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Manter apenas as 7 cidades com maior receita
top_cidades = dc_rec_estado.sort_values(by='Frete Peso', ascending=False).head(7)

# Criar gráfico de barras
grafico_rec_cidade = px.bar(
    top_cidades,  
    x='Cidade Destino', 
    y='Frete Peso',
    color='Frete Peso',  # necessário para a escala de cores funcionar
    text='Frete Peso Formatado',  # mostra os valores nas barras com formatação
    labels={'Frete Peso': 'Receita (R$)'},
    color_continuous_scale=px.colors.sequential.Plasma,
    template='seaborn',
    title='Top 7 Cidades por Receita',
    hover_data={'Frete Peso': False, 'Frete Peso Formatado': True}
)

# Rótulo em negrito e fora da barra
grafico_rec_cidade.update_traces(
    texttemplate='<b>%{text}</b>',
    textposition='outside',
    textfont=dict(size=13)
)

# Layout refinado
grafico_rec_cidade.update_layout(
    xaxis_title='Cidade de Destino',
    yaxis_title='Receita (R$)',
    height=600,
    margin=dict(l=0, r=0, t=50, b=0)
)
dc_rec_remetente['Frete Peso Formatado'] = dc_rec_remetente['Frete Peso'].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Cores suaves
cores_personalizadas = px.colors.qualitative.Pastel

# Gráfico de pizza com buraco central (donut)
grafico_rec_remetente = px.pie(
    dc_rec_remetente,
    values='Frete Peso',
    names='Remetente',
    title='Distribuição de Receita por Remetente',
    template='seaborn',
    color_discrete_sequence=cores_personalizadas,
    hole=0.4,
    hover_data=['Frete Peso Formatado']
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
# Dados ordenados
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

# Função para formatar toneladas no estilo brasileiro (1.234,56 t)
def formatar_toneladas(valor):
    return f"{valor:,.2f} t".replace(',', 'X').replace('.', ',').replace('X', '.')

# Preparar os dados ordenados e formatar os rótulos
top_peso_rotas = df_rotas_peso[['sum']].sort_values('sum', ascending=False).head(7)
top_peso_rotas['sum_formatado'] = top_peso_rotas['sum'].apply(formatar_toneladas)

# Criar gráfico de barras
grafico_peso_rotas = px.bar(
    top_peso_rotas,
    x='sum',
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

grafico_rec_diaria = px.bar(
    dc_rec_diaria,
    x='Data',
    y='Frete Peso',
    text='Frete Peso Formatado',
    template='seaborn',
    labels={'Frete Peso': 'Receita (R$)', 'Data': 'Dia'},
    color='Frete Peso',
    color_continuous_scale=px.colors.sequential.Plasma,
    title='Faturamento de Frete Peso ',
    hover_data={'Frete Peso Formatado': True, 'Frete Peso': False, 'Data': True}
)

# Ajusta layout
grafico_rec_diaria.update_layout(
    height=500,
    xaxis_title='Data',
    yaxis_title='Receita (R$)',
    margin=dict(l=0, r=0, t=50, b=100),
    coloraxis_showscale=False
)
