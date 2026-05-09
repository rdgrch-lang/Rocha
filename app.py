import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página para aproveitar o espaço horizontal
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Inicialização de dados e categorias
if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]
if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=['Tipo', 'Valor', 'Categoria'])

st.title("💰 Painel de Controle Financeiro")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Análise de Dados"])

# --- REGISTRO DE ENTRADAS ---
with aba_in:
    st.subheader("Adicionar Entrada")
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
        st.success("Entrada salva com sucesso!")

# --- REGISTRO DE SAÍDAS ---
with aba_out:
    st.subheader("Adicionar Saída")
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
        st.warning("Gasto registrado!")

# --- VISUALIZAÇÃO GRÁFICA ---
with aba_graf:
    if not st.session_state.dados.empty:
        col1, col2 = st.columns([3, 2]) # Aumentei o espaço para o gráfico de barras

        with col1:
            st.subheader("Detalhamento por Categoria")
            
            # Criando o mapa de cores para as barras
            cores_frias = ['#0000FF', '#008000', '#00CED1', '#4682B4']
            cores_quentes = ['#FF0000', '#FF4500', '#DC143C', '#FF69B4']
            
            color_map = {}
            for i, cat in enumerate(st.session_state.cat_entrada):
                color_map[cat] = cores_frias[i % len(cores_frias)]
            for i, cat in enumerate(st.session_state.cat_saida):
                color_map[cat] = cores_quentes[i % len(cores_quentes)]
            
            # Gráfico de Barras Detalhado
            fig_bar = px.bar(
                st.session_state.dados,
                x='Categoria',
                y='Valor',
                color='Categoria',
                color_discrete_map=color_map,
                text_auto='.2f', # Mostra o valor em cima da barra
                title="Valores por Categoria"
            )
            fig_bar.update_layout(showlegend=False) # Remove legenda para limpar o visual
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("Resumo Global")
            resumo = st.session_state.dados.groupby("Tipo")["Valor"].sum().reset_index()
            
            fig_global = px.pie(
                resumo, 
                values='Valor', 
                names='Tipo',
                color='Tipo',
                color_discrete_map={"Entrada": "blue", "Saída": "red"},
                hole=0.4
            )
            fig_global.update_traces(textinfo='label+percent')
            st.plotly_chart(fig_global, use_container_width=True)
            
        st.divider()
        st.write("### Histórico Completo")
        st.dataframe(st.session_state.dados, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir. Comece lançando valores nas abas de Entrada ou Saída.")
