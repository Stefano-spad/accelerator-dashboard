import base64
import glob
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Base Accelerator", page_icon="🚀", layout="wide")

# ------------------------------------------------------------------
# CONFIGURACIÓN: nombres de archivo y columnas
# ------------------------------------------------------------------
NOMBRE_CSV = "base_accelerator.csv"
NOMBRE_LOGO = "workana_logo.svg"      # opcional: si está en la carpeta, se usa ese
NOMBRE_FUENTE = "cooper_light.woff2"  # Cooper Light BT convertida para la web
VERSION = "v5 · 24-10-2026"           # se muestra al pie de la barra lateral
COL_NOMBRE = "name"
COL_PAIS = "country"
COL_INSC = "fecha de inscripción"
COL_REG = "fecha de registro en Workana"
COL_SKILL = "skill"
COL_USER = "user_id"
COL_EDAD = "edad"
COL_PAIS_NOM = "País"                 # columna nueva (calculada)
COL_ANTIG = "Días en Workana"         # columna nueva (calculada)
COL_SEGMENTO = "Antigüedad"           # columna nueva (calculada)
COL_RANGO = "Rango de edad"           # columna nueva (calculada)

# ------------------------------------------------------------------
# BRANDING: colores institucionales y tipografías
# ------------------------------------------------------------------
AZUL = "#002D72"        # azul institucional (PANTONE 288 C)
AZUL_OSC = "#001E4D"    # barra lateral
LILA = "#DCB0E7"        # color secundario   (PANTONE 243 C)
CREMA = "#E8E8CA"       # tercer color       (PANTONE 7527 C)
CREMA_CLARO = "#F2F2E2"
BLANCO = "#FFFFFF"
TEXTO_CLARO = "#F2F5FB"     # texto sobre fondo azul
TEXTO_CLARO_TENUE = "#C7D4EA"
TINTA = AZUL                # texto sobre los paneles claros
TINTA_TENUE = "#4A6898"

# Paleta de datos: se usa en los KPIs y en todas las series de los gráficos
VERDE = "#69DAB9"
ROSA = "#FF699D"
CELESTE = "#5A85FF"
AMARILLO = "#FFEB90"
NARANJA = "#FF9655"
NEUTRO = "#9FB3D1"      # solo para la categoría de control "Revisar fecha"

FUENTE_TITULO = ("'CooperLight', 'Cooper Lt BT', 'Cooper Light', 'Bree Serif', "
                 "Georgia, serif")
FUENTE_TEXTO = "'Poppins', 'Segoe UI', sans-serif"

ORDEN_ANTIG = ["Recién llegado", "Nuevo", "Con experiencia", "Veterano",
               "Revisar fecha"]
COLOR_ANTIG = {
    "Recién llegado": VERDE,
    "Nuevo": AMARILLO,
    "Con experiencia": NARANJA,
    "Veterano": ROSA,
    "Revisar fecha": NEUTRO,
}
TEXTURA_ANTIG = {"Recién llegado": "/", "Nuevo": "x", "Con experiencia": "-",
                 "Veterano": "+", "Revisar fecha": "."}

ORDEN_RANGO = ["20 a 24", "25 a 29", "30 a 34", "35 a 40"]
COLOR_RANGO = {"20 a 24": CELESTE, "25 a 29": VERDE,
               "30 a 34": ROSA, "35 a 40": NARANJA}

# Para las categorías que superan los 5 colores, se repite la familia en
# versiones más profundas y más suaves del mismo tono
PALETA = [CELESTE, ROSA, VERDE, NARANJA, AMARILLO,
          "#3E66D9", "#E04A80", "#3FB998", "#E07A3C", "#E8D06A",
          "#8FA9FF", "#FF9BBE"]
TEXTURAS = ["/", "\\", "x", "-", "|", "+", ".", "/", "\\", "x", "-", "|"]

# Los KPIs usan los 5 colores de la paleta; el sexto vuelve al lila de marca
COLOR_KPI = [CELESTE, VERDE, NARANJA, ROSA, AMARILLO, LILA]

# Código ISO de 2 letras -> nombre, para que los gráficos se lean mejor
PAISES = {
    "AR": "Argentina", "BO": "Bolivia", "BR": "Brasil", "CA": "Canadá",
    "CL": "Chile", "CO": "Colombia", "CR": "Costa Rica", "DO": "Rep. Dominicana",
    "EC": "Ecuador", "ES": "España", "GT": "Guatemala", "MX": "México",
    "MZ": "Mozambique", "PA": "Panamá", "PE": "Perú", "PY": "Paraguay",
    "US": "Estados Unidos", "UY": "Uruguay", "VE": "Venezuela",
}

