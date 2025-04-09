import pandas as pd

df = pd.read_excel("dados/1.xlsx", index_col=0)

df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Peso Taxado'] = df['Peso Taxado'].astype(float).round(2).replace(',', '.')
df['Frete Peso'] = df['Frete Peso'].astype(float).round(2).replace(',', '.')
df['Valor N.F.'] = df['Valor N.F.'].astype(float).round(2).replace(',', '.')

