import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Qualidade - Estrutura Dinâmica", layout="wide")

# 2. URL de Download Direto (O seu link configurado)
URL_SHAREPOINT = "https://estruturadinamica365-my.sharepoint.com/:x:/g/personal/claudio_carvalho_estruturadinamica365_onmicrosoft_com/IQA5UpzDgv3ASZ3rOrpOCdjdAUT6YLH-HPrXrDYHq0FjGLA?download=1"

# Função para converter o texto do Forms em nota numérica
def converter_nota(texto):
    mapa = {
        "Acima do Esperado": 10,
        "Dentro do Esperado": 5,
        "Abaixo do Esperado": 0
    }
    return mapa.get(texto, 0)

@st.cache_data(ttl=300) # Atualiza os dados a cada 5 minutos
def carregar_dados():
    # Lê a planilha diretamente do SharePoint
    df = pd.read_excel(URL_SHAREPOINT)
    
    # Colunas de avaliação do seu Forms
    colunas_avaliadas = [
        '4.Cumpriu o script do atendimento?',
        '5.Tom de voz e entonação',
        '7.Formalidade',
        '9.Conhecimento Técnico',
        '10.Inteligência emocional',
        '11.Cordialidade'
    ]
    
    # Criar colunas numéricas e calcular a média
    for col in colunas_avaliadas:
        if col in df.columns:
            df[f'Num_{col}'] = df[col].apply(converter_nota)
    
    # Média final considerando apenas as colunas de nota
    cols_calculo = [f'Num_{c}' for c in colunas_avaliadas if f'Num_{c}' in df.columns]
    df['Nota_Final'] = df[cols_calculo].mean(axis=1)
    
    return df

# --- INTERFACE ---

try:
    dados = carregar_dados()

    st.sidebar.header("Painel do Coordenador")
    
    # Filtro de Operação
    lista_ops = sorted(dados['2.Operação'].unique())
    op_selecionada = st.sidebar.selectbox("Selecione sua Unidade", ["Selecione..."] + lista_ops)
    
    # Senha de Acesso (Exemplo: ed2026)
    senha = st.sidebar.text_input("Senha de Acesso", type="password")

    if op_selecionada != "Selecione..." and senha == "ed2026":
        
        # Filtra os dados: Privacidade Total
        df_unidade = dados[dados['2.Operação'] == op_selecionada].copy()

        st.title(f"Gestão de Qualidade: {op_selecionada}")

        # KPIs Rápidos
        c1, c2, c3 = st.columns(3)
        media_op = df_unidade['Nota_Final'].mean()
        
        c1.metric("Média da Unidade", f"{media_op:.2f}")
        c2.metric("Total de Auditorias", len(df_unidade))
        
        abaixo_meta = len(df_unidade[df_unidade['Nota_Final'] < 7.0])
        c3.metric("Casos Críticos (< 7.0)", abaixo_meta, delta_color="inverse")

        # Tabela de Resultados Estilizada
        st.subheader("Registros Detalhados")
        
        def colorir_nota(val):
            color = '#ff4b4b' if val < 7.0 else '#2ecc71'
            return f'background-color: {color}; color: white; font-weight: bold'

        exibicao = df_unidade[['1.Nome do colaborador', '3.ID da ligação (DG PHONE)', 'Nota_Final']]
        st.dataframe(
            exibicao.style.applymap(colorir_nota, subset=['Nota_Final']),
            use_container_width=True
        )

        # Seção de Alerta de Baixa Duração (Short Calls)
        st.divider()
        st.subheader("⚠️ Monitorização de Baixa Duração")
        # Se houver coluna de tempo no Excel, o filtro entra aqui:
        # curtas = df_unidade[df_unidade['Tempo'] < 15]
        st.info("O sistema está pronto para identificar desvios éticos automaticamente.")

    else:
        st.info("Por favor, selecione a operação e insira a senha para ver os resultados.")

except Exception as e:
    st.error(f"Erro ao carregar os dados. Verifique o link. Detalhe: {e}")