# Logo institucional embebido (si existe el .svg en la carpeta, se usa ese)
LOGO_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzODEuMiAzODEuMiI+PHRpdGxlPlJlY3Vyc28gN2xkcGk8L3RpdGxlPjxnIGlkPSJDYXBhXzIiIGRhdGEtbmFtZT0iQ2FwYSAyIj48ZyBpZD0iQ2FwYV8xLTIiIGRhdGEtbmFtZT0iQ2FwYSAxIj48cGF0aCBkPSJNMTkwLjYsODIuNUExOTEuMSwxOTEuMSwwLDAsMSwzMzEuOCw2Mi42YTE5MC42LDE5MC42LDAsMCwwLTI4Mi40LDBBMTkxLjEsMTkxLjEsMCwwLDEsMTkwLjYsODIuNSIgc3R5bGU9ImZpbGw6I2Y5YzYxMSIvPjxwYXRoIGQ9Ik03LjUsMTM3LjRBMTkwLjYsMTkwLjYsMCwwLDAsMCwxOTAuNmMwLDg5LjQsNjEuNiwxNjQuNSwxNDQuNywxODVBMTg5LjksMTg5LjksMCwwLDEsOTUuMywyNDkuMywxOTEuMSwxOTEuMSwwLDAsMSw3LjUsMTM3LjQiIHN0eWxlPSJmaWxsOiNmOTQ4MTAiLz48cGF0aCBkPSJNOTUuMywyNDkuM2MwLS42LDAtMS4xLDAtMS43QTE5MC41LDE5MC41LDAsMCwxLDE5MC42LDgyLjUsMTkxLjEsMTkxLjEsMCwwLDAsNDkuNCw2Mi42LDE5MC4zLDE5MC4zLDAsMCwwLDcuNSwxMzcuNCwxOTEuMSwxOTEuMSwwLDAsMCw5NS4zLDI0OS4zIiBzdHlsZT0iZmlsbDojZjU5NmIxIi8+PHBhdGggZD0iTTI4NS45LDI0OS4zYTE4OS45LDE4OS45LDAsMCwxLTQ5LjQsMTI2LjNjODMuMS0yMC42LDE0NC43LTk1LjYsMTQ0LjctMTg1YTE5MC43LDE5MC43LDAsMCwwLTcuNS01My4yLDE5MS4xLDE5MS4xLDAsMCwxLTg3LjgsMTExLjkiIHN0eWxlPSJmaWxsOiMwYTc4ZmYiLz48cGF0aCBkPSJNMjg1LjksNTdhMTg5LjcsMTg5LjcsMCwwLDAtOTUuMywyNS41LDE5MC41LDE5MC41LDAsMCwxLDk1LjMsMTY1LjFjMCwuNiwwLDEuMSwwLDEuN2ExOTEuMSwxOTEuMSwwLDAsMCw4Ny44LTExMS45LDE5MC4zLDE5MC4zLDAsMCwwLTQxLjgtNzQuOEExOTEsMTkxLDAsMCwwLDI4NS45LDU3IiBzdHlsZT0iZmlsbDojMTQ5MjQzIi8+PHBhdGggZD0iTTE5MC42LDI3NC44YTE4OS43LDE4OS43LDAsMCwxLTk1LjMtMjUuNSwxODkuOSwxODkuOSwwLDAsMCw0OS40LDEyNi4zLDE5MS43LDE5MS43LDAsMCwwLDkxLjgsMCwxODkuOSwxODkuOSwwLDAsMCw0OS40LTEyNi4zLDE4OS43LDE4OS43LDAsMCwxLTk1LjMsMjUuNSIgc3R5bGU9ImZpbGw6I2MxMTk4OSIvPjxwYXRoIGQ9Ik05NS4zLDI0Ny42YzAsLjYsMCwxLjEsMCwxLjdhMTkwLjgsMTkwLjgsMCwwLDAsMTkwLjYsMGMwLS42LDAtMS4xLDAtMS43QTE5MC41LDE5MC41LDAsMCwwLDE5MC42LDgyLjUsMTkwLjUsMTkwLjUsMCwwLDAsOTUuMywyNDcuNiIgc3R5bGU9ImZpbGw6IzAwMmQ3MiIvPjwvZz48L2c+PC9zdmc+Cg=="


