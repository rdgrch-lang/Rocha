import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração para parecer um app de celular
st.set_page_config(page_title="Família Rocha - Finanças", layout="centered")

# Simulação de categorias conforme sua ideia
if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]
if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=['Tipo', 'Valor', 'Categoria'])

st.title("💰 Gestão Rocha")

# Navegação por Abas (funciona como os links que você pediu)
aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Gráfico"])

with aba_in:
    st.subheader("Nova Entrada")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="in")
    cat_in = st.selectbox("Tipo", st.session_state.cat_entrada + ["Outra..."], key="cat_in")
    
    if cat_in == "Outra...":
        nova = st.text_input("Qual a nova entrada?")
        if st.button("Adicionar"):
            st.session_state.cat_entrada.append(nova)
            st.rerun()
            
    if st.button("Salvar Entrada"):
        novo = pd.DataFrame([["Entrada", val_in, cat_in]], columns=['Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo])
        st.success("Salvo!")

with aba_out:
    st.subheader("Nova Saída")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="out")
    cat_out = st.selectbox("Tipo", st.session_state.cat_saida + ["Outra..."], key="cat_out")
    
    if cat_out == "Outra...":
        nova_s = st.text_input("Qual o novo gasto?")
        if st.button("Adicionar Gasto"):
            st.session_state.cat_saida.append(nova_s)
            st.rerun()

    if st.button("Salvar Saída"):
        novo = pd.DataFrame([["Saída", val_out, cat_out]], columns=['Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo])
        st.warning("Gasto registrado!")

with aba_graf:
    st.subheader("Visão Geral")
    if not st.session_state.dados.empty:
        # Gráfico de Pizza conforme solicitado
        fig = px.pie(st.session_state.dados, values='Valor', names='Categoria', 
                     title='Distribuição de Gastos e Ganhos', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado lançado ainda.")
