import pandas as pd
import streamlit as st
from datetime import date


def render_despachos_tab(despachos: pd.DataFrame):

    st.markdown("### 🚚 Despachos")

    if despachos is None or despachos.empty:
        st.info("No hay información de despachos para mostrar.")
        return

    df = despachos.copy()
    df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]

    # -------------------------------------------------
    # FECHA (columna C)
    # -------------------------------------------------
    fecha_col = df.columns[2]

    df[fecha_col] = pd.to_datetime(
        df[fecha_col], errors="coerce"
    ).dt.date

    # -------------------------------------------------
    # Días restantes
    # -------------------------------------------------
    today = date.today()

    df["_dias"] = df[fecha_col].apply(
        lambda x: (x - today).days if pd.notna(x) else None
    )

    # -------------------------------------------------
    # Semáforo
    # -------------------------------------------------
    def semaforo(d):
        if d is None:
            return "⚪ SIN FECHA"
        if d <= 5:
            return "🔴 ROJO"
        if d <= 10:
            return "🟡 AMARILLO"
        return "🟢 VERDE"

    df["SEMAFORO"] = df["_dias"].apply(semaforo)

    # -------------------------------------------------
    # Estilo REAL (background tenue)
    # -------------------------------------------------
    def highlight_row(row):
        s = row["SEMAFORO"]

        if "ROJO" in s:
            return ["background-color: rgba(239,68,68,0.12)"] * len(row)
        if "AMARILLO" in s:
            return ["background-color: rgba(234,179,8,0.12)"] * len(row)
        if "VERDE" in s:
            return ["background-color: rgba(34,197,94,0.12)"] * len(row)

        return [""] * len(row)

    styled_df = (
        df.drop(columns=["_dias"])
        .style
        .apply(highlight_row, axis=1)
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
    )