def archivo_base64(nombre):
    """Devuelve el archivo de la carpeta del proyecto en base64, o None."""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre)
    if os.path.exists(ruta):
        with open(ruta, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    return None


def logo_base64():
    return archivo_base64(NOMBRE_LOGO) or LOGO_B64


def regla_cooper():
    """Carga Cooper Light BT desde la carpeta; si no está, usa la instalada."""
    fuente = archivo_base64(NOMBRE_FUENTE)
    if fuente:
        origen = (f"url(data:font/woff2;base64,{fuente}) format('woff2'), "
                  "local('Cooper Lt BT'), local('Cooper Light')")
    else:
        origen = ("local('Cooper Lt BT'), local('Cooper Light'), "
                  "local('CooperBT-Light')")
    return ("@font-face { font-family:'CooperLight'; src:%s;"
            " font-weight:300 400; font-style:normal; font-display:swap; }" % origen)


# ------------------------------------------------------------------
# MODO DÍA / MODO NOCHE
# ------------------------------------------------------------------
# El interruptor se crea antes que el CSS porque de él sale todo el tema.
# Aparece arriba de todo en la barra lateral; los filtros siguen más abajo.
st.sidebar.title("🔎 Filtros")
if hasattr(st.sidebar, "toggle"):          # toggle existe desde Streamlit 1.26
    MODO_DIA = st.sidebar.toggle("☀️ Modo día", value=False)
else:
    MODO_DIA = st.sidebar.checkbox("☀️ Modo día", value=False)

if MODO_DIA:
    FONDO = CREMA                  # la página pasa al crema
    PANEL = BLANCO                 # y los paneles al blanco
    PANEL_SUAVE = "#F7F7F0"
    TEXTO_FONDO = AZUL             # texto directo sobre la página
    TEXTO_FONDO_TENUE = TINTA_TENUE
    TITULOS = AZUL
    PUNTO, RAYA = "rgba(0,45,114,0.08)", "rgba(255,255,255,0.35)"
    SOMBRA = "0 2px 8px rgba(0,45,114,0.16)"
else:
    FONDO = AZUL                   # el tema original: página azul
    PANEL = CREMA                  # y paneles crema
    PANEL_SUAVE = CREMA_CLARO
    TEXTO_FONDO = TEXTO_CLARO
    TEXTO_FONDO_TENUE = TEXTO_CLARO_TENUE
    TITULOS = CREMA
    PUNTO, RAYA = "rgba(220,176,231,0.14)", "rgba(255,255,255,0.035)"
    SOMBRA = "0 2px 8px rgba(0,0,0,0.28)"

# Escala del heatmap: arranca en el color del panel y sube por la paleta
ESCALA_HEATMAP = [[0.0, PANEL_SUAVE], [0.30, AMARILLO], [0.65, NARANJA],
                  [1.0, ROSA]]
# Las barras llevan trama; este relleno suave hace que el color se lea mejor
TRAMA = dict(solidity=0.52, bgcolor=PANEL_SUAVE)
BORDE_BARRA = dict(color=AZUL, width=1)

# ------------------------------------------------------------------
# ESTILO: fondo con textura, tipografías y logo
# ------------------------------------------------------------------
# OJO: el HTML que se inyecta no puede tener líneas en blanco adentro;
# markdown corta el bloque y el resto del CSS se vería como texto suelto.
FUENTES_WEB = ("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;"
               "500;600;700&family=Bree+Serif&display=swap")
CSS = [
    f'<link href="{FUENTES_WEB}" rel="stylesheet">',
    "<style>",
    regla_cooper(),
    # Fondo de la página, con la misma textura en los dos modos
    ".stApp { background-color:%s;"
    " background-image: radial-gradient(%s 1.6px, transparent 1.6px),"
    " repeating-linear-gradient(45deg, %s 0 10px, transparent 10px 20px);"
    " background-size: 24px 24px, auto; }" % (FONDO, PUNTO, RAYA),
    # La barra lateral queda azul en los dos modos: ancla la marca y
    # mantiene legibles los controles (Streamlit los dibuja en tema oscuro)
    '[data-testid="stSidebar"] { background-color:%s;'
    " background-image: radial-gradient(rgba(220,176,231,0.16) 1.6px, transparent 1.6px),"
    " repeating-linear-gradient(-45deg, rgba(255,255,255,0.045) 0 10px, transparent 10px 20px);"
    " background-size: 24px 24px, auto; min-width:330px; }" % AZUL_OSC,
    '[data-testid="stHeader"] { background: transparent; }',
    # Esquinas redondeadas para los paneles de los gráficos
    '[data-testid="stPlotlyChart"] > div, [data-testid="stPlotlyChart"] iframe'
    " { border-radius:12px; overflow:hidden; box-shadow:%s; }" % SOMBRA,
    # Tipografías: Cooper Light para títulos, Poppins para el resto.
    # No se tocan div ni span: heredan igual y, si se los fuerza, los
    # iconos de Streamlit pierden su fuente y aparecen como texto.
    ".stApp, .stApp p, .stApp li, .stApp label, .stApp button,"
    ' .stApp [data-testid="stMarkdownContainer"],'
    ' [data-testid="stSidebar"], [data-testid="stSidebar"] label'
    " { font-family:%s; }" % FUENTE_TEXTO,
    '.stApp [data-testid="stIconMaterial"], .stApp span[class*="material-symbols"],'
    ' .stApp i[class*="material-icons"], .stApp span[class*="material-icons"]'
    " { font-family:'Material Symbols Rounded','Material Icons Rounded',"
    "'Material Icons' !important; }",
    ".stApp h1, .stApp h2, .stApp h3, .stApp h4,"
    ' [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2'
    " { font-family:%s; font-weight:400; letter-spacing:0.4px; }" % FUENTE_TITULO,
    ".stApp h1 { font-size:2.9rem; }",
    # Colores de texto sobre el fondo de la página
    ".stApp p, .stApp label,"
    ' .stApp [data-testid="stMarkdownContainer"] { color:%s; }' % TEXTO_FONDO,
    '.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] *'
    " { color:%s; }" % TEXTO_FONDO_TENUE,
    ".stApp h1, .stApp h2, .stApp h3 { color:%s; }" % TITULOS,
    # La barra lateral va siempre en claro; necesita más especificidad que
    # las reglas de arriba para no apagarse en modo día
    '.stApp [data-testid="stSidebar"] p, .stApp [data-testid="stSidebar"] label,'
    ' .stApp [data-testid="stSidebar"] div, .stApp [data-testid="stSidebar"] span,'
    ' .stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]'
    " { color:%s; }" % TEXTO_CLARO,
    '.stApp [data-testid="stSidebar"] h1 { color:%s; }' % LILA,
    # Controles de la barra lateral
    '[data-testid="stSidebar"] [data-baseweb="select"] > div,'
    ' [data-testid="stSidebar"] [data-baseweb="input"] > div'
    " { background-color: rgba(255,255,255,0.08); border-color: rgba(220,176,231,0.45); }",
    '[data-testid="stSidebar"] [data-baseweb="tag"]'
    " { background-color:%s !important; color:%s !important; }" % (LILA, AZUL),
    # Los <code> del cuadro de criterios, sobre el panel claro
    '.stApp [data-testid="stMarkdownContainer"] code'
    " { background: rgba(0,45,114,0.09); color:#17457F;"
    " padding:1px 5px; border-radius:4px; }",
    # Logo institucional, fijo arriba a la derecha
    # el 50%% va doble: la cadena se arma con formateo %
    ".logo-workana { position:fixed; top:62px; right:26px; z-index:900;"
    " background:#FFFFFF; border-radius:50%%; padding:9px;"
    " box-shadow:%s; line-height:0; }" % SOMBRA,
    ".logo-workana img { width:62px; height:62px; display:block; }",
    "@media (max-width:1200px) { .logo-workana { display:none; } }",
    "</style>",
    '<div class="logo-workana">'
    f'<img src="data:image/svg+xml;base64,{logo_base64()}" alt="Workana"></div>',
]
st.markdown("\n".join(CSS), unsafe_allow_html=True)


# ------------------------------------------------------------------
# 1) Cargar y preparar los datos (se guarda en memoria para ir rápido)
# ------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(carpeta, NOMBRE_CSV)
    if not os.path.exists(ruta):  # por si el archivo se renombra
        candidatos = sorted(glob.glob(os.path.join(carpeta, "*.csv")))
        if not candidatos:
            st.error(f"No encontré ningún CSV en la carpeta {carpeta}.")
            st.stop()
        ruta = candidatos[0]

    # El archivo viene separado por comas y en UTF-8 (export de una query)
    try:
        d = pd.read_csv(ruta, sep=",", encoding="utf-8-sig")
    except UnicodeDecodeError:
        d = pd.read_csv(ruta, sep=",", encoding="cp1252")

    # Fechas en formato año-mes-día; la inscripción trae además la hora
    d[COL_INSC] = pd.to_datetime(d[COL_INSC], format="mixed", errors="coerce")
    d[COL_REG] = pd.to_datetime(d[COL_REG], format="mixed", errors="coerce")

    # Limpieza de texto y nombre de país
    for c in (COL_NOMBRE, COL_PAIS, COL_SKILL):
        d[c] = d[c].astype(str).str.strip()
    d[COL_SKILL] = d[COL_SKILL].replace({"": np.nan, "nan": np.nan}).fillna("Sin skill")
    d[COL_PAIS] = d[COL_PAIS].str.upper()
    d[COL_PAIS_NOM] = d[COL_PAIS].map(PAISES).fillna(d[COL_PAIS])
    d[COL_EDAD] = pd.to_numeric(d[COL_EDAD], errors="coerce")

    # NUEVA COLUMNA: días que ya llevaba en Workana al momento de inscribirse
    dias = (d[COL_INSC].dt.normalize() - d[COL_REG].dt.normalize()).dt.days
    d[COL_ANTIG] = dias.where(d[COL_INSC].notna() & d[COL_REG].notna())

    # NUEVA COLUMNA: segmento según esos días
    #   0 a 30 = Recién llegado | 31 a 90 = Nuevo
    #   91 a 365 = Con experiencia | más de 365 = Veterano
    #   negativos = se registró después de inscribirse (revisar)
    d[COL_SEGMENTO] = pd.cut(
        d[COL_ANTIG],
        bins=[-float("inf"), -1, 30, 90, 365, float("inf")],
        labels=["Revisar fecha", "Recién llegado", "Nuevo",
                "Con experiencia", "Veterano"],
    ).astype(object)

    # NUEVA COLUMNA: rango de edad
    d[COL_RANGO] = pd.cut(
        d[COL_EDAD], bins=[-float("inf"), 24, 29, 34, float("inf")],
        labels=ORDEN_RANGO,
    ).astype(object)
    return d


df = cargar_datos()

# Colores y texturas fijos por skill (el más numeroso va en naranja de marca)
skills = sorted(df[COL_SKILL].unique())
SKILL_DESTACADO = df[COL_SKILL].value_counts().idxmax()
color_skill, textura_skill = {}, {}
otros = [c for c in PALETA if c != NARANJA]
i = 0
for s in skills:
    if s == SKILL_DESTACADO:
        color_skill[s] = NARANJA
        textura_skill[s] = "/"
    else:
        color_skill[s] = otros[i % len(otros)]
        textura_skill[s] = TEXTURAS[(i + 1) % len(TEXTURAS)]
        i += 1


def mostrar(fig):
    """Muestra un gráfico de Plotly ocupando todo el ancho."""
    fig.update_layout(
        paper_bgcolor=PANEL,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TINTA, family="Poppins, Segoe UI, sans-serif", size=13),
        title_font=dict(color=AZUL, family="CooperLight, Bree Serif, Georgia, serif",
                        size=20),
        legend=dict(font=dict(color=TINTA)),
        margin=dict(l=14, r=14, t=58, b=14),
    )
    # title_font explícito: si no, el título del eje toma el gris del
    # template de Plotly y se apaga sobre el panel claro
    ejes = dict(gridcolor="rgba(0,45,114,0.14)",
                zerolinecolor="rgba(0,45,114,0.28)",
                linecolor="rgba(0,45,114,0.35)",
                tickfont=dict(color=TINTA_TENUE),
                title_font=dict(color=TINTA, size=13))
    fig.update_xaxes(**ejes)
    fig.update_yaxes(**ejes)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:  # versiones viejas de Streamlit
        st.plotly_chart(fig, use_container_width=True)


