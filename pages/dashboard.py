import re
import unicodedata
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

from pages.tabs_programa import render_programa_tab
from pages.tabs_despachos import render_despachos_tab
from pages.tabs_programacion import render_programacion_tab

# ---------------------------
# UI + Dark theme (Versión Ultra-Compacta)
# ---------------------------
st.set_page_config(
    page_title="Dashboard | Producción",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      /* 1. ELIMINAR ESPACIO SUPERIOR ABSOLUTO */
      div[data-testid="stAppViewContainer"] main .block-container { 
        padding-top: 0rem !important; 
        margin-top: -45px !important; /* Sube todo al límite superior */
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
      }
      
      header[data-testid="stHeader"] {
        display: none !important;
      }

      .stApp {
        background:
          radial-gradient(1100px 500px at 15% 10%, rgba(0,255,255,0.12), transparent),
          radial-gradient(1100px 500px at 85% 20%, rgba(160,70,255,0.12), transparent),
          #0b1220;
        color: #e8eefc;
      }

      /* 2. HEADER ALINEADO (LOGO + TEXTO) */
      .header-container {
        display: flex;
        align-items: center;
        gap: 15px; 
        margin-bottom: 5px;
      }

      .title {
        font-size: 2rem;
        font-weight: 800; 
        line-height: 1;
        margin: 0px !important;
      }
      .sub {
        opacity: 0.75; 
        font-size: 0.9rem;
        margin: 0px !important;
      }

      /* 3. SEPARACIÓN ESTÉTICA DE LAS CARDS (KPIs) */
      div[data-testid="column"] {
        padding: 0px 8px !important; 
      }

      .card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 12px 15px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        margin-bottom: 5px;
      }
      
      .klabel {opacity: 0.75; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;}
      .kvalue {font-size: 1.6rem; font-weight: 800; margin-top: 2px; line-height: 1;}
      .ksub {opacity: 0.65; font-size: 0.7rem; margin-top: 4px;}

      /* 4. TABS COMPACTAS */
      div[data-testid="stTabs"] {
        margin-top: -10px !important;
      }
      
      /* ESTILOS DE FORMULARIOS */
      label, label span, label p, .stCaption, .stMarkdown, .stCheckbox, .stRadio,
      .stSelectbox, .stMultiSelect {
        color: rgba(232,238,252,0.92) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Helpers
# ---------------------------
def norm(txt: str) -> str:
    if txt is None: return ""
    txt = str(txt).strip().upper()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join([c for c in txt if not unicodedata.combining(c)])
    txt = re.sub(r"\s+", " ", txt)
    return txt

def find_sheet(xls: pd.ExcelFile, keyword: str):
    k = keyword.lower()
    for name in xls.sheet_names:
        if k in name.strip().lower(): return name
    return None

def find_col(df: pd.DataFrame, keys):
    cols = list(df.columns)
    cols_n = [norm(c) for c in cols]
    for key in keys:
        k = norm(key)
        for original, cn in zip(cols, cols_n):
            if k in cn: return original
    return None

def to_date_series(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

def kpi(label, value, sub=""):
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

def semaforo_item(entrega_dt: pd.Timestamp, avance_item: float) -> str:
    if pd.isna(entrega_dt): return "⚪ SIN CONFIRMAR"
    if avance_item >= 1.0: return "🟢 OK"
    today = pd.Timestamp(date.today())
    if entrega_dt < today: return "🔴 ATRASADO"
    if (entrega_dt - today).days <= 7: return "🟡 PRÓXIMO"
    return "🟢 OK"

# ---------------------------
# Load excel
# ---------------------------
if "excel_file" not in st.session_state or st.session_state["excel_file"] is None:
    st.warning("No hay excel cargado. Ve a **📥 Cargar excel** y súbelo.")
    st.stop()

uploaded = st.session_state["excel_file"]
xls = pd.ExcelFile(uploaded)

sheet_prog = find_sheet(xls, "programa") or find_sheet(xls, "trabajo")
sheet_desp = find_sheet(xls, "despach")
if sheet_prog is None or sheet_desp is None:
    st.error("No pude detectar las pestañas requeridas.")
    st.stop()

programa = pd.read_excel(xls, sheet_name=sheet_prog)
despachos = pd.read_excel(xls, sheet_name=sheet_desp)

programa.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in programa.columns]
despachos.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in despachos.columns]

