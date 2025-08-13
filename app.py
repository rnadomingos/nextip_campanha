import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variaveis de ambiente

load_dotenv()

# Recebe variaveis de ambiente

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"



def conectar_banco():
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

sql_listagem_geral = """SELECT c.calldate,
                    c.nrilha as ilha,
                    c.nomeilha as 'Nome Ilha',
                    c.nragente as agente,
                    c.nomeagente as 'Nome Agente',
                    c.espera,
                    c.duracao,
                    c.numero as Telefone, 
                    c.status,
                    c.statusdeduzir,
                    c.statusretorno,
                    c.dataretorno,
                    c.categoria as Categoria,
                    c.subcategorias as 'Classificacao',
                    c.tags
                FROM nipview.n_cdr_ilha_categoria_view c
                WHERE c.calldate >= '2025-08-11'
            """

# Função para carregar dados do banco de dados
def carregar_dados(engine):
    if engine:
        try:
            data = pd.read_sql(sql_listagem_geral, engine)
            return data
        except Exception as e:
            st.error(f"Erro ao carregar os dados do banco de dados: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Função para exibir os dados
def exibir_dados(data):
    st.header("Dados de Classificações")
    st.dataframe(data)

# Função para plotar gráficos de experiência técnica
def plotar_graficos_classificacoes(data):
    st.header("Qualificações")

        
    df_t1 = (
        data[data['Classificacao'].notna()]  # WHERE c.subcategorias IS NOT NULL
        .assign(
            Categoria=lambda x: x['Categoria']
                .str.replace('ALPHA', '', regex=False)
                .str.replace('OMEGA', '', regex=False),
            Classificacao=lambda x: x['Classificacao']
                .str.replace('ALPHA GMM', '', regex=False)
                .str.replace('OMEGA GMM', '', regex=False)
                .str.replace('ALPHA', '', regex=False)
                .str.replace('OMEGA', '', regex=False)
        )
        .sort_values('Categoria', ascending=False)  # ORDER BY 1 DESC
    )

    # Agrupamento final
    resultado = (
        df_t1
        .groupby(['Categoria', 'Classificacao'])
        .size()
        .reset_index(name='Qtde')
        .sort_values(['Categoria', 'Qtde'], ascending=[True, False])  # ORDER BY 1, 3 DESC
    )

    df_nacoes = resultado[resultado['Categoria'].str.contains('Toyota Nacoes', case=False, na=False)]
    df_morumbi = resultado[resultado['Categoria'].str.contains('Toyota Morumbi', case=False, na=False)]

    st.subheader("Toyota Nacoes")

    st.bar_chart(df_nacoes.set_index('Classificacao')['Qtde'], horizontal=True, use_container_width=True )

    
    st.subheader("Toyota Morumbi")
    st.bar_chart(df_morumbi.set_index('Classificacao')['Qtde'], horizontal=True,) 

# Função para plotar gráficos de experiência técnica
def metricas_ligacoes_gerais(data):

    st.subheader("Total Ligações")
    col1,col2, col3 = st.columns(3)

    with col1:
        
        total_ligacoes = len(data)
        st.metric("Ligações Atendidas", value=total_ligacoes, delta='100 %', border=True)
        
    with col2:

        total_ligacoes_qualificadas = data['Classificacao'].notna().sum()
        delta_qulificadas = round((total_ligacoes_qualificadas / total_ligacoes)*100,2)

        st.metric("Ligações Qualificadas", value=total_ligacoes_qualificadas, delta=f'{delta_qulificadas} %', border=True)

    with col3:

        total_ligacoes_nao_qualificadas = data['Classificacao'].isnull().sum()
        delta_nao_qulificadas = round((total_ligacoes_nao_qualificadas / total_ligacoes)*100,2)

        st.metric("Ligações Não Qualificadas", value=total_ligacoes_nao_qualificadas, delta=f'{delta_nao_qulificadas} %', border=True, width="stretch")        

def metricas_confirmados_nacoes(data):

    st.subheader("Confirmados Nações", divider='red')
    col1,col2, col3 = st.columns(3)

    with col1:
        
        confirmados_nac = data[data['Categoria'].str.contains('Toyota Nacoes', case=False, na=False)]
        confirmados_nac['Nacoes'] = 'Toyota Nacoes'

        df_nacoes = (
        confirmados_nac[confirmados_nac['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Nacoes'])
        .size()
        )

        # Extrair valor numerico da série
        valor_confirmados_nacoes = df_nacoes.iloc[0]
        
        st.metric("Total de Confirmados", value=valor_confirmados_nacoes, delta='100 %', border=True)
        
    with col2:

        total_nacoes_alpha = data[data['Categoria'].str.contains('Toyota Nacoes ALPHA', case=False, na=False)]

        df_nacoes_alpha = (
        total_nacoes_alpha[total_nacoes_alpha['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Categoria'])
        .size()
        )
    
        # Extrair valor numérico da série
        valor_confirmados_alpha = df_nacoes_alpha.iloc[0]

        delta_confirmados_alpha = round((valor_confirmados_alpha / valor_confirmados_nacoes)*100,2)
        st.metric("Confirmados Alpha", value=valor_confirmados_alpha, delta=f'{delta_confirmados_alpha} %', border=True)

    with col3:

        total_nacoes_omega = data[data['Categoria'].str.contains('Toyota Nacoes OMEGA', case=False, na=False)]

        df_nacoes_omega = (
        total_nacoes_omega[total_nacoes_omega['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Categoria'])
        .size()
        )

        # Extrair valor numerico da serie

        valor_confirmados_omega = df_nacoes_omega.iloc[0]

        delta_confirmados_omega = round((valor_confirmados_omega / valor_confirmados_nacoes)*100,2)
        st.metric("Confirmados Omega", value=valor_confirmados_omega, delta=f'{delta_confirmados_omega} %', border=True)   

def metricas_confirmados_morumbi(data):

    st.subheader("Confirmados Mormbi", divider='blue')
    col1,col2, col3 = st.columns(3)

    with col1:
        
        confirmados_nac = data[data['Categoria'].str.contains('Toyota morumbi', case=False, na=False)]
        confirmados_nac['Morumbi'] = 'Toyota morumbi'

        df_morumbi = (
        confirmados_nac[confirmados_nac['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Morumbi'])
        .size()
        )

        # Extrair valor numerico da série
        valor_confirmados_morumbi = df_morumbi.iloc[0]

        st.metric("Total de Confirmados", value=valor_confirmados_morumbi, delta='100 %', border=True)
        
    with col2:

        total_morumbi_alpha = data[data['Categoria'].str.contains('Toyota Morumbi ALPHA', case=False, na=False)]

        df_morumbi_alpha = (
        total_morumbi_alpha[total_morumbi_alpha['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Categoria'])
        .size()
        )
    
        # Extrair valor numérico da série
        valor_confirmados_alpha = df_morumbi_alpha.iloc[0]

        delta_confirmados_alpha = round((valor_confirmados_alpha / valor_confirmados_morumbi)*100,2)
        st.metric("Confirmados Alpha", value=valor_confirmados_alpha, delta=f'{delta_confirmados_alpha} %', border=True)

    with col3:

        total_morumbi_omega = data[data['Categoria'].str.contains('Toyota Morumbi OMEGA', case=False, na=False)]

        df_morumbi_omega = (
        total_morumbi_omega[total_morumbi_omega['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Categoria'])
        .size()
        )

        # Extrair valor numerico da serie

        valor_confirmados_omega = df_morumbi_omega.iloc[0]

        delta_confirmados_omega = round((valor_confirmados_omega / valor_confirmados_morumbi)*100,2)
        st.metric("Confirmados Omega", value=valor_confirmados_omega, delta=f'{delta_confirmados_omega} %', border=True)              


def resumo_confirmados(data):


    metricas_confirmados_nacoes(data)

    st.subheader('Confirmação por Agente', divider='red', )
    col1, col2, col3 = st.columns(3)

    with col1:
        toy_nacoes_por_agente = data[data['Categoria'].str.contains('Toyota Nacoes', case=False, na=False)]
        df_nacoes_por_agente = (
        toy_nacoes_por_agente[toy_nacoes_por_agente['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Nome Agente', 'Categoria'])
        .size()
        .reset_index(name='Qtde')
        .sort_values('Qtde',ascending=False)
        )

        st.text('Toyota Nações', )
        st.dataframe(df_nacoes_por_agente.drop(columns=['Categoria']), hide_index=True)
    

    with col2:

        toy_nacoes_alpha = data[data['Categoria'].str.contains('Toyota Nacoes ALPHA', case=False, na=False)]

        df_nacoes_alpha_agente = (
            toy_nacoes_alpha[toy_nacoes_alpha['Classificacao'].str.startswith('CONFIRMADO', na=False)]
            .groupby(['Nome Agente', 'Categoria'])
            .size()
            .reset_index(name='Qtde')
            .sort_values('Qtde',ascending=False)  # ORDER BY 1 → coluna 'categoria'
        )
        st.text('Toyota Nações Alpha')
        st.dataframe(df_nacoes_alpha_agente.drop(columns=['Categoria']), hide_index=True)

    with col3:
        toy_nacoes_omega = data[data['Categoria'].str.contains('Toyota Nacoes OMEGA', case=False, na=False)]

        df_nacoes_omega_agente = (
            toy_nacoes_omega[toy_nacoes_omega['Classificacao'].str.startswith('CONFIRMADO', na=False)]
            .groupby(['Nome Agente', 'Categoria'])
            .size()
            .reset_index(name='Qtde')
            .sort_values('Qtde',ascending=False)  # ORDER BY 1 → coluna 'categoria'
        )

        st.text('Toyota Nações Omega')
        st.dataframe(df_nacoes_omega_agente.drop(columns=['Categoria']), hide_index=True)


    metricas_confirmados_morumbi(data)
    
    st.subheader('Confirmação por Agente', divider='blue', )
    col4, col5, col6 = st.columns(3)

    with col4:
        toy_morumbi_por_agente = data[data['Categoria'].str.contains('Toyota Morumbi', case=False, na=False)]
        df_morumbi_por_agente = (
        toy_morumbi_por_agente[toy_morumbi_por_agente['Classificacao'].str.startswith('CONFIRMADO', na=False)]
        .groupby(['Nome Agente', 'Categoria'])
        .size()
        .reset_index(name='Qtde')
        .sort_values('Qtde',ascending=False)
        )

        st.text('Toyota Morumbi', )
        st.dataframe(df_morumbi_por_agente.drop(columns=['Categoria']), hide_index=True)
    
    with col5:

        toy_morumbi_alpha = data[data['Categoria'].str.contains('Toyota Morumbi ALPHA', case=False, na=False)]

        df_morumbi_alpha_agente = (
            toy_morumbi_alpha[toy_morumbi_alpha['Classificacao'].str.startswith('CONFIRMADO', na=False)]
            .groupby(['Nome Agente', 'Categoria'])
            .size()
            .reset_index(name='Qtde')
            .sort_values('Qtde',ascending=False)
        )
        st.text('Toyota Morumbi Alpha')
        st.dataframe(df_morumbi_alpha_agente.drop(columns=['Categoria']), hide_index=True)

    with col6:
        toy_morumbi_omega = data[data['Categoria'].str.contains('Toyota Morumbi OMEGA', case=False, na=False)]

        df_morumbi_omega_agente = (
            toy_morumbi_omega[toy_morumbi_omega['Classificacao'].str.startswith('CONFIRMADO', na=False)]
            .groupby(['Nome Agente', 'Categoria'])
            .size()
            .reset_index(name='Qtde')
            .sort_values('Qtde',ascending=False)  # ORDER BY 1 → coluna 'categoria'
        )

        st.text('Toyota Morumbi Omega')
        st.dataframe(df_morumbi_omega_agente.drop(columns=['Categoria']), hide_index=True)
    

        
# Chamar as funções para exibir os dados e gráficos
st.title("Campanha de Vendas Toyota")

st.set_page_config(
    page_title='Campanha Nextip',
    page_icon='📞',
    layout='wide'
)

# Carregar os dados do banco de dados
engine = conectar_banco()

data = carregar_dados(engine)
metricas_ligacoes_gerais(data)  
resumo_confirmados(data)
#plotar_graficos_classificacoes(data)
#exibir_dados(data_general)
#plotar_grafico_area(data_general)