def tarjeta(titulo, valor, color, texto=AZUL):
    """Tarjeta grande de color para un KPI."""
    return f"""
    <div style="background:{color}; border-radius:14px; padding:18px 10px; min-height:122px;
                text-align:center; margin-bottom:10px;
                box-shadow:{SOMBRA};">
        <div style="font-family:{FUENTE_TEXTO}; font-size:14px; color:{texto};
                    opacity:0.92; font-weight:500;">{titulo}</div>
        <div style="font-family:{FUENTE_TITULO}; font-size:40px; font-weight:400;
                    color:{texto};">{valor}</div>
    </div>"""


def miles(n):
    return f"{n:,.0f}".replace(",", ".")


def pct(parte, base):
    """Porcentaje con coma decimal, por ejemplo 85,7%."""
    if not base:
        return "0,0%"
    return f"{parte / base * 100:.1f}".replace(".", ",") + "%"


def dec(x):
    """Número con 1 decimal y coma, por ejemplo 4,7."""
    return f"{x:.1f}".replace(".", ",")


def caja(html):
    """Panel crema para textos, intercalado con el fondo azul."""
    st.markdown(
        f'''<div style="background:{PANEL}; border-radius:12px;
        border:1px solid rgba(0,45,114,0.22);
        padding:16px 22px; margin:6px 0 14px 0; color:{TINTA};
        font-family:{FUENTE_TEXTO}; line-height:1.60;
        box-shadow:{SOMBRA};">{html}</div>''',
        unsafe_allow_html=True,
    )


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ------------------------------------------------------------------
# 2) Barra lateral: filtros
# ------------------------------------------------------------------
ins_min, ins_max = df[COL_INSC].min().date(), df[COL_INSC].max().date()
rango_ins = st.sidebar.date_input(
    "Fecha de inscripción", value=(ins_min, ins_max),
    min_value=ins_min, max_value=ins_max, format="DD/MM/YYYY",
)

