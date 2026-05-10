import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Link da sua planilha
url = "https://docs.google.com/spreadsheets/d/1-znLPBb__mvWKp1HtJICdzE9gy47PWGfsPQDz1HzNMQ/edit?usp=sharing"

# Criando a conexão
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        df_t = conn.read(spreadsheet=url, worksheet="Transactions", ttl="0s")
        df_c = conn.read(spreadsheet=url, worksheet="Categories", ttl="0s")
        
        if not df_t.empty and 'Date' in df_t.columns:
            df_t['Date'] = pd.to_datetime(df_t['Date'], dayfirst=True, errors='coerce')
            df_t = df_t.dropna(subset=['Date'])
        
        return df_t, df_c
    except Exception as e:
        st.error(f"🚨 ERRO DE CONEXÃO: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_transactions, df_categories = carregar_dados()

st.title("💰 Gestão Rocha")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatórios"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Inserir Valor Recebido")
    val_in = st.number_input("Valor Recebido (R$)", min_value=0.0, format="%.2f", key="in_val")
    
    list_cat_in = df_categories[df_categories['Type'] == 'Income']['Category'].tolist() if not df_categories.empty else []
    cat_in = st.selectbox("Selecione a Entrada", list_cat_in + ["Outra..."], key="in_cat")
    
    # Se escolher "Outra...", abre o campo para digitar
    if cat_in == "Outra...":
        nova_cat_in = st.text_input("📝 Digite o nome da nova Entrada (Ex: Venda, Bônus):", key="new_in_cat")
        cat_final_in = nova_cat_in
    else:
        cat_final_in = cat_in
    
    if st.button("Inserir Entrada", key="btn_save_in"):
        if val_in > 0 and cat_final_in:
            # 1. Grava a transação
            new_row = pd.DataFrame([[datetime.now().date(), "Income", val_in, cat_final_in]], 
                                   columns=['Date', 'Type', 'Value', 'Category'])
            df_final = pd.concat([df_transactions, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Transactions", data=df_final)
            
            # 2. Se for categoria nova, salva ela na aba Categories
            if cat_in == "Outra...":
                new_cat_row = pd.DataFrame([["Income", cat_final_in]], columns=['Type', 'Category'])
                df_cat_final = pd.concat([df_categories, new_cat_row], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categories", data=df_cat_final)
                
            st.success(f"Entrada de R$ {val_in} em '{cat_final_in}' inserida com sucesso!")
            st.rerun()

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Inserir Gasto")
    val_out = st.number_input("Valor Gasto (R$)", min_value=0.0, format="%.2f", key="out_val")
    
    list_cat_out = df_categories[df_categories['Type'] == 'Expense']['Category'].tolist() if not df_categories.empty else []
    cat_out = st.selectbox("Selecione o tipo de Gasto", list_cat_out + ["Outra..."], key="out_cat")
    
    # Se escolher "Outra...", abre o campo para digitar
    if cat_out == "Outra...":
        nova_cat_out = st.text_input("📝 Digite o nome do novo Gasto (Ex: Doces, Viagem, Conta de Luz):", key="new_out_cat")
        cat_final_out = nova_cat_out
    else:
        cat_final_out = cat_out
    
    if st.button("Inserir Saída", key="btn_save_out"):
        if val_out > 0 and cat_final_out:
            # 1. Grava a transação
            new_row = pd.DataFrame([[datetime.now().date(), "Expense", val_out, cat_final_out]], 
                                   columns=['Date', 'Type', 'Value', 'Category'])
            df_final = pd.concat([df_transactions, new_row], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Transactions", data=df_final)
            
            # 2. Se for categoria nova, salva ela na aba Categories
            if cat_out == "Outra...":
                new_cat_row = pd.DataFrame([["Expense", cat_final_out]], columns=['Type', 'Category'])
                df_cat_final = pd.concat([df_categories, new_cat_row], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categories", data=df_cat_final)
                
            st.warning(f"Gasto de R$ {val_out} com '{cat_final_out}' registrado!")
            st.rerun()

# --- ABA DE RELATÓRIOS ---
with aba_graf:
    if not df_transactions.empty:
        try:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Gastos por Categoria**")
                fig_bar = px.bar(df_transactions, x='Category', y='Value', color='Type', 
                                 color_discrete_map={"Income": "#00CC96", "Expense": "#EF553B"})
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.write("**Balanço Geral (Pizza)**")
                summary = df_transactions.groupby("Type")["Value"].sum().reset_index()
                fig_pie = px.pie(summary, values='Value', names='Type', 
                                 color='Type', color_discrete_map={"Income": "#00CC96", "Expense": "#EF553B"})
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.divider()
            st.write("### Histórico")
            st.dataframe(df_transactions, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráficos: {e}")
    else:
        st.info("Ainda não há dados para gerar os gráficos. Insira uma entrada ou saída primeiro!")
                            
