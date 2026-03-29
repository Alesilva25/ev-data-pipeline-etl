import streamlit as st

st.set_page_config(layout="wide")

# =========================
# CSS CUSTOM (PROFISSIONAL)
# =========================
st.markdown("""
<style>

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #8e2de2, #c039f9);
    color: white;
    height: 100vh;
}

.sidebar-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 20px;
}

/* ===== HEADER ===== */
.header {
    text-align: right;
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 10px;
}

/* ===== UPLOAD BOX ===== */
.upload-box {
    border: 2px dashed #3b82f6;
    border-radius: 10px;
    padding: 25px;
    text-align: center;
    color: #3b82f6;
    margin-bottom: 10px;
    font-weight: 500;
}

/* ===== BOTÕES ===== */
button[kind="primary"] {
    background-color: #1f77b4;
    border-radius: 6px;
    color: white;
}

button:hover {
    opacity: 0.9;
}

/* ===== BOTÃO VERDE ===== */
.btn-green {
    background-color: #2ecc71;
    color: white;
    padding: 10px;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
    margin-top: 10px;
}

/* ===== AJUSTES DE LAYOUT ===== */
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}

/* Remove scroll horizontal */
html, body {
    overflow-x: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown('<div class="sidebar-title">GSBA</div>', unsafe_allow_html=True)
st.sidebar.markdown("**CONTROLE DE ERBS**")
st.sidebar.markdown("**ACOMPANHAMENTO OLT**")

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["Carregar Dados", "Dashboard"])

# =========================
# TAB 1
# =========================
with tab1:

    col1, col2 = st.columns(2)

    # -------- ESQUERDA --------
    with col1:
        st.subheader("Importar Bases")
        st.caption("Bases aceitas: Fibrados, Report, Netcompass, HTL5")

        st.markdown('<div class="upload-box">Clique ou arraste arquivos aqui</div>', unsafe_allow_html=True)

        fibrados = st.file_uploader("Bases Fibrados")
        report = st.file_uploader("Bases Report")
        netcompass = st.file_uploader("Bases Netcompass")
        htl5 = st.file_uploader("Bases HTL5")

        # Mostrar nomes dos arquivos
        if fibrados:
            st.success(f"✔ {fibrados.name}")
        if report:
            st.success(f"✔ {report.name}")
        if netcompass:
            st.success(f"✔ {netcompass.name}")
        if htl5:
            st.success(f"✔ {htl5.name}")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            cancelar = st.button("Cancelar")
        with col_btn2:
            continuar = st.button("Continuar")

        st.markdown("⬇️ Baixar arquivo de validação")

    # -------- DIREITA --------
    with col2:
        st.subheader("Importar base validada")

        st.markdown('<div class="upload-box">Clique ou arraste arquivos aqui</div>', unsafe_allow_html=True)

        validada = st.file_uploader("Base Validada")

        if validada:
            st.success(f"✔ {validada.name}")

        col_btn3, col_btn4 = st.columns(2)
        with col_btn3:
            cancelar_validado = st.button("Cancelar ")
        with col_btn4:
            continuar_validado = st.button("Continuar ")

        st.markdown('<div class="btn-green">BAIXAR SIGTIM</div>', unsafe_allow_html=True)
        st.caption("Base mais recente 15/02/2026")

# =========================
# TAB 2
# =========================
with tab2:
    st.subheader("Dashboard")

    st.info("Em construção...")

    st.write("Aqui você pode adicionar:")
    st.write("- 📊 Gráficos")
    st.write("- 📈 KPIs")
    st.write("- 📋 Tabelas")

# =========================
# PROCESSAMENTO FUTURO
# =========================
if 'continuar' in locals() and continuar:
    st.success("Arquivos enviados com sucesso!")

    # Aqui entra seu código pandas depois
    # exemplo:
    # df = pd.read_excel(fibrados)
    # df = tratar_sisLic(df)

    st.info("Aqui você vai integrar seu pipeline de dados (pandas)")