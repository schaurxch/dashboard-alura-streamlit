import streamlit as st # Biblioteca para criar aplicativos web interativos
import requests # Biblioteca para fazer requisições HTTP
import pandas as pd # Biblioteca para manipulação e análise de dados
import plotly.express as px # Biblioteca para criação de gráficos interativos

st.set_page_config(layout='wide')

# Função para formatar números grandes para ficar mais legíveis
def formata_numero(valor, prefixo = ''):
  for unidade in ['', ' mil']:
    if valor < 1000:
      return f'{prefixo}{valor:.2f}{unidade}'
    valor /= 1000
  return f'{prefixo}{valor:.2f} milhões'

# Configurar o título do aplicativo;
st.title('DASHBOARD DE VENDAS :shopping_cart:')

# Fazer a leitura de dados a partir de uma API usando a biblioteca Requests
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
  regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
  ano = ''
else:
  ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', options=dados['Vendedor'].unique())
if filtro_vendedores:
  dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas

### Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(
  subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas de Quantidade de Vendas
vendas_estados = dados.groupby('Local da compra')[['Produto']].count().rename(columns={'Produto': 'Quantidade de Vendas'})
vendas_estados = dados.drop_duplicates(
  subset=['Local da compra'])[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Quantidade de Vendas', ascending=False)

vendas_mensal = dados.set_index('Data da Compra') \
    .groupby(pd.Grouper(freq='M'))['Produto'] \
    .count() \
    .reset_index() \
    .rename(columns={'Produto': 'Quantidade de Vendas'})

vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias =dados.groupby('Categoria do Produto')[['Produto']].count().sort_values('Produto', ascending=False)

### Tabelas de Vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos

### Gráficos de Receita
fig_mapa_receita = px.scatter_geo(receita_estados, lat='lat', lon='lon', scope='south america', size='Preço', template='seaborn', hover_name='Local da compra', hover_data= {'lat':False, 'lon':False}, title='Receita por Estado')

fig_receita_mensal = px.line(receita_mensal, x='Mês', y='Preço', markers=True, range_y=(0, receita_mensal.max()), color='Ano', line_dash='Ano', title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita (R$)')

fig_receita_estados = px.bar(receita_estados.head(), x='Local da compra', y='Preço', text_auto=True, title='Top Estados (Receita)')
fig_receita_estados.update_layout(yaxis_title='Receita (R$)')

fig_receita_categorias = px.bar(receita_categorias, text_auto=True, title='Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title='Receita (R$)')

### Gráficos de Quantidade de Vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados, lat='lat', lon='lon', scope='south america', size='Quantidade de Vendas', template='seaborn', hover_name='Local da compra', hover_data= {'lat':False, 'lon':False}, title='Quantidade de Vendas por Estado')

fig_vendas_estados = px.bar(vendas_estados.head(), x='Local da compra', y='Quantidade de Vendas', text_auto=True, title='Top Estados (Quantidade de Vendas)')

fig_vendas_mensal = px.line(vendas_mensal, x='Mês', y='Quantidade de Vendas', markers=True, range_y=(0, vendas_mensal.max()), color='Ano', line_dash='Ano', title='Quantidade de Vendas Mensal')

fig_vendas_categorias = px.bar(vendas_categorias, text_auto=True, title='Quantidade de Vendas por Categoria')
fig_vendas_categorias.update_layout(yaxis_title='Quantidade de Vendas')

## Visualizações no Streamlit

tab1, tab2, tab3 = st.tabs(['Receitas', 'Quantidade de Vendas', 'Vendedores'])

### Aba 1 - Receita

with tab1:
  col1, col2 = st.columns(2)
  with col1:
    st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_mapa_receita, use_container_width=True)
    st.plotly_chart(fig_receita_estados, use_container_width=True)
  with col2:
    st.metric("Quantidade de Produtos", formata_numero(dados.shape[0]))
    st.plotly_chart(fig_receita_mensal, use_container_width=True)
    st.plotly_chart(fig_receita_categorias, use_container_width=True)

### Aba 2 - Quantidade de Vendas

with tab2:
  col1, col2 = st.columns(2)
  with col1:
    st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_mapa_vendas, use_container_width=True)
    st.plotly_chart(fig_vendas_estados, use_container_width=True)
  with col2:
    st.metric("Quantidade de Produtos", formata_numero(dados.shape[0]))
    st.plotly_chart(fig_vendas_mensal, use_container_width=True)
    st.plotly_chart(fig_vendas_categorias, use_container_width=True)

### Aba 3 - Vendedores

with tab3:
  qtd_vendedores = st.number_input('Quantidade de Vendedores', min_value=2, max_value=10, value=5)
  col1, col2 = st.columns(2)
  with col1:
    st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
    fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                     x= 'sum', 
                                     y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                     text_auto=True,
                                     title=f'Top {qtd_vendedores} Vendedores (Receita)')
    st.plotly_chart(fig_receita_vendedores, use_container_width=True)
  with col2:
    st.metric("Quantidade de Produtos", formata_numero(dados.shape[0]))
    fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                     x= 'count', 
                                     y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                     text_auto=True,
                                     title=f'Top {qtd_vendedores} Vendedores (Vendas)')
    st.plotly_chart(fig_vendas_vendedores, use_container_width=True)

## Exbir DataFrame usando o componente dataframe;
#st.dataframe(dados)
#st.dataframe(vendas_estados)
#st.dataframe(vendas_mensal)