reg_min, reg_max = df[COL_REG].min().date(), df[COL_REG].max().date()
rango_reg = st.sidebar.date_input(
    "Fecha de registro en Workana", value=(reg_min, reg_max),
    min_value=reg_min, max_value=reg_max, format="DD/MM/YYYY",
)

ed_min, ed_max = int(df[COL_EDAD].min()), int(df[COL_EDAD].max())
rango_edad = st.sidebar.slider("Edad", ed_min, ed_max, (ed_min, ed_max))

st.sidebar.markdown("**Categorías** (vacío = todas)")
sel_skill = st.sidebar.multiselect("Especialidad (skill)", skills, placeholder="Todas")
sel_pais = st.sidebar.multiselect(
    "País", sorted(df[COL_PAIS_NOM].dropna().unique()), placeholder="Todos"
)
sel_seg = st.sidebar.multiselect(
    COL_SEGMENTO,
    [s for s in ORDEN_ANTIG if s in set(df[COL_SEGMENTO].dropna())],
    placeholder="Todas",
)
top_n = st.sidebar.slider("Países a mostrar en los gráficos", 5, 20, 12)
st.sidebar.caption(VERSION)

# Si el usuario eligió solo una fecha del calendario, esperar a que elija la otra
if len(rango_ins) != 2 or len(rango_reg) != 2:
    st.info("Elegí la fecha de inicio **y** la fecha de fin en los calendarios.")
    st.stop()

# ------------------------------------------------------------------
# 3) Aplicar los filtros
# ------------------------------------------------------------------
f = df[df[COL_INSC].between(
    pd.Timestamp(rango_ins[0]), pd.Timestamp(rango_ins[1]) + pd.Timedelta(days=1)
)]
f = f[f[COL_REG].between(pd.Timestamp(rango_reg[0]), pd.Timestamp(rango_reg[1]))]
f = f[f[COL_EDAD].between(rango_edad[0], rango_edad[1])]

if sel_skill:
    f = f[f[COL_SKILL].isin(sel_skill)]
if sel_pais:
    f = f[f[COL_PAIS_NOM].isin(sel_pais)]
if sel_seg:
    f = f[f[COL_SEGMENTO].isin(sel_seg)]

# ------------------------------------------------------------------
# 4) Título, filas y columnas
# ------------------------------------------------------------------
st.title("Base Accelerator")
caja(
    "<b>¿Qué busca este proyecto?</b><br>"
    "Esta base reúne a los freelancers que se inscribieron al programa "
    "<b>Accelerator</b> de Workana entre el "
    f"{df[COL_INSC].min().strftime('%d/%m/%Y')} y el "
    f"{df[COL_INSC].max().strftime('%d/%m/%Y')}. "
    "El análisis busca entender <b>cuántos</b> se inscriben, <b>de qué países</b>, "
    "<b>con qué especialidad</b>, <b>qué edad</b> tienen y <b>cuánta antigüedad</b> "
    "traían en la plataforma al momento de anotarse.<br>"
    "La columna <i>Días en Workana</i> mide la diferencia entre la fecha de registro "
    "en la plataforma y la fecha de inscripción al programa: sirve para separar a "
    "quienes recién llegaron de los perfiles ya establecidos.<br>"
    "Por protección de datos, los nombres figuran solo con la inicial del apellido."
    f"<div style='margin-top:20px; color:{TINTA_TENUE}; font-size:0.85em;'>"
    "Usá los filtros de la barra lateral: todos los gráficos, indicadores "
    "e insights se actualizan solos.</div>"
)