# --- Column mapping ---
c_status = find_col(programa, ["STATUS"])
c_start = find_col(programa, ["START DATE", "START"])
c_doc_type = find_col(programa, ["DOC TYPE", "DOC"])
c_hash = find_col(programa, ["####", "##"])
c_oit = find_col(programa, ["OIT NO", "OIT"])
c_cliente = find_col(programa, ["CLIENTE", "CLIENT"])
c_item = find_col(programa, ["ITEM"])
c_nombre = find_col(programa, ["NOMBRE"])
c_cant = find_col(programa, ["CANT."])
c_term = find_col(programa, ["CANT. TERMINADAS", "TERMINADAS"])
c_entrega = find_col(programa, ["FECHA DE ENTREGA", "ENTREGA"])

# --- Build DF ---
df = programa.copy()
df["STATUS"] = df[c_status].astype(str).map(norm)
df["START DATE"] = df[c_start].astype(str).fillna("").str.strip()
df["DOC TYPE"] = df[c_doc_type].astype(str).map(norm)
df["##"] = df[c_hash].astype(str).str.strip()
df["OIT No."] = df[c_oit].astype(str).str.strip()
df["CLIENT"] = df[c_cliente].astype(str).str.strip()
df["ITEM"] = df[c_item].astype(str).str.strip()
df["NOMBRE"] = df[c_nombre].astype(str).str.strip()
df["CANTIDAD"] = pd.to_numeric(df[c_cant], errors="coerce").fillna(0.0)
df["CANTIDAD TERMINADA"] = pd.to_numeric(df[c_term], errors="coerce").fillna(0.0)
df["entrega_raw"] = df[c_entrega].astype(str).fillna("").str.strip()
df["entrega_dt"] = to_date_series(df[c_entrega])
df["AVANCE"] = np.where(df["CANTIDAD"] > 0, df["CANTIDAD TERMINADA"] / df["CANTIDAD"], 0.0)
df["AVANCE"] = np.clip(df["AVANCE"], 0, 1)
df["FECHA DE ENTREGA"] = np.where(df["entrega_dt"].notna(), df["entrega_dt"].dt.strftime("%d/%m/%Y"), df["entrega_raw"])
df["SEMAFORO"] = [semaforo_item(dt, av) for dt, av in zip(df["entrega_dt"], df["AVANCE"])]

today_ts = pd.Timestamp(date.today())
df["atrasado_item"] = (df["entrega_dt"].notna()) & (df["entrega_dt"] < today_ts) & (df["AVANCE"] < 1.0)
raw_up = df["entrega_raw"].astype(str).str.upper()
df["sin_confirmar_item"] = df["entrega_dt"].isna() | raw_up.str.contains("CONFIRM", na=False)

# ---------------------------
# Header (Optimizado con Flexbox)
# ---------------------------
# Usamos columnas nativas pero muy ajustadas para el logo
h_col1, h_col2 = st.columns([0.06, 0.94])
with h_col1:
    st.image("logo.png", width=60)
with h_col2:
    st.markdown(
        """
        <div style='margin-top: 5px;'>
            <div class="title">Planeación - Planta de producción</div>
            <div class="sub">Dashboard para la planeación y seguimiento de actividades de manufactura</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ---------------------------
# Tabs
# ---------------------------
t1, t2, t3 = st.tabs(["📋 Programa de trabajo", "🚚 Despachos", "🗓️ Programación de planta"])

with t1:
    kpi_data = {
        "n_inp": int((df["STATUS"] == "IN PROCESS").sum()),
        "n_stb": int((df["STATUS"] == "STAND BY").sum()),
        "n_uns": int((df["STATUS"] == "UNSTARTED").sum()),
        "n_atr": int(df["atrasado_item"].sum()),
        "n_sin": int(df["sin_confirmar_item"].sum())
    }
    render_programa_tab(df, kpi_data)

with t2:
    render_despachos_tab(despachos)

with t3:
    render_programacion_tab()