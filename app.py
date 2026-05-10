import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Link da sua nova folha de cálculo Google (Nativa)
url = "https://docs.google.com/spreadsheets/d/1-znLPBb__mvWKp1HtJICdzE9gy47PWGfsPQDz1HzNMQ/edit?usp=sharing"

# Criando a conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO PARA CARREGAR DADOS (Versão Segura) ---
def carregar_dados():
    try:
        # Tenta ler as abas Lancamentos e Categorias
        df_l = conn.read(spreadsheet=url, worksheet="Lancamentos", ttl="0s")
        df_c = conn.read(spreadsheet=url, worksheet="Categorias", ttl="0s")
        
        # Converte a coluna Data para o formato correto, se houver dados
        if not df_l.empty and 'Data' in df_l.columns:
            df_l['Data'] = pd.to_datetime(df_l['Data'], errors='coerce')
        
        return df_l, df_c
    except Exception as e:
        # Se der erro, mostra o aviso mas não trava o app
        st.error(f"Aguardando conexão com a planilha... Verifique se as abas 'Lancamentos' e 'Categorias' existem.")
        return pd.DataFrame(columns=['Data', 'Tipo', 'Valor', 'Categoria']), pd.DataFrame(columns=['Tipo', 'Categoria'])

df_lancamentos, df_categorias = carregar_dados()

st.title("💰 Gestão Rocha")

# Navegação por abas
aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatórios"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Registrar Valor Recebido")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="in_val")
    
    # Filtra categorias do tipo Entrada
    lista_cat_in = df_categorias[df_categorias['Tipo'] == 'Entrada']['Categoria'].tolist() if not df_categorias.empty else []
    cat_in = st.selectbox("Selecione a Entrada", lista_cat_in + ["Outra..."], key="in_cat")
    
    if cat_in == "Outra...":
        nova_cat_in = st.text_input("Nome da nova categoria de entrada:")
        if st.button("Cadastrar Categoria", key="btn_new_in"):
            if nova_cat_in:
                nova_linha = pd.DataFrame([["Entrada", nova_cat_in]], columns=['Tipo', 'Categoria'])
                df_atualizado = pd.concat([df_categorias, nova_linha], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categorias", data=df_atualizado)
                st.success("Categoria adicionada!")
                st.rerun()

    if st.button("Confirmar Entrada", key="btn_save_in"):
        if val_in > 0:
            hoje = datetime.now().date()
            nova_entrada = pd.DataFrame([[hoje, "Entrada", val_in, cat_in]], columns=['Data', 'Tipo', 'Valor', 'Categoria'])
            df_final = pd.concat([df_lancamentos, nova_entrada], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Lancamentos", data=df_final)
            st.success("Entrada salva!")
            st.rerun()

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Registrar Gasto")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="out_val")
    
    # Filtra categorias do tipo Saída
    lista_cat_out = df_categorias[df_categorias['Tipo'] == 'Saída']['Categoria'].tolist() if not df_categorias.empty else []
    cat_out = st.selectbox("Selecione o tipo de Gasto", lista_cat_out + ["Outra..."], key="out_cat")
    
    if cat_out == "Outra...":
        nova_cat_out = st.text_input("Nome do novo gasto:")
        if st.button("Cadastrar Gasto", key="btn_new_out"):
            if nova_cat_out:
                nova_linha = pd.DataFrame([["Saída", nova_cat_out]], columns=['Tipo', 'Categoria'])
                df_atualizado = pd.concat([df_categorias, nova_linha], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categorias", data=df_atualizado)
                st.success("Novo tipo de gasto cadastrado!")
                st.rerun()

    if st.button("Confirmar Saída", key="btn_save_out"):
        if val_out > 0:
            hoje = datetime.now().date()
            nova_saida = pd.DataFrame([[hoje, "Saída", val_out, cat_out]], columns=['Data', 'Tipo', 'Valor', 'Categoria'])
            df_final = pd.concat([df_lancamentos, nova_saida], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Lancamentos", data=df_final)
            st.warning("Gasto registrado!")
            st.rerun()

# --- ABA DE RELATÓRIOS ---
with aba_graf:
    hoje = datetime.now()
    st.subheader(f"📊 Resumo de {hoje.strftime('%B / %Y')}")
    
    if not df_lancamentos.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Gastos por Categoria**")
            fig_bar = px.bar(df_lancamentos, x='Categoria', y='Valor', color='Tipo',
                             color_discrete_map={"Entrada": "#1f77b4", "Saída": "#e74c3c"})
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.write("**Balanço (Entrada vs Saída)**")
            resumo = df_lancamentos.groupby("Tipo")["Valor"].sum().reset_index()
            fig_pie = px.pie(resumo, values='Valor', names='Tipo',
                             color='Tipo', color_discrete_map={"Entrada": "blue", "Saída": "red"})
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        st.dataframe(df_lancamentos.sort_values(by='Data', ascending=False), use_container_width=True)
    else:
        st.info("Lance um valor para ver o gráfico.")
