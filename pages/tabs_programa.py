import pandas as pd
import streamlit as st

# DEFINIMOS KPI AQUÍ PARA EVITAR EL CIRCULAR IMPORT
def kpi_local(label, value, sub=""):
    st.markdown(
        f"""
        <div class="card">
          <div class="klabel">{label}</div>
          <div class="kvalue">{value}</div>
          <div class="ksub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_programa_tab(df: pd.DataFrame, kpi_data: dict):

    # =========================================================
    # CSS
    # =========================================================
    st.markdown(
        """
        <style>
        .btn-toggle-filters div[data-testid="stButton"] > button{
            background: linear-gradient(135deg,#3b82f6,#2563eb) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            border-radius: 14px !important;
            padding: 0.55rem 1.1rem !important;
            border: none !important;
            box-shadow: 0 6px 16px rgba(37,99,235,.45) !important;
        }
        .btn-toggle-filters div[data-testid="stButton"] > button *{ color: #ffffff !important; }
        
        .btn-reset div[data-testid="stButton"] > button{
            background: linear-gradient(135deg,#facc15,#eab308) !important;
            color: #1f2937 !important;
            font-weight: 800 !important;
            border-radius: 14px !important;
            border: none !important;
            box-shadow: 0 6px 16px rgba(234,179,8,.45) !important;
        }
        .btn-reset div[data-testid="stButton"] > button *{ color: #1f2937 !important; }

        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stMultiSelect"] div[role="combobox"]{
            background: rgba(255,255,255,0.96) !important;
            color: #111827 !important;
            border-radius: 12px !important;
        }
        div[data-testid="stTabs"] button { color: rgba(232, 238, 252, 0.9) !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # RENDER DE KPIs (Usando los datos recibidos)
    # =========================================================
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_local("Items/Filas en proceso", kpi_data["n_inp"], "Filas status: IN PROCESS")
    with c2: kpi_local("Items/Filas en stand by", kpi_data["n_stb"], "Filas status: STAND BY")
    with c3: kpi_local("Items/Filas sin iniciar", kpi_data["n_uns"], "Filas status: UNSTARTED")
    with c4: kpi_local("Atrasados", kpi_data["n_atr"], "Entrega vencida con avance < 100%")
    with c5: kpi_local("Sin confirmar", kpi_data["n_sin"], "Fecha vacía o 'X CONFIRMAR'")

    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    

    if "show_filters_programa" not in st.session_state:
        st.session_state.show_filters_programa = False

    label = "🔽 Ocultar filtros" if st.session_state.show_filters_programa else "🔎 Mostrar filtros"

    st.markdown('<div class="btn-toggle-filters">', unsafe_allow_html=True)
    if st.button(label, key="toggle_filters_programa", type="primary"):
        st.session_state.show_filters_programa = not st.session_state.show_filters_programa
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Columnas y Normalización ---
    cols = ["STATUS", "START DATE", "DOC TYPE", "####", "OIT No.", "CLIENT", "ITEM", "NOMBRE", "CANTIDAD", "CANTIDAD TERMINADA", "AVANCE", "FECHA DE ENTREGA", "SEMAFORO"]
    df = df[cols].copy()
    df["START DATE"] = pd.to_datetime(df["START DATE"], errors="coerce").dt.date.fillna(df["START DATE"])
    df["ITEM"] = pd.to_numeric(df["ITEM"], errors="coerce").astype("Int64")
    df["AVANCE"] = pd.to_numeric(df["AVANCE"], errors="coerce").fillna(0) * 100

    # --- Filtros ---
    status_opts = sorted(df["STATUS"].dropna().unique())
    doc_opts = sorted(df["DOC TYPE"].dropna().unique())
    client_opts = sorted(df["CLIENT"].dropna().unique())
    sem_opts = ["🔴 ATRASADO", "🟡 PRÓXIMO", "🟢 OK", "⚪ SIN CONFIRMAR"]

    st.session_state.setdefault("f_status", ["IN PROCESS", "UNSTARTED"])
    st.session_state.setdefault("f_doc", doc_opts)
    st.session_state.setdefault("f_client", "TODOS")
    st.session_state.setdefault("f_sem", sem_opts)
    st.session_state.setdefault("f_oit", "")

    if st.session_state.show_filters_programa:
        with st.container(border=True):
            st.markdown("#### Filtros")
            ca, cb, cc = st.columns([1.4, 1.2, 1.4])
            cd, ce = st.columns([1.4, 1.6])
            with ca: st.session_state.f_status = st.multiselect("STATUS", status_opts, st.session_state.f_status)
            with cb: st.session_state.f_doc = st.multiselect("DOC TYPE", doc_opts, st.session_state.f_doc)
            with cc: st.session_state.f_client = st.selectbox("CLIENT", ["TODOS"] + client_opts)
            with cd: st.session_state.f_oit = st.text_input("OIT No. (ej: 9423,9471)")
            with ce: st.session_state.f_sem = st.multiselect("SEMAFORO", sem_opts, st.session_state.f_sem)

            st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
            if st.button("♻️ Reset filtros", type="primary"):
                for k in ["f_status", "f_doc", "f_client", "f_sem", "f_oit"]:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Aplicar y Mostrar ---
    filtered = df.copy()
    filtered = filtered[filtered["STATUS"].isin(st.session_state.f_status)]
    filtered = filtered[filtered["DOC TYPE"].isin(st.session_state.f_doc)]
    if st.session_state.f_client != "TODOS": filtered = filtered[filtered["CLIENT"] == st.session_state.f_client]
    if st.session_state.f_oit:
        terms = [t.strip() for t in st.session_state.f_oit.split(",")]
        filtered = filtered[filtered["OIT No."].astype(str).str.contains("|".join(terms), na=False)]
    filtered = filtered[filtered["SEMAFORO"].isin(st.session_state.f_sem)]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={"AVANCE": st.column_config.ProgressColumn("% AVANCE", min_value=0, max_value=100, format="%.0f%%")}
    )

    st.download_button("⬇️ Descargar CSV", filtered.to_csv(index=False).encode("utf-8"), "programa_filtrado.csv", "text/csv")