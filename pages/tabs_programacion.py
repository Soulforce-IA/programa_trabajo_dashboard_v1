import streamlit as st
import os
import base64

# =====================================================
# FUNCIÓN AUXILIAR: IMÁGENES A BASE64
# =====================================================
def get_image_base64(path):
    try:
        if not path or not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

# =====================================================
# CONFIGURACIÓN DE IMÁGENES
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
    img_b64 = get_image_base64(img_path)
    
    # Si hay imagen la pone, si no pone un emoji de fábrica
    img_html = f'<img src="data:image/png;base64,{img_b64}" class="machine-img">' if img_b64 else "🏭"

    filas_html = ""
    actividades = maquina.get("actividades", [])
    if actividades:
        for act in actividades:
            filas_html += f'<div class="activity-box"><span><b>{act.get("oit", "N/A")}</b></span><span>{act.get("desc", "")}</span></div>'
    else:
        filas_html = '<div class="no-activity">Sin actividades programadas</div>'

    card_html = f"""
    <div class="machine-card">
        <div class="card-header-row">
            <div class="machine-img-container">{img_html}</div>
            <div>
                <div class="machine-title">{maquina.get('maquina', 'Desconocida')}</div>
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
def render_programacion_tab(df=None, kpi_data=None):
    # INYECTAMOS EL CSS AQUÍ PARA ASEGURAR QUE SE CARGUE EN LA CLOUD
    st.markdown(
        """
        <style>
        /* AJUSTE DE ESPACIO SUPERIOR */
        div[data-testid="stVerticalBlock"] > div:has(div.machine-card) {
            margin-top: -5px !important; 
        }

        .grid-container {
            padding-top: 8px;
        }

        .machine-card {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 12px !important;
            margin-bottom: 15px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
            display: flex !important;
            flex-direction: column !important; 
            gap: 10px !important;
            height: 180px !important; 
            overflow: hidden !important;
        }

        .card-header-row {
            display: flex !important;
            gap: 10px !important;
            align-items: center !important;
            border-bottom: 1px solid #f3f4f6 !important;
            padding-bottom: 8px !important;
        }

        .machine-img-container {
            flex-shrink: 0 !important;
            width: 75px !important;
            height: 75px !important;
            border-radius: 5px !important;
            overflow: hidden !important;
            background-color: #f3f4f6 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .machine-img {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
        }

        .machine-title {
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #111827 !important;
            margin: 0 !important;
            line-height: 1.1 !important;
        }

        .machine-sub {
            font-size: 14px !important;
            color: #9ca3af !important;
        }

        .activities-scroll-area {
            flex-grow: 1 !important;
            overflow-y: auto !important;
            padding-right: 2px !important;
        }

        .activity-box {
            background-color: #f8fafc !important;
            border-left: 3px solid #3b82f6 !important;
            padding: 4px 8px !important;
            border-radius: 4px !important;
            margin-bottom: 4px !important;
            font-size: 14px !important;
            color: #334155 !important;
            display: flex !important;
            justify-content: space-between !important;
        }

        .no-activity {
            font-size: 14px !important;
            color: #9ca3af !important;
            font-style: italic !important;
            padding-top: 5px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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