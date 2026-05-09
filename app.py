import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página para parecer um app de celular
st.set_page_config(page_title="Contas da Família Rocha", layout="centered")

# --- BANCO DE DADOS (Simulado por enquanto) ---
# Em breve conectaremos ao seu Google Sheets aqui
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=['Tipo', 'Valor', 'Categoria'])

if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]

if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]

# --- INTERFACE ---
st.title("💰 Gestão Financeira")

aba1, aba2, aba3 = st.tabs(["Início", "Lançamentos", "Gráficos"])

with aba1:
    st.subheader("Resumo Atual")
    total_in = st.session_state.dados[st.session_state.dados['Tipo'] == 'Entrada']['Valor'].sum()
    total_out = st.session_state.dados[st.session_state.dados['Tipo'] == 'Saída']['Valor'].sum()
    st.metric("Saldo", f"R$ {total_in - total_out:.2f}")

with aba2:
    tipo = st.radio("O que deseja registrar?", ["Entrada", "Saída"])
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    
    lista_cat = st.session_state.cat_entrada if tipo == "Entrada" else st.session_state.cat_saida
    categoria = st.selectbox("Categoria", lista_cat + ["Nova Categoria..."])
    
    if categoria == "Nova Categoria...":
        nova = st.text_input("Nome da nova categoria:")
        if st.button("Adicionar Categoria"):
            if tipo == "Entrada": st.session_state.cat_entrada.append(nova)
            else: st.session_state.cat_saida.append(nova)
            st.rerun()

    if st.button("Confirmar Lançamento"):
        novo_dado = pd.DataFrame([[tipo, valor, categoria]], columns=['Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo_dado], ignore_index=True)
        st.success("Lançado com sucesso!")

with aba3:
    st.subheader("Distribuição de Gastos")
    if not st.session_state.dados.empty:
        fig = px.pie(st.session_state.dados, values='Valor', names='Tipo', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ainda não há dados para gerar o gráfico.")