# --- Criterio de las columnas calculadas ---
CRITERIOS = [
    (COL_PAIS_NOM, "<code>country</code>",
     "Traduce el código ISO de 2 letras al nombre del país "
     "(BR → Brasil, CO → Colombia…). Si un código no está en la lista, "
     "se muestra tal cual vino."),
    (COL_ANTIG, f"<code>{COL_INSC}</code> − <code>{COL_REG}</code>",
     "Días que el freelancer ya llevaba registrado en Workana cuando se inscribió "
     "al programa. Se calcula sobre fechas sin hora; queda vacío si falta alguna "
     "de las dos fechas."),
    (COL_SEGMENTO, f"<code>{COL_ANTIG}</code>",
     "<b>Recién llegado:</b> 0 a 30 días &nbsp;|&nbsp; <b>Nuevo:</b> 31 a 90 "
     "&nbsp;|&nbsp; <b>Con experiencia:</b> 91 a 365 &nbsp;|&nbsp; "
     "<b>Veterano:</b> más de 365 &nbsp;|&nbsp; <b>Revisar fecha:</b> valores "
     "negativos (registro posterior a la inscripción)."),
    (COL_RANGO, "<code>edad</code>",
     "Agrupa la edad en cuatro tramos: 20 a 24, 25 a 29, 30 a 34 y 35 a 40 años."),
]
BORDE_FILA = "1px solid rgba(0,45,114,0.20)"
filas = "".join(
    f"""<tr>
        <td style="padding:9px 12px; border-top:{BORDE_FILA};
                   color:{AZUL}; font-weight:600; white-space:nowrap;">{n}</td>
        <td style="padding:9px 12px; border-top:{BORDE_FILA};
                   color:{TINTA_TENUE}; font-size:0.88em;">{origen}</td>
        <td style="padding:9px 12px; border-top:{BORDE_FILA};">{regla}</td>
    </tr>"""
    for n, origen, regla in CRITERIOS
)
caja(
    f"<div style='font-family:{FUENTE_TITULO}; font-size:1.35em; color:{AZUL}; "
    "margin-bottom:8px;'>📐 Criterio de las columnas calculadas</div>"
    "<div style='font-size:0.92em; margin-bottom:6px;'>Las 4 columnas que no vienen "
    "en el archivo original y se construyen al cargar los datos:</div>"
    "<table style='width:100%; border-collapse:collapse; font-size:0.93em;'>"
    "<tr style='background:rgba(0,45,114,0.07);'>"
    f"<th style='text-align:left; padding:7px 12px; color:{AZUL}; "
    "font-weight:600;'>Columna</th>"
    f"<th style='text-align:left; padding:7px 12px; color:{AZUL}; "
    "font-weight:600;'>Se calcula a partir de</th>"
    f"<th style='text-align:left; padding:7px 12px; color:{AZUL}; "
    "font-weight:600;'>Criterio</th>"
    "</tr>" + filas + "</table>"
)

st.write(
    f"El archivo tiene **{miles(df.shape[0])}** filas y **{df.shape[1]}** columnas "
    f"(incluye 4 calculadas). Con los filtros actuales se muestran "
    f"**{miles(len(f))}** inscriptos."
)

if f.empty:
    st.warning("No hay inscriptos con esos filtros. Probá ampliar la selección.")
    st.stop()

# ------------------------------------------------------------------
# 5) KPIs
# ------------------------------------------------------------------
total = len(f)
n_paises = f[COL_PAIS].nunique()
n_skills = f[COL_SKILL].nunique()
antig_ok = f[COL_ANTIG][f[COL_ANTIG] >= 0]
segmentados = f[COL_SEGMENTO].isin(
    ["Recién llegado", "Nuevo", "Con experiencia", "Veterano"])
pct_recien = ((f[COL_SEGMENTO] == "Recién llegado").sum() / segmentados.sum() * 100
              if segmentados.any() else 0)

# Los 5 colores de la paleta + el lila de marca en la última tarjeta.
# Todas llevan el texto en azul institucional: son tonos claros.
KPIS = [
    ("Inscriptos", miles(total)),
    ("Países", miles(n_paises)),
    ("Especialidades", miles(n_skills)),
    ("Edad promedio", dec(f[COL_EDAD].mean()) if f[COL_EDAD].notna().any() else "-"),
    ("Mediana días en Workana", f"{antig_ok.median():.0f}" if len(antig_ok) else "-"),
    ("Recién llegados", f"{pct_recien:.1f}%".replace(".", ",")),
]
k = st.columns(6)
for col, (titulo, valor), color in zip(k, KPIS, COLOR_KPI):
    col.markdown(tarjeta(titulo, valor, color, AZUL), unsafe_allow_html=True)

# ------------------------------------------------------------------
# 6) Gráficos
# ------------------------------------------------------------------
# --- Barras por skill (la especialidad más numerosa, destacada) ---
g_skill = f.groupby(COL_SKILL).size().reset_index(name="Inscriptos")
fig = px.bar(
    g_skill, x="Inscriptos", y=COL_SKILL, orientation="h", text="Inscriptos",
    color=COL_SKILL, color_discrete_map=color_skill,
    pattern_shape=COL_SKILL, pattern_shape_map=textura_skill,
    title="Inscriptos por especialidad (skill)",
)
fig.update_traces(textposition="outside", cliponaxis=False,
                  textfont=dict(color=TINTA),
                  marker=dict(pattern=TRAMA, line=BORDE_BARRA))
fig.update_layout(showlegend=False, yaxis=dict(categoryorder="total ascending", title=""))
mostrar(fig)

col1, col2 = st.columns(2)

# --- Evolución por fecha de inscripción ---
with col1:
    diario = f.groupby(f[COL_INSC].dt.normalize()).size()
    diario = diario.reindex(
        pd.date_range(diario.index.min(), diario.index.max()), fill_value=0
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=diario.index, y=diario.values, name="Inscripciones por día",
        mode="lines", line=dict(color=CELESTE, width=1.6),
        fill="tozeroy", fillpattern=dict(shape="/", fgcolor=CELESTE,
                                         bgcolor=PANEL_SUAVE),
    ))
    fig.add_trace(go.Scatter(
        x=diario.index, y=diario.rolling(7, min_periods=1).mean(),
        name="Promedio de 7 días", mode="lines", line=dict(color=NARANJA, width=3),
    ))
    fig.update_layout(
        title="Evolución de inscripciones por día",
        legend=dict(orientation="h", y=-0.15),
    )
    mostrar(fig)

