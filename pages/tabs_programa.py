import pandas as pd
import streamlit as st


def render_programa_tab(df: pd.DataFrame):

    # =========================================================
    # CSS — Botones con prioridad REAL (no blancos)
    # =========================================================
    st.markdown(
        """
        <style>
        /* ===== BOTÓN MOSTRAR / OCULTAR (AZUL) ===== */
        .btn-toggle-filters div[data-testid="stButton"] > button{
            background: linear-gradient(135deg,#3b82f6,#2563eb) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            border-radius: 14px !important;
            padding: 0.55rem 1.1rem !important;
            border: none !important;
            box-shadow: 0 6px 16px rgba(37,99,235,.45) !important;
            opacity: 1 !important;
        }

        .btn-toggle-filters div[data-testid="stButton"] > button *{
            color: #ffffff !important;
        }

        .btn-toggle-filters div[data-testid="stButton"] > button:hover{
            filter: brightness(1.1);
        }

        /* ===== BOTÓN RESET (AMARILLO) ===== */
        .btn-reset div[data-testid="stButton"] > button{
            background: linear-gradient(135deg,#facc15,#eab308) !important;
            color: #1f2937 !important;
            font-weight: 800 !important;
            border-radius: 14px !important;
            border: none !important;
            box-shadow: 0 6px 16px rgba(234,179,8,.45) !important;
            opacity: 1 !important;
        }

        .btn-reset div[data-testid="stButton"] > button *{
            color: #1f2937 !important;
        }

        .btn-reset div[data-testid="stButton"] > button:hover{
            filter: brightness(1.05);
        }

        /* ===== INPUTS CLAROS EN DARK MODE (NO TOCADO) ===== */
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stMultiSelect"] div[role="combobox"]{
            background: rgba(255,255,255,0.96) !important;
            color: #111827 !important;
            border-radius: 12px !important;
        }

        /* ===== Tabs: solo mejorar visibilidad del texto ===== */
        div[data-testid="stTabs"] button {
            color: rgba(232, 238, 252, 0.9) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # Header
    # =========================================================
    st.markdown("### 📋 Programa de trabajo")

    if "show_filters_programa" not in st.session_state:
        st.session_state.show_filters_programa = False

    label = "🔽 Ocultar filtros" if st.session_state.show_filters_programa else "🔎 Mostrar filtros"

    st.markdown('<div class="btn-toggle-filters">', unsafe_allow_html=True)
    if st.button(label, key="toggle_filters_programa", type="primary"):
        st.session_state.show_filters_programa = not st.session_state.show_filters_programa
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================
    # Columnas requeridas
    # =========================================================
    cols = [
        "STATUS", "START DATE", "DOC TYPE", "####", "OIT No.", "CLIENT",
        "ITEM", "NOMBRE", "CANTIDAD", "CANTIDAD TERMINADA",
        "AVANCE", "FECHA DE ENTREGA", "SEMAFORO"
    ]
    df = df[cols].copy()
    # =========================================================
    # NORMALIZACIÓN DE DATOS (sin tocar FECHA DE ENTREGA)
    # =========================================================

    # START DATE: fecha sin hora o "SIN INICIAR"
    df["START DATE"] = pd.to_datetime(
        df["START DATE"], errors="coerce"
    ).dt.date.fillna(df["START DATE"])

    # ITEM: 1.0 -> 1
    df["ITEM"] = (
        pd.to_numeric(df["ITEM"], errors="coerce")
        .astype("Int64")
    )

    # AVANCE: 0–1 -> 0–100 para visualización correcta
    df["AVANCE"] = (
        pd.to_numeric(df["AVANCE"], errors="coerce")
        .fillna(0) * 100
    )
    # =========================================================
    # Opciones filtros
    # =========================================================
    status_opts = sorted(df["STATUS"].dropna().unique())
    doc_opts = sorted(df["DOC TYPE"].dropna().unique())
    client_opts = sorted(df["CLIENT"].dropna().unique())
    sem_opts = ["🔴 ATRASADO", "🟡 PRÓXIMO", "🟢 OK", "⚪ SIN CONFIRMAR"]

    st.session_state.setdefault("f_status", ["IN PROCESS", "UNSTARTED"])
    st.session_state.setdefault("f_doc", doc_opts)
    st.session_state.setdefault("f_client", "TODOS")
    st.session_state.setdefault("f_sem", sem_opts)
    st.session_state.setdefault("f_oit", "")

    # =========================================================
    # FILTROS
    # =========================================================
    if st.session_state.show_filters_programa:
        with st.container(border=True):
            st.markdown("#### Filtros (solo afectan *Programa de trabajo*)")

            c1, c2, c3 = st.columns([1.4, 1.2, 1.4])
            c4, c5 = st.columns([1.4, 1.6])

            with c1:
                st.session_state.f_status = st.multiselect("STATUS", status_opts, st.session_state.f_status)

            with c2:
                st.session_state.f_doc = st.multiselect("DOC TYPE", doc_opts, st.session_state.f_doc)

            with c3:
                st.session_state.f_client = st.selectbox("CLIENT", ["TODOS"] + client_opts)

            with c4:
                st.session_state.f_oit = st.text_input("OIT No. (ej: 9423,9471)")

            with c5:
                st.session_state.f_sem = st.multiselect("SEMAFORO", sem_opts, st.session_state.f_sem)

            st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
            if st.button("♻️ Reset filtros", type="primary"):
                for k in list(st.session_state.keys()):
                    if k.startswith("f_"):
                        del st.session_state[k]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================
    # APLICAR FILTROS
    # =========================================================
    filtered = df.copy()

    filtered = filtered[filtered["STATUS"].isin(st.session_state.f_status)]
    filtered = filtered[filtered["DOC TYPE"].isin(st.session_state.f_doc)]

    if st.session_state.f_client != "TODOS":
        filtered = filtered[filtered["CLIENT"] == st.session_state.f_client]

    if st.session_state.f_oit:
        terms = [t.strip() for t in st.session_state.f_oit.split(",")]
        filtered = filtered[
            filtered["OIT No."].astype(str).str.contains("|".join(terms), na=False)
        ]

    filtered = filtered[filtered["SEMAFORO"].isin(st.session_state.f_sem)]

    # =========================================================
    # TABLA
    # =========================================================
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "AVANCE": st.column_config.ProgressColumn(
                "% AVANCE",
                min_value=0,
                max_value=100,
                format="%.0f%%"
            )
        }
    )

    st.download_button(
        "⬇️ Descargar tabla filtrada (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        "programa_trabajo_filtrado.csv",
        "text/csv",
    )