import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Inicialização de dados e categorias
if 'cat_entrada' not in st.session_state:
    st.session_state.cat_entrada = ["Salário", "Cartão Alimentação"]
if 'cat_saida' not in st.session_state:
    st.session_state.cat_saida = ["Cafezinho", "Despesa", "Parcela do Carro"]
if 'dados' not in st.session_state:
    # Adicionada a coluna 'Data' na estrutura
    st.session_state.dados = pd.DataFrame(columns=['Data', 'Tipo', 'Valor', 'Categoria'])

st.title("💰 Gestão Financeira Inteligente")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatório Mensal"])

# --- DATA ATUAL E LIMITES DO MÊS ---
hoje = datetime.now()
primeiro_dia = hoje.replace(day=1).date()
ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).date()

# --- REGISTRO DE ENTRADAS ---
with aba_in:
    st.subheader("Registrar Entrada")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_in")
    cat_in = st.selectbox("Tipo", st.session_state.cat_entrada + ["Outra..."], key="cat_in")
    
    if cat_in == "Outra...":
        nova = st.text_input("Nome da nova entrada:")
        if st.button("Adicionar Categoria", key="btn_add_in"):
            st.session_state.cat_entrada.append(nova)
            st.rerun()
            
    if st.button("Confirmar Entrada", key="btn_save_in"):
        # Captura a data automática aqui
        data_atual = hoje.date()
        novo = pd.DataFrame([[data_atual, "Entrada", val_in, cat_in]], 
                            columns=['Data', 'Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
        st.success(f"Entrada de R$ {val_in:.2f} salva em {data_atual.strftime('%d/%m/%Y')}!")

# --- REGISTRO DE SAÍDAS ---
with aba_out:
    st.subheader("Registrar Saída")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_out")
    cat_out = st.selectbox("Tipo", st.session_state.cat_saida + ["Outra..."], key="cat_out")
    
    if cat_out == "Outra...":
        nova_s = st.text_input("Nome da nova saída:")
        if st.button("Adicionar Categoria", key="btn_add_out"):
            st.session_state.cat_saida.append(nova_s)
            st.rerun()

    if st.button("Confirmar Saída", key="btn_save_out"):
        data_atual = hoje.date()
        novo = pd.DataFrame([[data_atual, "Saída", val_out, cat_out]], 
                            columns=['Data', 'Tipo', 'Valor', 'Categoria'])
        st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
        st.warning(f"Saída de R$ {val_out:.2f} registrada em {data_atual.strftime('%d/%m/%Y')}!")

# --- RELATÓRIO MENSAL ---
with aba_graf:
    st.subheader(f"📅 Relatório: {hoje.strftime('%B / %Y')}")
    st.info(f"Período: {primeiro_dia.strftime('%d/%m/%Y')} até {ultimo_dia.strftime('%d/%m/%Y')}")

    if not st.session_state.dados.empty:
        # Converter coluna Data para o formato correto caso necessário
        df = st.session_state.dados.copy()
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        
        # Filtrar apenas dados do mês atual
        df_mes = df[(df['Data'] >= primeiro_dia) & (df['Data'] <= ultimo_dia)]

        if not df_mes.empty:
            col1, col2 = st.columns([3, 2])

            with col1:
                st.write("**Gastos e Entradas Detalhados**")
                cores_frias = ['#0000FF', '#008000', '#00CED1', '#4682B4']
                cores_quentes = ['#FF0000', '#FF4500', '#DC143C', '#FF69B4']
                
                color_map = {}
                for i, cat in enumerate(st.session_state.cat_entrada):
                    color_map[cat] = cores_frias[i % len(cores_frias)]
                for i, cat in enumerate(st.session_state.cat_saida):
                    color_map[cat] = cores_quentes[i % len(cores_quentes)]
                
                fig_bar = px.bar(
                    df_mes, x='Categoria', y='Valor', color='Categoria',
                    color_discrete_map=color_map, text_auto='.2f'
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.write("**Balanço Geral do Mês**")
                resumo = df_mes.groupby("Tipo")["Valor"].sum().reset_index()
                fig_global = px.pie(
                    resumo, values='Valor', names='Tipo',
                    color='Tipo', color_discrete_map={"Entrada": "blue", "Saída": "red"},
                    hole=0.4
                )
                fig_global.update_traces(textinfo='label+percent')
                st.plotly_chart(fig_global, use_container_width=True)
            
            st.divider()
            st.write("### 📝 Histórico de Lançamentos do Mês")
            st.dataframe(df_mes.sort_values(by='Data', ascending=False), use_container_width=True)
        else:
            st.warning("Nenhum lançamento encontrado para o mês atual.")
    else:
        st.info("Lance algum valor para ativar o relatório.")