# --- Antigüedad en Workana al inscribirse ---
with col2:
    g_s = (f[COL_SEGMENTO].value_counts().reindex(ORDEN_ANTIG).dropna()
           .reset_index())
    g_s.columns = [COL_SEGMENTO, "Inscriptos"]
    fig = px.bar(
        g_s, x=COL_SEGMENTO, y="Inscriptos", text="Inscriptos",
        color=COL_SEGMENTO, color_discrete_map=COLOR_ANTIG,
        pattern_shape=COL_SEGMENTO, pattern_shape_map=TEXTURA_ANTIG,
        title="Inscriptos según antigüedad en Workana",
    )
    fig.update_traces(textposition="outside", cliponaxis=False,
                      textfont=dict(color=TINTA),
                  marker=dict(pattern=TRAMA, line=BORDE_BARRA))
    fig.update_layout(showlegend=False, xaxis_title="")
    mostrar(fig)

col3, col4 = st.columns(2)

# --- Inscriptos por país ---
with col3:
    g_p = (f[COL_PAIS_NOM].value_counts().head(top_n)
           .reset_index())
    g_p.columns = [COL_PAIS_NOM, "Inscriptos"]
    fig = px.bar(
        g_p, x="Inscriptos", y=COL_PAIS_NOM, orientation="h", text="Inscriptos",
        color=COL_PAIS_NOM, color_discrete_sequence=PALETA,
        pattern_shape=COL_PAIS_NOM, pattern_shape_sequence=TEXTURAS,
        title=f"Inscriptos por país (top {len(g_p)})",
    )
    fig.update_traces(textposition="outside", cliponaxis=False,
                      textfont=dict(color=TINTA),
                  marker=dict(pattern=TRAMA, line=BORDE_BARRA))
    fig.update_layout(showlegend=False, yaxis=dict(categoryorder="total ascending", title=""))
    mostrar(fig)

# --- Rango de edad ---
with col4:
    g_r = (f[COL_RANGO].fillna("Sin edad").value_counts()
           .reindex([r for r in ORDEN_RANGO if r in set(f[COL_RANGO].dropna())]
                    + (["Sin edad"] if f[COL_RANGO].isna().any() else []))
           .dropna().reset_index())
    g_r.columns = [COL_RANGO, "Inscriptos"]
    g_r["Leyenda"] = (g_r[COL_RANGO].astype(str) + " años ("
                      + g_r["Inscriptos"].map(miles) + ")")
    fig = px.pie(
        g_r, names="Leyenda", values="Inscriptos", hole=0.45,
        color="Leyenda",
        color_discrete_map={
            r["Leyenda"]: COLOR_RANGO.get(r[COL_RANGO], "#8FA3C8")
            for _, r in g_r.iterrows()
        },
        title="Inscriptos por rango de edad",
    )
    fig.update_traces(textinfo="none",
                      marker=dict(line=dict(color=PANEL, width=2)))
    mostrar(fig)

# --- Heatmap: País x Especialidad ---
top_pais = f[COL_PAIS_NOM].value_counts().head(top_n).index
sub = f[f[COL_PAIS_NOM].isin(top_pais)]
cruce = pd.crosstab(sub[COL_PAIS_NOM], sub[COL_SKILL])
cruce = cruce.loc[cruce.sum(axis=1).sort_values(ascending=False).index]
cruce = cruce[cruce.sum().sort_values(ascending=False).index]

fig = go.Figure(go.Heatmap(
    z=cruce.values, x=cruce.columns, y=cruce.index,
    text=cruce.values, texttemplate="%{text}", textfont=dict(color=AZUL),
    hovertemplate="País: %{y}<br>Skill: %{x}<br>Inscriptos: %{z}<extra></extra>",
    colorscale=ESCALA_HEATMAP, colorbar=dict(title="Inscriptos"),
    xgap=2, ygap=2,
))
fig.update_layout(
    title=f"Heatmap: inscriptos por país y especialidad (top {len(cruce)} países)",
    height=max(380, 28 * len(cruce) + 220),
    yaxis=dict(autorange="reversed", title="País"),
    xaxis=dict(tickangle=-30, title="Especialidad (skill)"),
)
mostrar(fig)

# ------------------------------------------------------------------
# 7) Tabla (con los filtros aplicados)
# ------------------------------------------------------------------
st.subheader("Tabla de inscriptos")
vista = f.copy()
vista[COL_INSC] = vista[COL_INSC].dt.strftime("%d/%m/%Y %H:%M")
vista[COL_REG] = vista[COL_REG].dt.strftime("%d/%m/%Y")
st.dataframe(vista)

# ------------------------------------------------------------------
# 8) Insights (se calculan con los datos filtrados)
# ------------------------------------------------------------------
st.subheader("💡 Insights")
st.caption("Se recalculan con los filtros que tengas aplicados.")

ins = []

# Especialidad principal
vs_skill = f[COL_SKILL].value_counts()
if len(vs_skill) > 1:
    txt = (f"<b>Especialidad principal:</b> «{vs_skill.index[0]}» concentra el "
           f"{pct(vs_skill.iloc[0], total)} de los inscriptos "
           f"({miles(vs_skill.iloc[0])} de {miles(total)})")
    if len(vs_skill) >= 3:
        txt += (f"; las 3 principales ({', '.join(vs_skill.head(3).index)}) suman "
                f"el {pct(vs_skill.head(3).sum(), total)}")
    ins.append(txt + ".")

