import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# Configuração da página para aproveitar bem o espaço do celular
st.set_page_config(page_title="Gestão Financeira Rocha", layout="wide")

# Link da sua planilha (Já configurado com o link que você mandou)
url = "https://docs.google.com/spreadsheets/d/1RA2_tIBjRvT6Dhou3Rc1rJvVF40yJuy1/edit?usp=sharing"

# Criando a conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO PARA CARREGAR DADOS ---
def carregar_dados():
    # Lê os lançamentos e as categorias cadastradas
    df_l = conn.read(spreadsheet=url, worksheet="Lancamentos", ttl="0s")
    df_c = conn.read(spreadsheet=url, worksheet="Categorias", ttl="0s")
    df_l['Data'] = pd.to_datetime(df_l['Data'])
    return df_l, df_c

df_lancamentos, df_categorias = carregar_dados()

st.title("💰 Gestão Rocha")

# Navegação por abas (Funciona como os hiperlinks que você pediu)
aba_in, aba_out, aba_graf = st.tabs(["📈 Entradas", "📉 Saídas", "📊 Relatórios"])

# --- ABA DE ENTRADAS ---
with aba_in:
    st.subheader("Registrar Valor Recebido")
    val_in = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="in_val")
    
    # Filtra categorias que são do tipo Entrada
    lista_cat_in = df_categorias[df_categorias['Tipo'] == 'Entrada']['Categoria'].tolist()
    cat_in = st.selectbox("Selecione a Entrada", lista_cat_in + ["Outra..."], key="in_cat")
    
    if cat_in == "Outra...":
        nova_cat_in = st.text_input("Digite o nome da nova categoria de entrada:")
        if st.button("Cadastrar Nova Categoria", key="btn_new_in"):
            if nova_cat_in:
                nova_linha_cat = pd.DataFrame([["Entrada", nova_cat_in]], columns=['Tipo', 'Categoria'])
                df_cat_atualizada = pd.concat([df_categorias, nova_linha_cat], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categorias", data=df_cat_atualizada)
                st.success("Categoria adicionada!")
                st.rerun()

    if st.button("Confirmar Entrada", key="btn_save_in"):
        if val_in > 0:
            hoje = datetime.now().date()
            nova_entrada = pd.DataFrame([[hoje, "Entrada", val_in, cat_in]], columns=['Data', 'Tipo', 'Valor', 'Categoria'])
            df_final = pd.concat([df_lancamentos, nova_entrada], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Lancamentos", data=df_final)
            st.success("Entrada salva com sucesso!")
            st.rerun()

# --- ABA DE SAÍDAS ---
with aba_out:
    st.subheader("Registrar Gasto")
    val_out = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="out_val")
    
    # Filtra categorias que são do tipo Saída
    lista_cat_out = df_categorias[df_categorias['Tipo'] == 'Saída']['Categoria'].tolist()
    cat_out = st.selectbox("Selecione o tipo de Gasto", lista_cat_out + ["Outra..."], key="out_cat")
    
    if cat_out == "Outra...":
        nova_cat_out = st.text_input("Digite o nome da nova categoria de saída:")
        if st.button("Cadastrar Novo Tipo de Gasto", key="btn_new_out"):
            if nova_cat_out:
                nova_linha_cat = pd.DataFrame([["Saída", nova_cat_out]], columns=['Tipo', 'Categoria'])
                df_cat_atualizada = pd.concat([df_categorias, nova_linha_cat], ignore_index=True)
                conn.update(spreadsheet=url, worksheet="Categorias", data=df_cat_atualizada)
                st.success("Novo gasto cadastrado!")
                st.rerun()

    if st.button("Confirmar Saída", key="btn_save_out"):
        if val_out > 0:
            hoje = datetime.now().date()
            nova_saida = pd.DataFrame([[hoje, "Saída", val_out, cat_out]], columns=['Data', 'Tipo', 'Valor', 'Categoria'])
            df_final = pd.concat([df_lancamentos, nova_saida], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Lancamentos", data=df_final)
            st.warning("Saída registrada na planilha!")
            st.rerun()

# --- ABA DE RELATÓRIOS ---
with aba_graf:
    hoje = datetime.now()
    st.subheader(f"📊 Resumo de {hoje.strftime('%B / %Y')}")
    
    # Lógica para pegar o período do mês atual automaticamente
    primeiro_dia = hoje.replace(day=1).date()
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).date()
    
    if not df_lancamentos.empty:
        # Filtrando dados do mês
        df_mes = df_lancamentos[(df_lancamentos['Data'].dt.date >= primeiro_dia) & 
                                (df_lancamentos['Data'].dt.date <= ultimo_dia)]
        
        if not df_mes.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Gastos por Categoria**")
                # Cores frias para entradas e quentes para saídas
                fig_bar = px.bar(df_mes, x='Categoria', y='Valor', color='Tipo',
                                 color_discrete_map={"Entrada": "#1f77b4", "Saída": "#e74c3c"},
                                 text_auto='.2f')
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.write("**Balanço Global (Entrada vs Saída)**")
                resumo = df_mes.groupby("Tipo")["Valor"].sum().reset_index()
                fig_pie = px.pie(resumo, values='Valor', names='Tipo', hole=0.4,
                                 color='Tipo', color_discrete_map={"Entrada": "blue", "Saída": "red"})
                fig_pie.update_traces(textinfo='label+percent')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.divider()
            st.write("### Histórico de Lançamentos")
            st.dataframe(df_mes.sort_values(by='Data', ascending=False), use_container_width=True)
        else:
            st.info("Nenhum lançamento registrado neste mês.")
    else:
        st.info("O banco de dados está vazio.")
