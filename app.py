import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

url = "https://docs.google.com/spreadsheets/d/1-znLPBb__mvWKp1HtJICdzE9gy47PWGfsPQDz1HzNMQ/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Função de carga com proteção de cache
@st.cache_data(ttl=10)
def carregar_dados():
    try:
        df_t = conn.read(spreadsheet=url, worksheet="Transactions")
        df_c = conn.read(spreadsheet=url, worksheet="Categories")
        return df_t, df_c
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

# Limpeza manual de cache para garantir dados novos
if st.sidebar.button("🔄 Atualizar Dados Manualmente"):
    st.cache_data.clear()
    st.rerun()

df_transactions, df_categories = carregar_dados()

st.title("💰 Gestão Rocha")
aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatórios"])
hoje = datetime.now().strftime("%d/%m/%Y")

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Inserir Valor Recebido")
    val_in = st.number_input("Quanto você recebeu? (R$)", min_value=0.0, format="%.2f", key="in_val")
    
    list_cat_in = df_categories[df_categories['Type'] == 'Income']['Category'].tolist() if not df_categories.empty else []
    cat_in = st.selectbox("Selecione a Origem", list_cat_in + ["Outra..."], key="in_cat")
    
    cat_final_in = ""
    if cat_in == "Outra...":
        cat_final_in = st.text_input("📝 Nome da nova Entrada (Ex: Salário, Venda):", key="new_in_cat")
    else:
        cat_final_in = cat_in
    
    if st.button("Confirmar Entrada", key="btn_save_in"):
        if val_in <= 0:
            st.error("Digite um valor maior que zero!")
        elif not cat_final_in or cat_final_in == "Outra...":
            st.error("Por favor, digite o nome da categoria no campo acima!")
        else:
            new_row = pd.DataFrame([[hoje, "Income", val_in, cat_final_in]], columns=['Date', 'Type', 'Value', 'Category'])
            df_final = pd.concat([df_transactions, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Transactions", data=df_final)
            
            if cat_in == "Outra...":
                new_cat_row = pd.DataFrame([["Income", cat_final_in]], columns=['Type', 'Category'])
                df_cat_merged = pd.concat([df_categories, new_cat_row], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categories", data=df_cat_merged)
            
            st.cache_data.clear()
            st.success("✅ Gravado com sucesso!")
            st.rerun()

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Inserir Gasto")
    val_out = st.number_input("Quanto você gastou? (R$)", min_value=0.0, format="%.2f", key="out_val")
    
    list_cat_out = df_categories[df_categories['Type'] == 'Expense']['Category'].tolist() if not df_categories.empty else []
    cat_out = st.selectbox("Selecione o Gasto", list_cat_out + ["Outra..."], key="out_cat")
    
    cat_final_out = ""
    if cat_out == "Outra...":
        cat_final_out = st.text_input("📝 Nome do novo Gasto (Ex: Mercado, Luz, Doces):", key="new_out_cat")
    else:
        cat_final_out = cat_out
    
    if st.button("Confirmar Saída", key="btn_save_out"):
        if val_out <= 0:
            st.error("Digite um valor maior que zero!")
        elif not cat_final_out or cat_final_out == "Outra...":
            st.error("Por favor, digite o nome da categoria no campo acima!")
        else:
            new_row = pd.DataFrame([[hoje, "Expense", val_out, cat_final_out]], columns=['Date', 'Type', 'Value', 'Category'])
            df_final = pd.concat([df_transactions, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Transactions", data=df_final)
            
            if cat_out == "Outra...":
                new_cat_row = pd.DataFrame([["Expense", cat_final_out]], columns=['Type', 'Category'])
                df_cat_merged = pd.concat([df_categories, new_cat_row], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categories", data=df_cat_merged)
            
            st.cache_data.clear()
            st.warning("⚠️ Gasto registrado na planilha!")
            st.rerun()

# --- ABA DE RELATÓRIOS ---
with aba_graf:
    if not df_transactions.empty:
        df_transactions['Date'] = pd.to_datetime(df_transactions['Date'], dayfirst=True, errors='coerce')
        
        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(df_transactions, x='Category', y='Value', color='Type', 
                             title="Gastos e Entradas por Categoria",
                             color_discrete_map={"Income": "#00CC96", "Expense": "#EF553B"})
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            summary = df_transactions.groupby("Type")["Value"].sum().reset_index()
            fig_pie = px.pie(summary, values='Value', names='Type', title="Balanço Geral",
                             color='Type', color_discrete_map={"Income": "#00CC96", "Expense": "#EF553B"})
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        st.write("### 📜 Histórico Recente")
        st.dataframe(df_transactions.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Nenhum dado encontrado. Faça o seu primeiro lançamento!")
                            