# Concentración geográfica
vp = f[COL_PAIS_NOM].value_counts()
if len(vp) > 1:
    txt = (f"<b>Concentración geográfica:</b> {vp.index[0]} aporta el "
           f"{pct(vp.iloc[0], total)} de los inscriptos")
    if len(vp) >= 3:
        txt += (f"; los 3 principales ({', '.join(vp.head(3).index)}) suman el "
                f"{pct(vp.head(3).sum(), total)} y hay {miles(len(vp))} países en total")
    ins.append(txt + ".")

# Edad
if f[COL_EDAD].notna().any():
    rango_top = f[COL_RANGO].value_counts()
    txt = (f"<b>Perfil de edad:</b> el promedio es de {dec(f[COL_EDAD].mean())} años "
           f"(mediana {f[COL_EDAD].median():.0f}, mínimo {int(f[COL_EDAD].min())} y "
           f"máximo {int(f[COL_EDAD].max())})")
    if len(rango_top):
        txt += (f"; el grupo más numeroso es el de {rango_top.index[0]} años, "
                f"con el {pct(rango_top.iloc[0], total)} del total")
    ins.append(txt + ".")

# Antigüedad en la plataforma
if len(antig_ok) and segmentados.any():
    n_seg = int(segmentados.sum())
    n_rec = int((f[COL_SEGMENTO] == "Recién llegado").sum())
    n_vet = int((f[COL_SEGMENTO] == "Veterano").sum())
    txt = (
        f"<b>Antigüedad al inscribirse:</b> la mitad de los inscriptos llevaba "
        f"{antig_ok.median():.0f} día(s) o menos en Workana y el promedio es de "
        f"{dec(antig_ok.mean())} días. El {pct(n_rec, n_seg)} se anotó dentro de su "
        f"primer mes en la plataforma y el {pct(n_vet, n_seg)} ya llevaba más de un año."
    )
    if antig_ok.mean() > 1.5 * antig_ok.median():
        txt += (" El promedio supera a la mediana porque unos pocos perfiles muy "
                "antiguos lo empujan hacia arriba.")
    ins.append(txt)

    # Skill y país con más antigüedad (solo categorías con suficientes casos)
    for col, minimo, nombre in [(COL_SKILL, 10, "Especialidad más establecida"),
                                (COL_PAIS_NOM, 10, "País con perfiles más antiguos")]:
        g = f[f[COL_ANTIG] >= 0].groupby(col)[COL_ANTIG].agg(["mean", "count"])
        g = g[g["count"] >= minimo]
        if len(g) > 1:
            top = g["mean"].idxmax()
            ins.append(
                f"<b>{nombre}:</b> «{top}» llega al programa con {dec(g.loc[top, 'mean'])} "
                f"días de antigüedad promedio (el total es {dec(antig_ok.mean())}). "
                f"Se consideran solo categorías con al menos {minimo} inscriptos."
            )

# Momentos de mayor demanda
dia_pico = diario.idxmax()
meses = f[COL_INSC].dt.to_period("M").value_counts()
mes_pico = meses.idxmax()
ins.append(
    f"<b>Momentos de mayor demanda:</b> el día con más inscripciones fue el "
    f"{dia_pico.strftime('%d/%m/%Y')} ({miles(diario.max())}) y el mes más cargado "
    f"fue {MESES[mes_pico.month - 1]} de {mes_pico.year} "
    f"({miles(meses.max())}, {pct(meses.max(), total)} del total)."
)

# Franja horaria de inscripción
horas = f[COL_INSC].dt.hour
if horas.notna().any():
    tarde = int(horas.between(12, 19).sum())
    ins.append(
        f"<b>Horario de inscripción:</b> la hora más frecuente es "
        f"{int(horas.mode().iloc[0]):02d}:00 y el {pct(tarde, total)} de las "
        f"inscripciones se registra entre las 12 y las 19 h."
    )

# Calidad de datos
n_rev = int((f[COL_SEGMENTO] == "Revisar fecha").sum())
n_sin_skill = int((f[COL_SKILL] == "Sin skill").sum())
n_sin_edad = int(f[COL_EDAD].isna().sum())
n_dup = int(f[COL_USER].duplicated().sum())
n_pais_raro = int((~f[COL_PAIS].isin(PAISES)).sum())
alertas = []
if n_rev:
    alertas.append(f"{miles(n_rev)} con fecha de registro posterior a la de inscripción")
if n_sin_skill:
    alertas.append(f"{miles(n_sin_skill)} sin skill")
if n_sin_edad:
    alertas.append(f"{miles(n_sin_edad)} sin edad")
if n_dup:
    alertas.append(f"{miles(n_dup)} user_id repetidos")
if n_pais_raro:
    alertas.append(f"{miles(n_pais_raro)} con código de país sin nombre asignado")
if alertas:
    ins.append("<b>Calidad de datos a revisar:</b> " + "; ".join(alertas) + ".")
else:
    ins.append("<b>Calidad de datos:</b> sin nulos, sin user_id repetidos y sin "
               "fechas inconsistentes en la selección actual.")

caja("<ul style='margin:0; padding-left:20px;'>"
     + "".join(f"<li style='margin-bottom:8px;'>{x}</li>" for x in ins)
     + "</ul>")
