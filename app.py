import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Teste de Interface Rocha", layout="wide")

# Criando dados fictícios na memória (não salva na planilha)
if 'df_teste_l' not in st.session_state:
    st.session_state.df_teste_l = pd.DataFrame([
        [datetime.now().date(), "Entrada", 5000.00, "Salário"],
        [datetime.now().date(), "Saída", 150.00, "Mercado"]
    ], columns=['Data', 'Tipo', 'Valor', 'Categoria'])

if 'df_teste_c' not in st.session_state:
    st.session_state.df_teste_c = pd.DataFrame([
        ["Entrada", "Salário"],
        ["Entrada", "Pix"],
        ["Saída", "Aluguel"],
        ["Saída", "Cafezinho"]
    ], columns=['Tipo', 'Categoria'])

st.title("💰 Teste de Interface (Sem Planilha)")
st.info("Este é um modo de teste. Os dados abaixo são temporários e não serão salvos.")

# Navegação por abas
aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatórios"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Simular Entrada")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="in_val")
    cat_in = st.selectbox("Categoria", st.session_state.df_teste_c[st.session_state.df_teste_c['Tipo'] == 'Entrada']['Categoria'].tolist(), key="in_cat")
    
    if st.button("Simular Registro", key="btn_save_in"):
        st.success(f"Sucesso! A interface funcionaria para registrar R$ {val_in}")

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Simular Saída")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="out_val")
    cat_out = st.selectbox("Categoria", st.session_state.df_teste_c[st.session_state.df_teste_c['Tipo'] == 'Saída']['Categoria'].tolist(), key="out_cat")
    
    if st.button("Simular Gasto", key="btn_save_out"):
        st.warning(f"Sucesso! A interface funcionaria para gastar R$ {val_out}")

# --- ABA DE RELATÓRIOS ---
with aba_graf:
    st.subheader("📊 Visualização de Gráficos")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(st.session_state.df_teste_l, x='Categoria', y='Valor', color='Tipo',
                         color_discrete_map={"Entrada": "blue", "Saída": "red"})
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        resumo = st.session_state.df_teste_l.groupby("Tipo")["Valor"].sum().reset_index()
        fig_pie = px.pie(resumo, values='Valor', names='Tipo', color='Tipo',
                         color_discrete_map={"Entrada": "blue", "Saída": "red"})
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    st.write("### Histórico Temporário")
    st.dataframe(st.session_state.df_teste_l, use_container_width=True)
