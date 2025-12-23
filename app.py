import streamlit as st
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    PASSWORD = os.getenv("APP_PASSWORD")

    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("### 🔒 Acceso interno")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if pwd == PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        return  # detiene solo la función, no todo el script

    st.set_page_config(page_title="Cargar Excel | Producción", layout="wide", initial_sidebar_state="collapsed")

    st.markdown(
        """
        <style>
          .stApp {
            background:
              radial-gradient(1100px 500px at 15% 10%, rgba(0,255,255,0.12), transparent),
              radial-gradient(1100px 500px at 85% 20%, rgba(160,70,255,0.12), transparent),
              #0b1220;
            color: #e8eefc;
          }
          header, footer {visibility: hidden;}
          #MainMenu {visibility: hidden;}
          .title {font-size: 2.0rem; font-weight: 800; margin-bottom: 0.2rem;}
          .sub {opacity: 0.75; margin-bottom: 1rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="title">📥 Cargar Excel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub">Sube el excel (2 pestañas: programa de trabajo y despachos). Al cargar, te llevará al Dashboard automáticamente.</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("📄 Sube el Excel", type=["xlsx"])

    if uploaded:
        st.session_state["excel_file"] = uploaded
        st.success("Excel cargado. Redirigiendo al Dashboard…")
        st.switch_page("pages/1_Dashboard.py")
    else:
        st.info("Sube el archivo para habilitar el dashboard.")

if __name__ == "__main__":
    main()