import streamlit as st
import os
import base64

# =====================================================
# FUNCIÓN AUXILIAR: IMÁGENES A BASE64
# =====================================================
def get_image_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# =====================================================
# ESTILOS CSS (EQUILIBRIO DE ESPACIOS)
# =====================================================
st.markdown(
    """
    <style>
    /* 1. AJUSTE DE ESPACIO SUPERIOR (SUAVIZADO) */
    /* Subimos el bloque de la pestaña pero dejando un margen de seguridad */
    div[data-testid="stVerticalBlock"] > div:has(div.machine-card) {
        margin-top: -5px !important; 
    }

    /* 2. CONTENEDOR DE GRILLA CON RESPIRO */
    .grid-container {
        padding-top: 8px; /* Crea el espacio necesario entre la pestaña y las cards */
    }

    .machine-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column; 
        gap: 10px;
        height: 180px; 
        overflow: hidden;
    }

    .card-header-row {
        display: flex;
        gap: 10px;
        align-items: center;
        border-bottom: 1px solid #f3f4f6;
        padding-bottom: 8px;
    }

    .machine-img-container {
        flex-shrink: 0;
        width: 75px;
        height: 75px;
        border-radius: 5px;
        overflow: hidden;
        background-color: #f3f4f6;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .machine-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .machine-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin: 0;
        line-height: 1.1;
    }

    .machine-sub {
        font-size: 14px;
        color: #9ca3af;
    }

    .activities-scroll-area {
        flex-grow: 1;
        overflow-y: auto;
        padding-right: 2px;
    }

    .activity-box {
        background-color: #f8fafc;
        border-left: 3px solid #3b82f6;
        padding: 4px 8px;
        border-radius: 4px;
        margin-bottom: 4px;
        font-size: 14px;
        color: #334155;
        display: flex;
        justify-content: space-between;
    }

    .no-activity {
        font-size: 14px;
        color: #9ca3af;
        font-style: italic;
        padding-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# CONFIGURACIÓN DE IMÁGENES Y RENDERIZADO
# =====================================================
IMAGENES = {
    "Torno LTC": "assets/ltc.png",
    "Torno DOOSAN": "assets/doosan.png",
    "Torno WINSTON": "assets/winston.png",
    "Torno BULG Nuevo": "assets/bulg-new.png",
    "Torno DMTG 1": "assets/dmtg1.png",
    "Torno DMTG 2": "assets/dmtg2.png",
}

def render_maquina_card(maquina):
    img_path = IMAGENES.get(maquina["maquina"])
    img_b64 = get_image_base64(img_path) if img_path else None
    img_html = f'<img src="data:image/png;base64,{img_b64}" class="machine-img">' if img_b64 else "🏭"

    filas_html = ""
    if maquina["actividades"]:
        for act in maquina["actividades"]:
            filas_html += f'<div class="activity-box"><span><b>{act["oit"]}</b></span><span>{act["desc"]}</span></div>'
    else:
        filas_html = '<div class="no-activity">Sin actividades programadas</div>'

    card_html = f"""
    <div class="machine-card">
        <div class="card-header-row">
            <div class="machine-img-container">{img_html}</div>
            <div>
                <div class="machine-title">{maquina['maquina']}</div>
                <div class="machine-sub">Costo hora: --</div>
            </div>
        </div>
        <div class="activities-scroll-area">
            {filas_html}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# =====================================================
# TAB PROGRAMACIÓN
# =====================================================
def render_programacion_tab():
    maquinas = [
        {"maquina": "Torno LTC", "centro": "Tornos", "actividades": [{"oit": "OIT-101", "desc": "Mecanizado eje principal"}, {"oit": "OIT-102", "desc": "Rosca interna 2 pulgadas"}, {"oit": "OIT-103", "desc": "Acabado superficial"}]},
        {"maquina": "Torno DOOSAN", "centro": "Tornos", "actividades": [{"oit": "OIT-201", "desc": "Desbaste material"}, {"oit": "OIT-202", "desc": "Perforación profunda"}, {"oit": "OIT-203", "desc": "Control calidad"}]},
        {"maquina": "Torno WINSTON", "centro": "Tornos", "actividades": [{"oit": "OIT-301", "desc": "Ajuste mordazas"}, {"oit": "OIT-302", "desc": "Producción serie"}]},
        {"maquina": "Torno BULG Nuevo", "centro": "Tornos", "actividades": [{"oit": "OIT-401", "desc": "Corte prototipo"}, {"oit": "OIT-402", "desc": "Torneado cónico"}]},
        {"maquina": "Torno DMTG 1", "centro": "Tornos", "actividades": [{"oit": "OIT-501", "desc": "Mantenimiento"}, {"oit": "OIT-502", "desc": "Rectificado bridas"}]},
        {"maquina": "Torno DMTG 2", "centro": "Tornos", "actividades": [{"oit": "OIT-601", "desc": "Producción piñones"}, {"oit": "OIT-602", "desc": "Escariado"}]},
        {"maquina": "Centro de mecanizado 1", "centro": "Centros", "actividades": [{"oit": "OIT-701", "desc": "Fresado bloque"}, {"oit": "OIT-702", "desc": "Taladrado patrón"}]},
        {"maquina": "Centro de mecanizado 2", "centro": "Centros", "actividades": [{"oit": "OIT-801", "desc": "Planeado base"}, {"oit": "OIT-802", "desc": "Mecanizado 5 ejes"}]},
        {"maquina": "Fresadora vertical", "centro": "Fresado", "actividades": [{"oit": "OIT-901", "desc": "Ranurado chaveteros"}]},
        {"maquina": "Banco de fosfatado", "centro": "Tratamientos", "actividades": [{"oit": "OIT-010", "desc": "Anticorrosión"}]},
        {"maquina": "Labores auxiliares", "centro": "Apoyo", "actividades": [{"oit": "OIT-AUX1", "desc": "Transporte pesado"}]},
        {"maquina": "Técnicos de ensamble", "centro": "Apoyo", "actividades": [{"oit": "OIT-ENS1", "desc": "Armado conjunto A"}]},
    ]

    # Contenedor especial para el espaciado
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    
    for i in range(0, len(maquinas), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(maquinas):
                with cols[j]:
                    render_maquina_card(maquinas[i + j])
                    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render_programacion_tab()