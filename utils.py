from dataset import df
import pandas as pd

def format_number(value, prefix = ''):
    for unit in ['', 'mil']:
        if value < 1000:
            return f'{prefix} {value:.2f} {unit}'
        value /= 1000
    return f'{prefix} {value:.2f} milhões'    

# Dataframe com as cidades de destino e suas respectivas latitudes e longitudes
dc_rec_estado = df.groupby('Cidade Destino')[['Frete Peso']].sum()
dc_rec_estado = df.drop_duplicates(subset='Cidade Destino')[['Cidade Destino', 'lat', 'lon']].merge(dc_rec_estado, left_on='Cidade Destino', right_index=True).sort_values('Frete Peso', ascending=False)

# DataFrame com as receitas mensais

dc_rec_mensal = df.set_index('Data').groupby(pd.Grouper(freq='ME'))['Frete Peso'].sum().reset_index()
dc_rec_mensal['Mes'] = dc_rec_mensal['Data'].dt.month_name()
dc_rec_mensal['Ano'] = dc_rec_mensal['Data'].dt.year
dc_rec_diaria = df.set_index('Data').groupby(pd.Grouper(freq='D'))['Frete Peso'].sum().reset_index()
dc_rec_diaria['Dia'] = dc_rec_diaria['Data'].dt.day_name()

dc_rec_remetente = df.groupby('Remetente')[['Frete Peso']].sum()
dc_rec_remetente = df.drop_duplicates(subset='Remetente')[['Remetente', 'lat', 'lon']].merge(dc_rec_remetente, left_on='Remetente', right_index=True).sort_values('Frete Peso', ascending=False)
#dc_rec_remetente = dc_rec_remetente.rename(columns={'Remetente': 'Cidade Remetente'})

df_rotas = pd.DataFrame(df.groupby('Tabela de Preço')['Frete Peso'].agg(['sum','count']))
df_cliente = pd.DataFrame(df.groupby('Cliente')['Frete Peso'].agg(['sum','count']))
df_cliente_peso = pd.DataFrame(df.groupby('Cliente')['Peso Taxado'].agg(['sum','count']))
df_rotas_peso = pd.DataFrame(df.groupby('Tabela de Preço')['Peso Taxado'].agg(['sum','count']))
dc_rec_diaria = df.set_index('Data').groupby(pd.Grouper(freq='D'))['Frete Peso'].sum().reset_index()

# Adiciona nome do dia da semana em português
dc_rec_diaria['Dia'] = dc_rec_diaria['Data'].dt.strftime('%A')

# Formata o valor do frete para exibição
dc_rec_diaria['Frete Peso Formatado'] = dc_rec_diaria['Frete Peso'].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))

#_-----------------------------------------------------------------------

def filtrar_dados(df, filtro_remetente, filtro_mes):
    """Filtra o DataFrame com base nos filtros de remetente e mês."""
    df['Mes'] = df['Data'].dt.strftime('%B')  # Adiciona coluna com nome do mês
    if filtro_remetente:
        df = df[df['Remetente'].isin(filtro_remetente)]

    if filtro_mes:
        df = df[df['Mes'].isin(filtro_mes)]
    
    return df