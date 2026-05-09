import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Inicialização de dados
if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]
if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=['Tipo', 'Valor', 'Categoria'])

st.title("💰 Painel Financeiro Familiar")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Análise Gráfica"])

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

# --- ABA DE GRÁFICOS PARALELOS ---
with aba_graf:
    if not st.session_state.dados.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Categorias Detalhadas")
            # Definindo paletas
            cores_frias = ['#0000FF', '#008000', '#00CED1', '#4682B4']
            cores_quentes = ['#FF0000', '#FF4500', '#DC143C', '#FF69B4']
            
            color_map = {}
            for i, cat in enumerate(st.session_state.cat_entrada):
                color_map[cat] = cores_frias[i % len(cores_frias)]
            for i, cat in enumerate(st.session_state.cat_saida):
                color_map[cat] = cores_quentes[i % len(cores_quentes)]
            
            fig_det = px.pie(
                st.session_state.dados, 
                values='Valor', 
                names='Categoria',
                color='Categoria',
                color_discrete_map=color_map,
                hole=0.3
            )
            # A mágica aqui: mostra o nome (label) em vez de porcentagem
            fig_det.update_traces(textinfo='label')
            st.plotly_chart(fig_det, use_container_width=True)

        with col2:
            st.subheader("Entradas vs Saídas (Global)")
            resumo = st.session_state.dados.groupby("Tipo")["Valor"].sum().reset_index()
            
            fig_global = px.pie(
                resumo, 
                values='Valor', 
                names='Tipo',
                color='Tipo',
                color_discrete_map={"Entrada": "blue", "Saída": "red"},
                hole=0.3
            )
            fig_global.update_traces(textinfo='label+value')
            st.plotly_chart(fig_global, use_container_width=True)
            
        st.write("---")
        st.write("### Histórico de Lançamentos")
        st.dataframe(st.session_state.dados, use_container_width=True)
    else:
        st.info("Lance algum valor para visualizar os gráficos.")
