import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Link da sua planilha Google
url = "https://docs.google.com/spreadsheets/d/1-znLPBb__mvWKp1HtJICdzE9gy47PWGfsPQDz1HzNMQ/edit?usp=sharing"

# Criando a conexão (Corrigido para a versão nova)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO PARA CARREGAR DADOS ---
def carregar_dados():
    try:
        # Busca abas com nomes em inglês para evitar erros de sistema
        df_t = conn.read(spreadsheet=url, worksheet="Transactions", ttl="0s")
        df_c = conn.read(spreadsheet=url, worksheet="Categories", ttl="0s")
        
        if not df_t.empty and 'Date' in df_t.columns:
            # Garante que o sistema entenda que o dia vem antes do mês (Brasil)
            df_t['Date'] = pd.to_datetime(df_t['Date'], dayfirst=True, errors='coerce')
            df_t = df_t.dropna(subset=['Date'])
        
        return df_t, df_c
    except Exception as e:
        st.error(f"Erro de conexão: Verifique se as abas se chamam 'Transactions' e 'Categories'.")
        return pd.DataFrame(columns=['Date', 'Type', 'Value', 'Category']), pd.DataFrame(columns=['Type', 'Category'])

df_transactions, df_categories = carregar_dados()

st.title("💰 Gestão Rocha")

# Navegação por abas
aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatórios"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Inserir Valor Recebido")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="in_val")
    
    # Filtra por 'Income' (Entrada) na planilha
    list_cat_in = df_categories[df_categories['Type'] == 'Income']['Category'].tolist() if not df_categories.empty else []
    cat_in = st.selectbox("Selecione a Entrada", list_cat_in + ["Outra..."], key="in_cat")
    
    if st.button("Inserir Entrada", key="btn_save_in"):
        if val_in > 0:
            new_row = pd.DataFrame([[datetime.now().date(), "Income", val_in, cat_in]], 
                                   columns=['Date', 'Type', 'Value', 'Category'])
            df_final = pd.concat([df_transactions, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Transactions", data=df_final)
            st.success("Entrada inserida com sucesso!")
            st.rerun()

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Inserir Gasto")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="out_val")
    
    # Filtra por 'Expense' (Saída) na planilha
    list_cat_out = df_categories[df_categories['Type'] == 'Expense']['Category'].tolist() if not df_categories.empty else []
    cat_out = st.selectbox("Selecione o tipo de Gasto", list_cat_out + ["Outra..."], key="out_cat")
    
    if st.button("Inserir Saída", key="btn_save_out"):
        if val_out > 0:
            new_row = pd.DataFrame([[datetime.now().date(), "Expense", val_out, cat_out]], 
                                   columns=['Date', 'Type', 'Value', 'Category'])
            df_final = pd.concat([df_transactions, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Transactions", data=df_final)
            st.warning("Gasto inserido na planilha!")
            st.rerun()

# --- ABA DE RELATÓRIOS ---
with aba_graf:
    if not df_transactions.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Resumo por Categoria**")
            fig_bar = px.bar(df_transactions, x='Category', y='Value', color='Type',
                             color_discrete_map={"Income": "blue", "Expense": "red"})
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.write("**Balanço Geral**")
            summary = df_transactions.groupby("Type")["Value"].sum().reset_index()
            fig_pie = px.pie(summary, values='Value', names='Type', 
                             color='Type', color_discrete_map={"Income": "blue", "Expense": "red"})
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        st.write("### Histórico de Movimentações")
        df_view = df_transactions.copy()
        df_view['Date'] = df_view['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_view.sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.info("Lance um valor para ver os gráficos.")
