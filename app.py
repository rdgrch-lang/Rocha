import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração do App
st.set_page_config(page_title="Gestão Financeira Familiar", layout="centered")

# Inicialização de dados
if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]
if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=['Tipo', 'Valor', 'Categoria'])

st.title("💰 Gestão Financeira Independente")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Gráfico Detalhado"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Nova Entrada")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_in")
    cat_in = st.selectbox("Tipo", st.session_state.cat_entrada + ["Outra..."], key="cat_in")
    
    if cat_in == "Outra...":
        nova = st.text_input("Nome da nova entrada:")
        if st.button("Adicionar Categoria", key="btn_add_in"):
            st.session_state.cat_entrada.append(nova)
            st.rerun()
            
    if st.button("Confirmar Entrada", key="btn_save_in"):
        novo = pd.DataFrame([["Entrada", val_in, cat_in]], columns=['Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
        st.success("Entrada salva!")

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Nova Saída")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_out")
    cat_out = st.selectbox("Tipo", st.session_state.cat_saida + ["Outra..."], key="cat_out")
    
    if cat_out == "Outra...":
        nova_s = st.text_input("Nome da nova saída:")
        if st.button("Adicionar Categoria", key="btn_add_out"):
            st.session_state.cat_saida.append(nova_s)
            st.rerun()

    if st.button("Confirmar Saída", key="btn_save_out"):
        novo = pd.DataFrame([["Saída", val_out, cat_out]], columns=['Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
        st.warning("Saída registrada!")

# --- ABA DE GRÁFICOS (Cores Independentes) ---
with aba_graf:
    st.subheader("Gráfico de Categorias")
    
    if not st.session_state.dados.empty:
        # Paletas de cores solicitadas
        cores_frias = ['#0000FF', '#008000', '#00CED1', '#2E8B57', '#4682B4', '#3CB371']
        cores_quentes = ['#FF0000', '#FF69B4', '#FF4500', '#DC143C', '#DB7093', '#E67E22']
        
        # Mapeamento dinâmico para garantir que cada categoria tenha sua cor
        color_map = {}
        
        # Mapeia Entradas para cores Frias
        for i, cat in enumerate(st.session_state.cat_entrada):
            color_map[cat] = cores_frias[i % len(cores_frias)]
            
        # Mapeia Saídas para cores Quentes
        for i, cat in enumerate(st.session_state.cat_saida):
            color_map[cat] = cores_quentes[i % len(cores_quentes)]
            
        # Criando o gráfico discriminado por CATEGORIA
        fig = px.pie(
            st.session_state.dados, 
            values='Valor', 
            names='Categoria',
            color='Categoria',
            color_discrete_map=color_map,
            hole=0.3,
            title="Distribuição por Categoria (Frio = Entrada | Quente = Saída)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Lance algum valor para visualizar o gráfico detalhado.")
