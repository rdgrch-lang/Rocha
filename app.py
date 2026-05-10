import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Conexão com o Google Sheets
# O URL abaixo é o que você me passou
url = "https://docs.google.com/spreadsheets/d/1RA2_tIBjRvT6Dhou3Rc1rJvVF40yJuy1/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO PARA LER DADOS ---
def carregar_dados():
    df_lanc = conn.read(spreadsheet=url, worksheet="Lancamentos")
    df_cat = conn.read(spreadsheet=url, worksheet="Categorias")
    # Garantir que a coluna Data seja do tipo datetime
    df_lanc['Data'] = pd.to_datetime(df_lanc['Data'])
    return df_lanc, df_cat

df_lancamentos, df_categorias = carregar_dados()

st.title("💰 Gestão Financeira Rocha (Nuvem)")

aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatório Mensal"])

# --- REGISTRO DE ENTRADAS ---
with aba_in:
    st.subheader("Registrar Entrada")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_in")
    
    cats_in = df_categorias[df_categorias['Tipo'] == 'Entrada']['Categoria'].tolist()
    cat_in = st.selectbox("Tipo", cats_in + ["Outra..."], key="cat_in")
    
    if cat_in == "Outra...":
        nova = st.text_input("Nome da nova entrada:")
        if st.button("Adicionar Categoria"):
            nova_cat = pd.DataFrame([["Entrada", nova]], columns=['Tipo', 'Categoria'])
            df_cat_updated = pd.concat([df_categorias, nova_cat])
            conn.update(spreadsheet=url, worksheet="Categorias", data=df_cat_updated)
            st.success("Categoria adicionada! O app vai reiniciar.")
            st.rerun()
            
    if st.button("Confirmar Entrada"):
        nova_linha = pd.DataFrame([[datetime.now().date(), "Entrada", val_in, cat_in]], 
                                  columns=['Data', 'Tipo', 'Valor', 'Categoria'])
        df_final = pd.concat([df_lancamentos, nova_linha])
        conn.update(spreadsheet=url, worksheet="Lancamentos", data=df_final)
        st.success("Salvo no Google Sheets!")
        st.rerun()

# --- REGISTRO DE SAÍDAS ---
with aba_out:
    st.subheader("Registrar Saída")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_out")
    
    cats_out = df_categorias[df_categorias['Tipo'] == 'Saída']['Categoria'].tolist()
    cat_out = st.selectbox("Tipo", cats_out + ["Outra..."], key="cat_out")
    
    if cat_out == "Outra...":
        nova_s = st.text_input("Nome da nova saída:")
        if st.button("Adicionar Categoria", key="btn_out"):
            nova_cat_s = pd.DataFrame([["Saída", nova_s]], columns=['Tipo', 'Categoria'])
            df_cat_updated = pd.concat([df_categorias, nova_cat_s])
            conn.update(spreadsheet=url, worksheet="Categorias", data=df_cat_updated)
            st.rerun()

    if st.button("Confirmar Saída"):
        nova_linha = pd.DataFrame([[datetime.now().date(), "Saída", val_out, cat_out]], 
                                  columns=['Data', 'Tipo', 'Valor', 'Categoria'])
        df_final = pd.concat([df_lancamentos, nova_linha])
        conn.update(spreadsheet=url, worksheet="Lancamentos", data=df_final)
        st.warning("Gasto registrado na planilha!")
        st.rerun()

# --- RELATÓRIO MENSAL ---
with aba_graf:
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1).date()
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).date()
    
    st.subheader(f"📅 Relatório: {hoje.strftime('%B / %Y')}")

    if not df_lancamentos.empty:
        df_mes = df_lancamentos[(df_lancamentos['Data'].dt.date >= primeiro_dia) & 
                                (df_lancamentos['Data'].dt.date <= ultimo_dia)]

        if not df_mes.empty:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.write("**Gastos Detalhados (Barras)**")
                # Lógica de cores frias/quentes baseada no que você pediu
                fig_bar = px.bar(df_mes, x='Categoria', y='Valor', color='Tipo',
                                 color_discrete_map={"Entrada": "blue", "Saída": "red"}, 
                                 text_auto='.2f')
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.write("**Balanço Geral (Pizza)**")
                resumo = df_mes.groupby("Tipo")["Valor"].sum().reset_index()
                fig_pie = px.pie(resumo, values='Valor', names='Tipo', hole=0.4,
                                 color='Tipo', color_discrete_map={"Entrada": "blue", "Saída": "red"})
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.divider()
            st.write("### Histórico do Mês")
            st.dataframe(df_mes.sort_values(by='Data', ascending=False), use_container_width=True)
        else:
            st.info("Sem dados para este mês.")
