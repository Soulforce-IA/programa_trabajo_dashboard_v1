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
# UI + Dark theme
# ---------------------------
st.set_page_config(
    page_title="Dashboard | Producción",
    layout="wide",
    #initial_sidebar_state="collapsed",  # <-- sidebar oculto al inicio
)

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

      /* Titles */
      .title {font-size: 2.0rem; font-weight: 800; margin-bottom: 0.2rem;}
      .sub {opacity: 0.75; margin-bottom: 1rem;}

      /* Cards */
      .card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 12px 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      }
      .klabel {opacity: 0.75; font-size: 0.85rem;}
      .kvalue {font-size: 1.6rem; font-weight: 800; margin-top: 4px; line-height: 1.1;}
      .ksub {opacity: 0.65; font-size: 0.8rem; margin-top: 2px;}

      /* ===== Make labels readable in dark mode (main + sidebar) ===== */
      label, label span, label p,
      .stCaption, .stMarkdown, .stCheckbox, .stRadio,
      .stSelectbox, .stMultiSelect {
        color: rgba(232,238,252,0.92) !important;
      }
      div[data-testid="stSidebar"] label,
      div[data-testid="stSidebar"] p,
      div[data-testid="stSidebar"] span {
        color: rgba(232,238,252,0.92) !important;
      }
      div[data-testid="stCheckbox"] label p {
        color: rgba(232,238,252,0.92) !important;
      }

      /* Inputs text on dark */
      .stTextInput input, .stDateInput input, .stNumberInput input,
      div[data-baseweb="select"] span,
      div[data-baseweb="select"] input {
        color: #e8eefc !important;
      }

      /* Dropdown popover (options list) in dark */
      div[data-baseweb="popover"] div[role="listbox"] {
        background: rgba(13,18,32,0.98) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 14px !important;
        box-shadow: 0 16px 40px rgba(0,0,0,0.45) !important;
      }
      div[data-baseweb="popover"] div[role="option"] {
        color: #e8eefc !important;
      }
      div[data-baseweb="popover"] div[role="option"]:hover {
        background: rgba(255,255,255,0.08) !important;
      }
      div[data-baseweb="popover"] div[role="option"][aria-selected="true"] {
        background: rgba(255,255,255,0.10) !important;
      }

      /* Tags */
      div[data-baseweb="tag"] {
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 999px !important;
        padding: 1px 8px !important;
        font-size: 0.85rem !important;
      }
      /* Reducir espacio superior del contenido principal */
        div[data-testid="stAppViewContainer"] main .block-container {
            padding-top: 1rem !important;
        }
     
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------
# Helpers
# ---------------------------
def norm(txt: str) -> str:
    if txt is None:
        return ""
    txt = str(txt).strip().upper()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join([c for c in txt if not unicodedata.combining(c)])
    txt = re.sub(r"\s+", " ", txt)
    return txt


def find_sheet(xls: pd.ExcelFile, keyword: str):
    k = keyword.lower()
    for name in xls.sheet_names:
        if k in name.strip().lower():
            return name
    return None


def find_col(df: pd.DataFrame, keys):
    cols = list(df.columns)
    cols_n = [norm(c) for c in cols]
    for key in keys:
        k = norm(key)
        for original, cn in zip(cols, cols_n):
            if k in cn:
                return original
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
    if pd.isna(entrega_dt):
        return "⚪ SIN CONFIRMAR"
    if avance_item >= 1.0:
        return "🟢 OK"
    today = pd.Timestamp(date.today())
    if entrega_dt < today:
        return "🔴 ATRASADO"
    if (entrega_dt - today).days <= 7:
        return "🟡 PRÓXIMO"
    return "🟢 OK"


# ---------------------------
# Load excel from session
# ---------------------------
if "excel_file" not in st.session_state or st.session_state["excel_file"] is None:
    st.warning("No hay excel cargado. Ve a **📥 Cargar excel** y súbelo.")
    st.stop()

uploaded = st.session_state["excel_file"]
xls = pd.ExcelFile(uploaded)

sheet_prog = find_sheet(xls, "programa") or find_sheet(xls, "trabajo")
sheet_desp = find_sheet(xls, "despach")
if sheet_prog is None or sheet_desp is None:
    st.error("No pude detectar las pestañas. Renómbralas incluyendo: 'programa' y 'despachos'.")
    st.stop()

programa = pd.read_excel(xls, sheet_name=sheet_prog)
despachos = pd.read_excel(xls, sheet_name=sheet_desp)

programa.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in programa.columns]
despachos.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in despachos.columns]


# ---------------------------
# Column mapping (Programa)
# ---------------------------
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

required = [c_status, c_start, c_doc_type, c_hash, c_oit, c_cliente, c_item, c_nombre, c_cant, c_term, c_entrega]
if any(x is None for x in required):
    st.error("Faltan columnas en 'programa de trabajo'.")
    st.write("Columnas encontradas:", list(programa.columns))
    st.stop()


# ---------------------------
# Build main dataframe
# ---------------------------
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

df["FECHA DE ENTREGA"] = np.where(
    df["entrega_dt"].notna(),
    df["entrega_dt"].dt.strftime("%d/%m/%Y"),
    df["entrega_raw"],
)

df["SEMAFORO"] = [semaforo_item(dt, av) for dt, av in zip(df["entrega_dt"], df["AVANCE"])]

today_ts = pd.Timestamp(date.today())
df["atrasado_item"] = (df["entrega_dt"].notna()) & (df["entrega_dt"] < today_ts) & (df["AVANCE"] < 1.0)
raw_up = df["entrega_raw"].astype(str).str.upper()
df["sin_confirmar_item"] = df["entrega_dt"].isna() | raw_up.str.contains("CONFIRM", na=False)

# ---------------------------
# Header con logo + título
# ---------------------------
h1, h2 = st.columns([0.3, 6])

with h1:
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    st.image("logo.png", width=90)

with h2:
    st.markdown(
        """
        <div class="title">Planeación - Planta de producción</div>
        <div class="sub">Dashboard para la planeación y seguimiento de actividades de manufactura</div>
        """,
        unsafe_allow_html=True,
    )

n_inp = int((df["STATUS"] == "IN PROCESS").sum())
n_stb = int((df["STATUS"] == "STAND BY").sum())
n_uns = int((df["STATUS"] == "UNSTARTED").sum())
n_atr = int(df["atrasado_item"].sum())
n_sin = int(df["sin_confirmar_item"].sum())

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi("Items/Filas en proceso", n_inp, "Filas de excel con status: IN PROCESS")
with c2: kpi("Items/Filas en stand by", n_stb, "Filas de excel con status: STAND BY")
with c3: kpi("Items/Filas sin iniciar", n_uns, "Filas de excel con status: UNSTARTED")
with c4: kpi("Atrasados", n_atr, "Entrega vencida con avance < 100% (por fila)")
with c5: kpi("Sin confirmar", n_sin, "Fecha de entrega: X CONFIRMAR/vacía/no fecha")

st.markdown("<div style='height: 7px'></div>", unsafe_allow_html=True)
# ---------------------------
# Tabs
# ---------------------------
t1, t2, t3 = st.tabs(["📋 Programa de trabajo", "🚚 Despachos", "🗓️ Programación de planta"])

with t1:
    render_programa_tab(df)  # filtros se aplican adentro

with t2:
    render_despachos_tab(despachos)

with t3:
    render_programacion_tab()