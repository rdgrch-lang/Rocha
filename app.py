import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração visual do App
st.set_page_config(page_title="Gestão Financeira Rocha", layout="centered")

# Inicialização de estados (categorias e dados)
if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]
if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=['Tipo', 'Valor', 'Categoria'])

st.title("💰 Gestão de Contas")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Gráfico"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Registrar Ganho")
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
        st.success(f"R$ {val_in:.2f} adicionado com sucesso!")

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Registrar Gasto")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_out")
    cat_out = st.selectbox("Tipo", st.session_state.cat_saida + ["Outra..."], key="cat_out")
    
    if cat_out == "Outra...":
        nova_s = st.text_input("Nome do novo gasto:")
        if st.button("Adicionar Categoria", key="btn_add_out"):
            st.session_state.cat_saida.append(nova_s)
            st.rerun()

    if st.button("Confirmar Saída", key="btn_save_out"):
        novo = pd.DataFrame([["Saída", val_out, cat_out]], columns=['Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
        st.warning(f"Gasto de R$ {val_out:.2f} registrado.")

# --- ABA DE GRÁFICOS (Com Cores Frias e Quentes) ---
with aba_graf:
    st.subheader("Análise de Movimentação")
    
    if not st.session_state.dados.empty:
        # Criamos o mapa de cores: Entrada = Frio (Azul), Saída = Quente (Vermelho/Laranja)
        mapa_cores = {
            "Entrada": "#1f77b4", # Azul (Frio)
            "Saída": "#e74c3c"    # Vermelho (Quente)
        }
        
        # Agrupamos por tipo para o gráfico principal
        resumo = st.session_state.dados.groupby("Tipo")["Valor"].sum().reset_index()
        
        fig = px.pie(
            resumo, 
            values='Valor', 
            names='Tipo',
            color='Tipo',
            color_discrete_map=mapa_cores,
            hole=0.4,
            title="Entradas vs Saídas"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada logo abaixo
        st.write("### Detalhes dos Lançamentos")
        st.dataframe(st.session_state.dados, use_container_width=True)
    else:
        st.info("Aguardando lançamentos para gerar o gráfico...")
