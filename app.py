
"""
================================================================================
DASHBOARD PROFESIONAL DE PERFORMANCE DE LÍNEA - STREAMLIT CLOUD
================================================================================
Aplicación institucional para análisis de paradas, disponibilidad, MTBF y MTTR.
Compatible con archivos Excel estándar desde SharePoint o carga local.

Autor: Sistema de Manufactura Inteligente
Versión: 3.0.0
Fecha: 2026
================================================================================
"""

# ==============================================================================
# IMPORTACIÓN DE LIBRERÍAS
# ==============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import calendar
import json
import base64
from io import BytesIO
import warnings
import re
import requests
from urllib.parse import urlparse
import time
import math

# Suprimir warnings para presentación limpia
warnings.filterwarnings('ignore')

# Configuración de página - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(
    page_title="Dashboard Performance de Línea | Gerencia",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Dashboard Profesional de Performance de Línea v3.0.0 - Sistema de Manufactura Inteligente"
    }
)

# ==============================================================================
# CSS PERSONALIZADO INSTITUCIONAL
# ==============================================================================
st.markdown("""
<style>
    /* ================================================================ */
    /* TEMA CORPORATIVO INSTITUCIONAL                                     */
    /* ================================================================ */

    /* Fuentes y base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }

    /* ================================================================ */
    /* HEADER INSTITUCIONAL                                              */
    /* ================================================================ */
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2c5282 50%, #1e3a5f 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3);
        border-left: 6px solid #e67e22;
    }

    .main-header h1 {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }

    .main-header h2 {
        color: #94a3b8 !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        margin: 0.5rem 0 0 0 !important;
    }

    .main-header .badge {
        background: #e67e22;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
    }

    /* ================================================================ */
    /* KPI CARDS                                                          */
    /* ================================================================ */
    .kpi-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .kpi-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }

    .kpi-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #e67e22, #d35400);
    }

    .kpi-container.green::before {
        background: linear-gradient(180deg, #27ae60, #219a52);
    }

    .kpi-container.blue::before {
        background: linear-gradient(180deg, #3498db, #2980b9);
    }

    .kpi-container.red::before {
        background: linear-gradient(180deg, #e74c3c, #c0392b);
    }

    .kpi-container.purple::before {
        background: linear-gradient(180deg, #9b59b6, #8e44ad);
    }

    .kpi-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1e293b;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }

    .kpi-delta {
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .kpi-delta.positive {
        color: #27ae60;
    }

    .kpi-delta.negative {
        color: #e74c3c;
    }

    .kpi-subtext {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.5rem;
    }

    /* ================================================================ */
    /* SECCIONES Y TARJETAS                                              */
    /* ================================================================ */
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #e67e22;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .section-title .icon {
        font-size: 1.5rem;
    }

    /* ================================================================ */
    /* TABLAS ESTILIZADAS                                                */
    /* ================================================================ */
    .styled-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.9rem;
    }

    .styled-table th {
        background: linear-gradient(90deg, #1e3a5f, #2c5282);
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }

    .styled-table td {
        padding: 12px;
        border-bottom: 1px solid #e2e8f0;
        color: #334155;
    }

    .styled-table tr:hover td {
        background: #f8fafc;
    }

    /* ================================================================ */
    /* SIDEBAR PERSONALIZADA                                             */
    /* ================================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }

    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e1;
    }

    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    /* ================================================================ */
    /* BOTONES Y CONTROLES                                               */
    /* ================================================================ */
    .stButton>button {
        background: linear-gradient(90deg, #e67e22, #d35400);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #d35400, #e67e22);
        box-shadow: 0 4px 15px rgba(230, 126, 34, 0.4);
        transform: translateY(-2px);
    }

    /* ================================================================ */
    /* ALERTAS Y MENSAJES                                                */
    /* ================================================================ */
    .alert-box {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        font-weight: 500;
    }

    .alert-box.info {
        background: #eff6ff;
        border-color: #3b82f6;
        color: #1e40af;
    }

    .alert-box.success {
        background: #f0fdf4;
        border-color: #22c55e;
        color: #166534;
    }

    .alert-box.warning {
        background: #fffbeb;
        border-color: #f59e0b;
        color: #92400e;
    }

    .alert-box.error {
        background: #fef2f2;
        border-color: #ef4444;
        color: #991b1b;
    }

    /* ================================================================ */
    /* ANIMACIONES Y EFECTOS                                             */
    /* ================================================================ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-in {
        animation: fadeIn 0.6s ease-out forwards;
    }

    /* ================================================================ */
    /* FOOTER INSTITUCIONAL                                              */
    /* ================================================================ */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }

    .footer strong {
        color: #1e3a5f;
    }

    /* ================================================================ */
    /* TABS PERSONALIZADOS                                               */
    /* ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #64748b;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #1e3a5f !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* ================================================================ */
    /* PROGRESS BARS Y GAUGES                                            */
    /* ================================================================ */
    .progress-container {
        background: #e2e8f0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 8px 0;
    }

    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    .progress-bar.green { background: linear-gradient(90deg, #27ae60, #2ecc71); }
    .progress-bar.yellow { background: linear-gradient(90deg, #f39c12, #f1c40f); }
    .progress-bar.red { background: linear-gradient(90deg, #e74c3c, #c0392b); }

    /* ================================================================ */
    /* DIVISORES Y SEPARADORES                                           */
    /* ================================================================ */
    .divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #e67e22, transparent);
        margin: 2rem 0;
        border-radius: 2px;
    }

    /* ================================================================ */
    /* RESPONSIVE AJUSTES                                                */
    /* ================================================================ */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        .kpi-value {
            font-size: 1.8rem;
        }
    }

    /* Ocultar elementos de Streamlit por defecto */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


# ==============================================================================
# CONSTANTES Y CONFIGURACIONES GLOBALES
# ==============================================================================
COLUMNAS_ESPERADAS = {
    'fecha': ['FECHA', 'Fecha', 'fecha', 'DATE', 'Date', 'FCH', 'DIA'],
    'turno': ['TURNO', 'Turno', 'turno', 'SHIFT', 'Shift'],
    'aviso': ['AVISO', 'Aviso', 'aviso', 'NOTICE', 'ID', 'CODIGO'],
    'tiempo': ['TIEMPO (Minutos)', 'TIEMPO', 'Tiempo', 'tiempo', 'TIME', 'Time', 
               'DURACION', 'Duracion', 'MINUTOS', 'Minutos', 'minutos'],
    'maquina': ['MAQUINA', 'Maquina', 'maquina', 'MACHINE', 'Machine', 'EQUIPO', 'Equipo'],
    'estacion': ['ESTACIÓN', 'ESTACION', 'Estacion', 'estacion', 'STATION', 'Station', 'AREA', 'Area'],
    'sistema': ['SISTEMA', 'Sistema', 'sistema', 'SYSTEM', 'System'],
    'parte': ['PARTE', 'Parte', 'parte', 'PART', 'Part', 'COMPONENTE', 'Componente'],
    'causa': ['CAUSA DE AVERÍA', 'CAUSA DE AVERIA', 'Causa de averia', 'causa', 
              'CAUSA', 'Causa', 'CAUSE', 'Cause', 'MODO FALLA', 'Modo Falla'],
    'problema': ['DESCRIPCIÓN DEL PROBLEMA', 'DESCRIPCION DEL PROBLEMA', 'Descripcion del problema',
                 'problema', 'PROBLEMA', 'Problema', 'FALLA', 'Falla', 'DESCRIPCION'],
    'trabajo': ['DESCRIPCIÓN DEL TRABAJO', 'DESCRIPCION DEL TRABAJO', 'Descripcion del trabajo',
                'trabajo', 'TRABAJO', 'Trabajo', 'ACCION', 'Accion', 'SOLUCION']
}

COLORES_INSTITUCIONALES = {
    'primario': '#1e3a5f',
    'secundario': '#2c5282',
    'acento': '#e67e22',
    'exito': '#27ae60',
    'peligro': '#e74c3c',
    'advertencia': '#f39c12',
    'info': '#3498db',
    'morado': '#9b59b6',
    'gris': '#95a5a6',
    'paleta': ['#1e3a5f', '#e67e22', '#27ae60', '#e74c3c', '#9b59b6', 
               '#3498db', '#f39c12', '#1abc9c', '#34495e', '#e91e63']
}

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

DIAS_ES = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
           4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}


# ==============================================================================
# FUNCIONES DE UTILIDAD Y AYUDA
# ==============================================================================
def detectar_columnas(df):
    """
    Detecta automáticamente las columnas del DataFrame basándose en
    variantes conocidas de nombres de columnas estándar.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con los datos cargados

    Retorna:
    --------
    dict : Mapeo de nombres estándar a nombres reales del archivo
    """
    columnas_detectadas = {}
    columnas_originales = list(df.columns)
    columnas_lower = [c.strip().lower() for c in columnas_originales]

    for estandar, variantes in COLUMNAS_ESPERADAS.items():
        for var in variantes:
            var_lower = var.strip().lower()
            if var_lower in columnas_lower:
                idx = columnas_lower.index(var_lower)
                columnas_detectadas[estandar] = columnas_originales[idx]
                break

    return columnas_detectadas


def convertir_fecha_excel(valor):
    """
    Convierte valores de fecha de Excel (números seriales) a datetime.
    Maneja múltiples formatos de entrada.

    Parámetros:
    -----------
    valor : various
        Valor a convertir

    Retorna:
    --------
    datetime o NaT
    """
    if pd.isna(valor):
        return pd.NaT

    if isinstance(valor, (int, float)):
        # Fecha serial de Excel
        try:
            return pd.Timestamp('1899-12-30') + pd.Timedelta(days=int(valor))
        except:
            return pd.NaT

    if isinstance(valor, str):
        formatos = [
            '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y',
            '%d/%m/%y', '%Y/%m/%d', '%d.%m.%Y', '%Y%m%d'
        ]
        for fmt in formatos:
            try:
                return pd.to_datetime(valor, format=fmt)
            except:
                continue
        try:
            return pd.to_datetime(valor, dayfirst=True)
        except:
            return pd.NaT

    try:
        return pd.to_datetime(valor)
    except:
        return pd.NaT


def limpiar_dataframe(df, columnas_map):
    """
    Limpia y estandariza el DataFrame para análisis.
    Elimina filas de encabezado duplicadas, convierte tipos de datos,
    y normaliza valores categóricos.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame original
    columnas_map : dict
        Mapeo de columnas detectadas

    Retorna:
    --------
    pd.DataFrame : DataFrame limpio y listo para análisis
    """
    df_limpio = df.copy()

    # Eliminar filas que parecen ser encabezados repetidos
    primera_fila = df_limpio.iloc[0].astype(str).str.strip().str.lower()
    if any(primera_fila.isin(['fecha', 'turno', 'aviso', 'tiempo'])):
        df_limpio = df_limpio.iloc[1:].reset_index(drop=True)

    # Renombrar columnas a nombres estándar
    rename_map = {v: k for k, v in columnas_map.items()}
    df_limpio = df_limpio.rename(columns=rename_map)

    # Procesar columna de fecha
    if 'fecha' in df_limpio.columns:
        df_limpio['fecha'] = df_limpio['fecha'].apply(convertir_fecha_excel)
        df_limpio = df_limpio.dropna(subset=['fecha'])
        df_limpio['fecha'] = pd.to_datetime(df_limpio['fecha'], errors='coerce')

    # Procesar columna de tiempo
    if 'tiempo' in df_limpio.columns:
        df_limpio['tiempo'] = pd.to_numeric(df_limpio['tiempo'], errors='coerce')
        df_limpio = df_limpio[df_limpio['tiempo'] > 0]
        df_limpio['tiempo_horas'] = df_limpio['tiempo'] / 60.0

    # Limpiar columnas categóricas
    for col in ['turno', 'maquina', 'estacion', 'sistema', 'parte', 'causa']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace(['nan', 'None', ''], 'No Especificado')

    # Limpiar textos largos
    for col in ['problema', 'trabajo']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace(['nan', 'None'], '')

    # Crear columnas derivadas de fecha
    if 'fecha' in df_limpio.columns:
        df_limpio['año'] = df_limpio['fecha'].dt.year
        df_limpio['mes'] = df_limpio['fecha'].dt.month
        df_limpio['mes_nombre'] = df_limpio['mes'].map(MESES_ES)
        df_limpio['dia_semana'] = df_limpio['fecha'].dt.dayofweek
        df_limpio['dia_nombre'] = df_limpio['dia_semana'].map(DIAS_ES)
        df_limpio['semana'] = df_limpio['fecha'].dt.isocalendar().week
        df_limpio['dia_mes'] = df_limpio['fecha'].dt.day
        df_limpio['trimestre'] = df_limpio['fecha'].dt.quarter
        df_limpio['año_mes'] = df_limpio['fecha'].dt.to_period('M').astype(str)

    # Ordenar por fecha
    if 'fecha' in df_limpio.columns:
        df_limpio = df_limpio.sort_values('fecha').reset_index(drop=True)

    return df_limpio


def descargar_desde_url(url):
    """
    Descarga un archivo Excel desde una URL (SharePoint u otro servicio).
    Maneja autenticación básica y timeouts.

    Parámetros:
    -----------
    url : str
        URL del archivo Excel

    Retorna:
    --------
    BytesIO o None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Timeout de 30 segundos para archivos grandes
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            st.error(f"Error al descargar: Código HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        st.error("Tiempo de espera agotado. El archivo es muy grande o la conexión es lenta.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Error de conexión. Verifique la URL y su conexión a internet.")
        return None
    except Exception as e:
        st.error(f"Error al descargar archivo: {str(e)}")
        return None


def generar_excel_descarga(df, nombre_hoja='Reporte'):
    """
    Genera un archivo Excel en memoria para descarga.

    Parámetros:
    -----------
    df : pd.DataFrame
        Datos a exportar
    nombre_hoja : str
        Nombre de la hoja

    Retorna:
    --------
    bytes : Contenido del archivo Excel
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre_hoja, index=False)

        # Autoajustar columnas
        worksheet = writer.sheets[nombre_hoja]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)
    return output.getvalue()


def calcular_kpi_color(valor, tipo='disponibilidad'):
    """
    Determina el color de un KPI basado en umbrales estándar de la industria.

    Parámetros:
    -----------
    valor : float
        Valor del KPI
    tipo : str
        Tipo de KPI ('disponibilidad', 'mtbf', 'mttr', 'oee')

    Retorna:
    --------
    str : Código de color
    """
    if tipo == 'disponibilidad':
        if valor >= 95:
            return 'green'
        elif valor >= 85:
            return 'yellow'
        else:
            return 'red'
    elif tipo == 'mtbf':
        if valor >= 8:
            return 'green'
        elif valor >= 4:
            return 'yellow'
        else:
            return 'red'
    elif tipo == 'mttr':
        if valor <= 1:
            return 'green'
        elif valor <= 3:
            return 'yellow'
        else:
            return 'red'
    elif tipo == 'oee':
        if valor >= 85:
            return 'green'
        elif valor >= 60:
            return 'yellow'
        else:
            return 'red'
    return 'blue'


def formato_numero(valor, decimales=2, sufijo=''):
    """
    Formatea un número para presentación en KPIs.

    Parámetros:
    -----------
    valor : float
        Número a formatear
    decimales : int
        Cantidad de decimales
    sufijo : str
        Sufijo a agregar

    Retorna:
    --------
    str : Número formateado
    """
    if pd.isna(valor) or valor == 0:
        return f"0{sufijo}"

    if valor >= 1000000:
        return f"{valor/1000000:.{decimales}f}M{sufijo}"
    elif valor >= 1000:
        return f"{valor/1000:.{decimales}f}K{sufijo}"
    else:
        return f"{valor:.{decimales}f}{sufijo}"


def crear_gauge_chart(valor, titulo, maximo=100, color_primario=None):
    """
    Crea un gráfico gauge (medidor) profesional con Plotly.

    Parámetros:
    -----------
    valor : float
        Valor actual
    titulo : str
        Título del gauge
    maximo : float
        Valor máximo
    color_primario : str
        Color principal

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    if color_primario is None:
        color_primario = COLORES_INSTITUCIONALES['primario']

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo, 'font': {'size': 18, 'color': '#1e293b', 'family': 'Inter'}},
        number={'font': {'size': 28, 'color': '#1e293b', 'family': 'Inter'}, 
                'suffix': '%' if maximo == 100 else ''},
        gauge={
            'axis': {'range': [0, maximo], 'tickwidth': 1, 'tickcolor': '#64748b'},
            'bar': {'color': color_primario, 'thickness': 0.75},
            'bgcolor': '#f1f5f9',
            'borderwidth': 2,
            'bordercolor': '#e2e8f0',
            'steps': [
                {'range': [0, maximo*0.33], 'color': '#fef2f2'},
                {'range': [maximo*0.33, maximo*0.66], 'color': '#fffbeb'},
                {'range': [maximo*0.66, maximo], 'color': '#f0fdf4'}
            ],
            'threshold': {
                'line': {'color': COLORES_INSTITUCIONALES['peligro'], 'width': 4},
                'thickness': 0.8,
                'value': maximo * 0.85
            }
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'}
    )

    return fig


def crear_pareto(df, columna_categoria, columna_valor, titulo, top_n=15, color_barras=None):
    """
    Crea un gráfico de Pareto profesional con barras y línea acumulada.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    columna_categoria : str
        Columna para categorías (eje X)
    columna_valor : str
        Columna para valores (barras)
    titulo : str
        Título del gráfico
    top_n : int
        Cantidad de categorías a mostrar
    color_barras : str
        Color de las barras

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    if color_barras is None:
        color_barras = COLORES_INSTITUCIONALES['acento']

    # Agrupar y ordenar
    pareto_data = df.groupby(columna_categoria)[columna_valor].sum().reset_index()
    pareto_data = pareto_data.sort_values(columna_valor, ascending=False).head(top_n)
    pareto_data['acumulado'] = pareto_data[columna_valor].cumsum()
    pareto_data['porcentaje_acumulado'] = (pareto_data['acumulado'] / pareto_data[columna_valor].sum()) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras
    fig.add_trace(
        go.Bar(
            x=pareto_data[columna_categoria],
            y=pareto_data[columna_valor],
            name='Tiempo (min)',
            marker_color=color_barras,
            text=pareto_data[columna_valor].round(1),
            textposition='outside',
            textfont={'size': 11, 'color': '#1e293b'},
            hovertemplate='<b>%{x}</b><br>Tiempo: %{y:.1f} min<extra></extra>'
        ),
        secondary_y=False
    )

    # Línea acumulada
    fig.add_trace(
        go.Scatter(
            x=pareto_data[columna_categoria],
            y=pareto_data['porcentaje_acumulado'],
            name='% Acumulado',
            mode='lines+markers+text',
            line={'color': COLORES_INSTITUCIONALES['primario'], 'width': 3},
            marker={'size': 8, 'color': COLORES_INSTITUCIONALES['primario']},
            text=[f'{v:.1f}%' for v in pareto_data['porcentaje_acumulado']],
            textposition='top center',
            textfont={'size': 10, 'color': COLORES_INSTITUCIONALES['primario']},
            hovertemplate='<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True
    )

    # Línea de referencia 80%
    fig.add_hline(
        y=80, line_dash="dash", line_color="#e74c3c", line_width=2,
        secondary_y=True,
        annotation_text="Regla 80/20", 
        annotation_position="right",
        annotation_font_color="#e74c3c"
    )

    fig.update_layout(
        title={
            'text': f"<b>{titulo}</b>",
            'font': {'size': 20, 'color': '#1e293b', 'family': 'Inter'},
            'x': 0.5
        },
        xaxis_title="",
        yaxis_title="Tiempo Total (minutos)",
        yaxis2_title="Porcentaje Acumulado (%)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(l=60, r=60, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_xaxes(
        tickangle=-35, 
        tickfont={'size': 11},
        gridcolor='#f1f5f9'
    )
    fig.update_yaxes(
        gridcolor='#f1f5f9',
        secondary_y=False
    )
    fig.update_yaxes(
        range=[0, 105],
        ticksuffix='%',
        secondary_y=True
    )

    return fig


def crear_tendencia_temporal(df, agrupacion='D', titulo="Tendencia Temporal"):
    """
    Crea gráfico de tendencia temporal con múltiples métricas.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    agrupacion : str
        Frecuencia de agrupación ('D' día, 'W' semana, 'M' mes)
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    df_temp = df.copy()
    df_temp['periodo'] = df_temp['fecha'].dt.to_period(agrupacion)

    resumen = df_temp.groupby('periodo').agg({
        'tiempo': ['sum', 'count', 'mean'],
        'fecha': 'nunique'
    }).reset_index()

    resumen.columns = ['periodo', 'tiempo_total', 'cantidad_paradas', 'tiempo_promedio', 'dias_activos']
    resumen['periodo_str'] = resumen['periodo'].astype(str)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
        subplot_titles=('Tiempo Total de Paradas (min)', 'Cantidad de Paradas')
    )

    # Gráfico superior - Tiempo total
    fig.add_trace(
        go.Bar(
            x=resumen['periodo_str'],
            y=resumen['tiempo_total'],
            name='Tiempo Total',
            marker_color=COLORES_INSTITUCIONALES['acento'],
            text=resumen['tiempo_total'].round(0).astype(int),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Tiempo Total: %{y:.0f} min<extra></extra>'
        ),
        row=1, col=1
    )

    # Línea de tendencia
    fig.add_trace(
        go.Scatter(
            x=resumen['periodo_str'],
            y=resumen['tiempo_total'],
            mode='lines',
            line={'color': COLORES_INSTITUCIONALES['primario'], 'width': 2, 'dash': 'dot'},
            name='Tendencia',
            showlegend=False
        ),
        row=1, col=1
    )

    # Gráfico inferior - Cantidad de paradas
    fig.add_trace(
        go.Bar(
            x=resumen['periodo_str'],
            y=resumen['cantidad_paradas'],
            name='N° Paradas',
            marker_color=COLORES_INSTITUCIONALES['info'],
            text=resumen['cantidad_paradas'].astype(int),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Paradas: %{y}<extra></extra>'
        ),
        row=2, col=1
    )

    fig.update_layout(
        title={
            'text': f"<b>{titulo}</b>",
            'font': {'size': 20, 'color': '#1e293b', 'family': 'Inter'},
            'x': 0.5
        },
        height=600,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        hovermode='x unified',
        margin=dict(l=60, r=40, t=100, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_xaxes(tickangle=-45, row=2, col=1)
    fig.update_yaxes(gridcolor='#f1f5f9', row=1, col=1)
    fig.update_yaxes(gridcolor='#f1f5f9', row=2, col=1)

    return fig


def crear_heatmap_calendario(df, columna_valor='tiempo', titulo="Mapa de Calor - Calendario"):
    """
    Crea un heatmap de calendario mostrando intensidad por día.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    columna_valor : str
        Columna a sumar
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    df_cal = df.copy()
    df_cal['dia_semana'] = df_cal['fecha'].dt.dayofweek
    df_cal['semana_año'] = df_cal['fecha'].dt.isocalendar().week
    df_cal['mes'] = df_cal['fecha'].dt.month

    pivot = df_cal.groupby(['semana_año', 'dia_semana'])[columna_valor].sum().reset_index()
    pivot_pivot = pivot.pivot(index='semana_año', columns='dia_semana', values=columna_valor).fillna(0)

    dias_labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    fig = go.Figure(data=go.Heatmap(
        z=pivot_pivot.values,
        x=dias_labels,
        y=[f"Sem {s}" for s in pivot_pivot.index],
        colorscale=[
            [0, '#f0fdf4'],
            [0.2, '#fef3c7'],
            [0.5, '#fdba74'],
            [0.8, '#ef4444'],
            [1, '#7f1d1d']
        ],
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.0f} min<extra></extra>',
        colorbar=dict(title="Minutos", titleside="right")
    ))

    fig.update_layout(
        title={
            'text': f"<b>{titulo}</b>",
            'font': {'size': 18, 'color': '#1e293b'},
            'x': 0.5
        },
        height=500,
        template='plotly_white',
        margin=dict(l=60, r=40, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def crear_analisis_caja(df, columna_categoria, columna_valor, titulo):
    """
    Crea gráfico de caja (boxplot) para análisis de distribución.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    columna_categoria : str
        Columna categórica
    columna_valor : str
        Columna numérica
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    categorias = df[columna_categoria].value_counts().head(10).index.tolist()
    df_filtrado = df[df[columna_categoria].isin(categorias)]

    fig = px.box(
        df_filtrado,
        x=columna_categoria,
        y=columna_valor,
        color=columna_categoria,
        color_discrete_sequence=COLORES_INSTITUCIONALES['paleta'],
        title=titulo,
        labels={columna_categoria: '', columna_valor: 'Tiempo (minutos)'}
    )

    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=450,
        template='plotly_white',
        showlegend=False,
        margin=dict(l=60, r=40, t=60, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-35
    )

    return fig


def calcular_mtbf_mttr_disponibilidad(df, minutos_turno=480, turnos_por_dia=2):
    """
    Calcula métricas clave de mantenimiento: MTBF, MTTR y Disponibilidad.

    Fórmulas:
    - MTBF (Mean Time Between Failures) = Tiempo total operativo / Número de fallas
    - MTTR (Mean Time To Repair) = Tiempo total de reparación / Número de fallas
    - Disponibilidad = MTBF / (MTBF + MTTR) * 100

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos de paradas
    minutos_turno : int
        Duración de un turno en minutos (default 480 = 8 horas)
    turnos_por_dia : int
        Cantidad de turnos por día

    Retorna:
    --------
    dict : Diccionario con métricas calculadas
    """
    if df.empty:
        return {
            'mtbf_horas': 0,
            'mttr_horas': 0,
            'mtbf_minutos': 0,
            'mttr_minutos': 0,
            'disponibilidad': 0,
            'tiempo_total_paradas': 0,
            'tiempo_operativo_total': 0,
            'total_fallas': 0,
            'tiempo_promedio_parada': 0
        }

    # Calcular rango de fechas
    fecha_inicio = df['fecha'].min()
    fecha_fin = df['fecha'].max()
    dias_totales = (fecha_fin - fecha_inicio).days + 1

    # Tiempo total programado (minutos)
    tiempo_programado = dias_totales * turnos_por_dia * minutos_turno

    # Tiempo total de paradas
    tiempo_total_paradas = df['tiempo'].sum()

    # Tiempo operativo = Tiempo programado - Tiempo paradas
    tiempo_operativo = max(0, tiempo_programado - tiempo_total_paradas)

    # Total de fallas (eventos)
    total_fallas = len(df)

    # MTBF en minutos y horas
    if total_fallas > 0:
        mtbf_minutos = tiempo_operativo / total_fallas
        mttr_minutos = tiempo_total_paradas / total_fallas
    else:
        mtbf_minutos = tiempo_operativo
        mttr_minutos = 0

    mtbf_horas = mtbf_minutos / 60.0
    mttr_horas = mttr_minutos / 60.0

    # Disponibilidad
    if (mtbf_minutos + mttr_minutos) > 0:
        disponibilidad = (mtbf_minutos / (mtbf_minutos + mttr_minutos)) * 100
    else:
        disponibilidad = 100.0

    # Tiempo promedio de parada
    tiempo_promedio = df['tiempo'].mean() if total_fallas > 0 else 0

    return {
        'mtbf_horas': mtbf_horas,
        'mttr_horas': mttr_horas,
        'mtbf_minutos': mtbf_minutos,
        'mttr_minutos': mttr_minutos,
        'disponibilidad': disponibilidad,
        'tiempo_total_paradas': tiempo_total_paradas,
        'tiempo_operativo_total': tiempo_operativo,
        'total_fallas': total_fallas,
        'tiempo_promedio_parada': tiempo_promedio,
        'dias_analizados': dias_totales,
        'tiempo_programado': tiempo_programado
    }


def analisis_texto_frecuencia(df, columna_texto, top_n=20):
    """
    Realiza análisis de frecuencia de palabras en descripciones.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    columna_texto : str
        Columna de texto a analizar
    top_n : int
        Cantidad de palabras principales

    Retorna:
    --------
    pd.DataFrame : Frecuencia de palabras
    """
    if columna_texto not in df.columns:
        return pd.DataFrame()

    textos = df[columna_texto].dropna().astype(str)
    textos = textos[textos.str.len() > 3]

    if textos.empty:
        return pd.DataFrame()

    # Palabras a excluir (stopwords en español)
    stopwords = {
        'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para',
        'con', 'no', 'una', 'su', 'al', 'lo', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este',
        'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 'me',
        'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos',
        'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto',
        'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto',
        'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar',
        'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus',
        'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo',
        'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra',
        'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas',
        'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos',
        'estéis', 'estén', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán',
        'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas',
        'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos',
        'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras', 'estuviéramos', 'estuvierais',
        'estuvieran', 'estuviese', 'estuvieses', 'estuviésemos', 'estuvieseis', 'estuviesen',
        'estando', 'estado', 'estada', 'estados', 'estadas', 'estad', 'he', 'has', 'ha',
        'hemos', 'habéis', 'han', 'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré',
        'habrás', 'habrá', 'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos',
        'habríais', 'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube',
        'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
        'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos',
        'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
        'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seáis',
        'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería', 'serías',
        'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais', 'eran', 'fui',
        'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera', 'fueras', 'fuéramos',
        'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos', 'fueseis', 'fuesen', 'siendo',
        'sido', 'tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas',
        'tengamos', 'tengáis', 'tengan', 'tendré', 'tendrás', 'tendrá', 'tendremos',
        'tendréis', 'tendrán', 'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían',
        'tenía', 'tenías', 'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo',
        'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais',
        'tuvieran', 'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis', 'tuviesen', 'teniendo',
        'tenido', 'tenida', 'tenidos', 'tenidas', 'tened'
    }

    todas_palabras = []
    for texto in textos:
        # Limpiar y tokenizar
        palabras = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}\b', texto.lower())
        palabras = [p for p in palabras if p not in stopwords]
        todas_palabras.extend(palabras)

    if not todas_palabras:
        return pd.DataFrame()

    freq = pd.Series(todas_palabras).value_counts().head(top_n).reset_index()
    freq.columns = ['Palabra', 'Frecuencia']

    return freq


def crear_treemap(df, path, valores, titulo):
    """
    Crea un treemap jerárquico para análisis drill-down.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    path : list
        Lista de columnas para jerarquía
    valores : str
        Columna de valores
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.treemap(
        df,
        path=path,
        values=valores,
        color=valores,
        color_continuous_scale=[
            '#f0fdf4', '#dcfce7', '#86efac', '#22c55e', '#16a34a', '#15803d', '#166534'
        ],
        title=titulo
    )

    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(
        textfont={'size': 13, 'family': 'Inter'},
        hovertemplate='<b>%{label}</b><br>Tiempo: %{value:.0f} min<extra></extra>'
    )

    return fig


def crear_sunburst(df, path, valores, titulo):
    """
    Crea un gráfico sunburst para análisis jerárquico circular.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    path : list
        Lista de columnas para jerarquía
    valores : str
        Columna de valores
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.sunburst(
        df,
        path=path,
        values=valores,
        color=valores,
        color_continuous_scale='Blues',
        title=titulo
    )

    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=550,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(
        textfont={'size': 12, 'family': 'Inter'},
        hovertemplate='<b>%{label}</b><br>Tiempo: %{value:.0f} min<extra></extra>'
    )

    return fig


def crear_grafico_barras_apiladas(df, eje_x, eje_y, color, titulo):
    """
    Crea gráfico de barras apiladas para comparación cruzada.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    eje_x : str
        Columna eje X
    eje_y : str
        Columna eje Y
    color : str
        Columna para color/apilamiento
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.bar(
        df,
        x=eje_x,
        y=eje_y,
        color=color,
        title=titulo,
        color_discrete_sequence=COLORES_INSTITUCIONALES['paleta'],
        barmode='stack'
    )

    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=100, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-35
    )

    return fig


def crear_grafico_dispersion(df, x, y, color, size, titulo):
    """
    Crea gráfico de dispersión para análisis de correlación.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    x : str
        Columna eje X
    y : str
        Columna eje Y
    color : str
        Columna para color
    size : str
        Columna para tamaño de burbujas
    titulo : str
        Título del gráfico

    Retorna:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=titulo,
        color_discrete_sequence=COLORES_INSTITUCIONALES['paleta'],
        hover_data=[x, y, color, size]
    )

    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=100, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def resumen_ejecutivo_texto(df, metricas):
    """
    Genera un resumen ejecutivo en texto para presentación a gerencia.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos
    metricas : dict
        Diccionario con métricas calculadas

    Retorna:
    --------
    str : Texto de resumen ejecutivo
    """
    fecha_inicio = df['fecha'].min().strftime('%d/%m/%Y')
    fecha_fin = df['fecha'].max().strftime('%d/%m/%Y')

    # Top causas
    top_causas = df.groupby('causa')['tiempo'].sum().sort_values(ascending=False).head(3)

    # Top estaciones
    top_estaciones = df.groupby('estacion')['tiempo'].sum().sort_values(ascending=False).head(3)

    resumen = f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%); 
                padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
        <h3 style="color: #e67e22; margin-bottom: 1rem; font-size: 1.4rem;">📊 RESUMEN EJECUTIVO</h3>
        <p style="font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            Durante el período analizado (<strong>{fecha_inicio} - {fecha_fin}</strong>), 
            la línea registró <strong>{metricas['total_fallas']} eventos</strong> de parada 
            con un tiempo total de <strong>{metricas['tiempo_total_paradas']:.0f} minutos 
            ({metricas['tiempo_total_paradas']/60:.1f} horas)</strong>.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            La <strong>disponibilidad</strong> de la línea fue del <strong>{metricas['disponibilidad']:.2f}%</strong>, 
            con un <strong>MTBF de {metricas['mtbf_horas']:.2f} horas</strong> y un 
            <strong>MTTR de {metricas['mttr_horas']:.2f} horas</strong>.
        </p>
        <div style="margin-top: 1.5rem;">
            <h4 style="color: #e67e22; font-size: 1.1rem;">🔴 Principales Causas de Parada:</h4>
            <ul style="line-height: 1.8;">
    """

    for causa, tiempo in top_causas.items():
        pct = (tiempo / metricas['tiempo_total_paradas']) * 100
        resumen += f"                <li><strong>{causa}</strong>: {tiempo:.0f} min ({pct:.1f}% del total)</li>\n"

    resumen += """            </ul>
        </div>
        <div style="margin-top: 1.5rem;">
            <h4 style="color: #e67e22; font-size: 1.1rem;">⚙️ Estaciones Críticas:</h4>
            <ul style="line-height: 1.8;">
    """

    for est, tiempo in top_estaciones.items():
        pct = (tiempo / metricas['tiempo_total_paradas']) * 100
        resumen += f"                <li><strong>{est}</strong>: {tiempo:.0f} min ({pct:.1f}% del total)</li>\n"

    resumen += """            </ul>
        </div>
    </div>
    """

    return resumen


def render_kpi_card(label, valor, delta=None, delta_type="normal", 
                    subtext="", color_class="", icon="📊"):
    """
    Renderiza una tarjeta KPI HTML personalizada.

    Parámetros:
    -----------
    label : str
        Etiqueta del KPI
    valor : str
        Valor formateado
    delta : str, opcional
        Texto de variación
    delta_type : str
        Tipo de delta (normal, inverse)
    subtext : str
        Texto adicional
    color_class : str
        Clase de color CSS
    icon : str
        Emoji/icono

    Retorna:
    --------
    str : HTML de la tarjeta
    """
    delta_html = ""
    if delta:
        delta_class = "positive" if delta_type == "normal" else "negative"
        if float(delta.replace('%', '').replace('+', '').replace('-', '')) < 0:
            delta_class = "negative" if delta_type == "normal" else "positive"
        delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>'

    return f"""
    <div class="kpi-container {color_class} animate-in">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{valor}</div>
        {delta_html}
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """


# ==============================================================================
# INICIALIZACIÓN DE ESTADO DE SESIÓN
# ==============================================================================
if 'datos_cargados' not in st.session_state:
    st.session_state.datos_cargados = False
    st.session_state.df_original = None
    st.session_state.df_filtrado = None
    st.session_state.columnas_map = {}
    st.session_state.metricas = {}
    st.session_state.nombre_archivo = ""
    st.session_state.filtros_aplicados = False


# ==============================================================================
# SIDEBAR - PANEL DE CONTROL Y CONFIGURACIÓN
# ==============================================================================
with st.sidebar:
    # Logo y título del sidebar
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0; border-bottom: 1px solid #334155; margin-bottom: 2rem;">
        <h1 style="color: #e67e22; font-size: 1.8rem; margin: 0;">🏭</h1>
        <h2 style="color: #f8fafc; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 700;">
            PERFORMANCE LINE
        </h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 0.3rem 0 0 0;">
            Sistema de Análisis de Paradas
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #e67e22; font-size: 1rem; margin-bottom: 1rem;'>📥 CARGA DE DATOS</h3>", 
                unsafe_allow_html=True)

    # Selector de método de carga
    metodo_carga = st.radio(
        "Método de carga:",
        ["🔗 URL (SharePoint)", "📁 Archivo Local"],
        index=0,
        help="Seleccione si desea cargar desde una URL o subir un archivo local"
    )

    archivo_cargado = None

    if metodo_carga == "🔗 URL (SharePoint)":
        url_input = st.text_input(
            "URL del archivo Excel:",
            placeholder="https://.../Reporte.xlsx",
            help="Ingrese la URL directa del archivo Excel en SharePoint u otro servicio"
        )

        if st.button("🚀 CARGAR DESDE URL", use_container_width=True):
            if url_input and url_input.strip():
                with st.spinner("Descargando archivo..."):
                    archivo_cargado = descargar_desde_url(url_input.strip())
                    if archivo_cargado:
                        st.session_state.nombre_archivo = url_input.split('/')[-1] or "archivo_sharepoint.xlsx"
            else:
                st.warning("⚠️ Por favor ingrese una URL válida")

    else:
        archivo_subido = st.file_uploader(
            "Seleccione archivo Excel:",
            type=['xlsx', 'xls'],
            help="Archivo Excel con el consolidado de paradas"
        )
        if archivo_subido:
            archivo_cargado = BytesIO(archivo_subido.read())
            st.session_state.nombre_archivo = archivo_subido.name

    # Procesar archivo cargado
    if archivo_cargado is not None:
        try:
            with st.spinner("Procesando datos..."):
                # Leer todas las hojas
                xls = pd.ExcelFile(archivo_cargado)
                hojas_disponibles = xls.sheet_names

                # Seleccionar hoja (por defecto la primera que no sea de catálogos)
                hoja_seleccionada = hojas_disponibles[0]
                if len(hojas_disponibles) > 1:
                    hoja_seleccionada = st.selectbox(
                        "Hoja a analizar:",
                        hojas_disponibles,
                        index=0
                    )

                # Leer datos
                df_raw = pd.read_excel(archivo_cargado, sheet_name=hoja_seleccionada)

                # Detectar columnas
                columnas_detectadas = detectar_columnas(df_raw)

                if not columnas_detectadas:
                    st.error("❌ No se detectaron columnas válidas. Verifique el formato del archivo.")
                    st.info("Columnas esperadas: FECHA, TURNO, TIEMPO, MAQUINA, ESTACION, SISTEMA, PARTE, CAUSA")
                else:
                    # Limpiar datos
                    df_limpio = limpiar_dataframe(df_raw, columnas_detectadas)

                    if df_limpio.empty:
                        st.error("❌ No se encontraron datos válidos después de la limpieza.")
                    else:
                        st.session_state.df_original = df_limpio
                        st.session_state.df_filtrado = df_limpio.copy()
                        st.session_state.columnas_map = columnas_detectadas
                        st.session_state.datos_cargados = True
                        st.session_state.filtros_aplicados = False

                        # Calcular métricas iniciales
                        st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(df_limpio)

                        st.success(f"✅ Datos cargados exitosamente: {len(df_limpio)} registros")

                        # Mostrar columnas detectadas
                        with st.expander("📋 Columnas detectadas"):
                            for estandar, real in columnas_detectadas.items():
                                st.markdown(f"<span style='color: #27ae60;'>✓</span> **{estandar}**: `{real}`", 
                                          unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error al procesar archivo: {str(e)}")
            st.info("💡 Verifique que el archivo sea un Excel válido y esté accesible.")

    st.markdown("<hr style='border-color: #334155; margin: 2rem 0;'>", unsafe_allow_html=True)

    # Filtros dinámicos (solo si hay datos cargados)
    if st.session_state.datos_cargados:
        st.markdown("<h3 style='color: #e67e22; font-size: 1rem; margin-bottom: 1rem;'>🔍 FILTROS</h3>", 
                    unsafe_allow_html=True)

        df = st.session_state.df_original

        # Filtro de fechas
        if 'fecha' in df.columns:
            fecha_min = df['fecha'].min().date()
            fecha_max = df['fecha'].max().date()

            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Desde:", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
            with col2:
                fecha_fin = st.date_input("Hasta:", value=fecha_max, min_value=fecha_min, max_value=fecha_max)
        else:
            fecha_inicio = None
            fecha_fin = None

        # Filtros categóricos
        filtros = {}
        for col in ['turno', 'maquina', 'estacion', 'sistema', 'parte', 'causa']:
            if col in df.columns:
                opciones = ['Todos'] + sorted(df[col].unique().tolist())
                seleccion = st.multiselect(
                    f"{col.upper()}:",
                    options=opciones,
                    default=['Todos'],
                    help=f"Filtrar por {col}"
                )
                if 'Todos' not in seleccion:
                    filtros[col] = seleccion

        # Botón aplicar filtros
        if st.button("🎯 APLICAR FILTROS", use_container_width=True):
            df_filtrado = df.copy()

            # Aplicar filtro de fechas
            if fecha_inicio and fecha_fin:
                df_filtrado = df_filtrado[
                    (df_filtrado['fecha'].dt.date >= fecha_inicio) & 
                    (df_filtrado['fecha'].dt.date <= fecha_fin)
                ]

            # Aplicar filtros categóricos
            for col, valores in filtros.items():
                df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]

            st.session_state.df_filtrado = df_filtrado
            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(df_filtrado)
            st.session_state.filtros_aplicados = True
            st.success(f"✅ Filtros aplicados: {len(df_filtrado)} registros")
            st.rerun()

        # Botón limpiar filtros
        if st.button("🧹 LIMPIAR FILTROS", use_container_width=True):
            st.session_state.df_filtrado = st.session_state.df_original.copy()
            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(st.session_state.df_original)
            st.session_state.filtros_aplicados = False
            st.rerun()

    # Configuración de parámetros de turno
    st.markdown("<hr style='border-color: #334155; margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e67e22; font-size: 1rem; margin-bottom: 1rem;'>⚙️ CONFIGURACIÓN</h3>", 
                unsafe_allow_html=True)

    minutos_turno = st.number_input(
        "Minutos por turno:",
        min_value=1,
        max_value=1440,
        value=480,
        help="Duración de un turno en minutos (default: 480 = 8 horas)"
    )

    turnos_dia = st.number_input(
        "Turnos por día:",
        min_value=1,
        max_value=3,
        value=2,
        help="Cantidad de turnos operativos por día"
    )

    st.session_state.config_turno = {
        'minutos_turno': minutos_turno,
        'turnos_dia': turnos_dia
    }

    # Footer sidebar
    st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; padding: 1rem; 
                background: #0f172a; border-top: 1px solid #334155; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">
            v3.0.0 | Sistema de Manufactura Inteligente
        </p>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# CONTENIDO PRINCIPAL
# ==============================================================================

# Header institucional
st.markdown("""
<div class="main-header animate-in">
    <h1>🏭 Dashboard Performance de Línea</h1>
    <h2>Análisis de Paradas, Disponibilidad y Eficiencia para Toma de Decisiones Gerenciales</h2>
    <span class="badge">VERSIÓN INSTITUCIONAL 3.0</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# PANTALLA DE BIENVENIDA (SIN DATOS)
# ==============================================================================
if not st.session_state.datos_cargados:
    st.markdown("""
    <div class="section-card" style="text-align: center; padding: 4rem 2rem;">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">📊</h1>
        <h2 style="color: #1e3a5f; font-size: 1.8rem; margin-bottom: 1rem;">Bienvenido al Dashboard de Performance</h2>
        <p style="color: #64748b; font-size: 1.1rem; max-width: 600px; margin: 0 auto 2rem auto; line-height: 1.8;">
            Este sistema permite analizar el performance de líneas de producción mediante 
            el análisis de paradas, cálculo de disponibilidad, MTBF y MTTR. 
            Cargue un archivo Excel desde SharePoint o localmente para comenzar.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; max-width: 900px; margin: 0 auto;">
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #e67e22; font-size: 1.2rem;">📈 Pareto de Paradas</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Identifique las causas principales siguiendo la regla 80/20</p>
            </div>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #e67e22; font-size: 1.2rem;">⏱️ MTBF / MTTR</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Métricas clave de confiabilidad y mantenibilidad</p>
            </div>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #e67e22; font-size: 1.2rem;">📊 Disponibilidad</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Cálculo automático de disponibilidad de línea</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Instrucciones de formato
    with st.expander("📋 FORMATO ESPERADO DEL ARCHIVO EXCEL", expanded=False):
        st.markdown("""
        El archivo Excel debe contener las siguientes columnas (nombres flexibles):

        | Columna | Descripción | Ejemplo |
        |---------|-------------|---------|
        | **FECHA** | Fecha del evento | 15/01/2026 |
        | **TURNO** | Turno de operación | Turno 1, Turno 2 |
        | **AVISO** | Código de aviso (opcional) | 120253513 |
        | **TIEMPO** | Duración en minutos | 45 |
        | **MAQUINA** | Identificación de máquina | M 219 |
        | **ESTACIÓN** | Estación o área afectada | ST1- Alimentación |
        | **SISTEMA** | Sistema involucrado | Alimentador de casquillos |
        | **PARTE** | Parte o componente | Pin volteador |
        | **CAUSA** | Causa de la avería | Trabamiento |
        | **PROBLEMA** | Descripción del problema | Operador reporta fallas... |
        | **TRABAJO** | Descripción del trabajo realizado | Se verifica funcionamiento... |

        **Notas:**
        - Los nombres de columnas pueden variar (ej: "Tiempo", "TIEMPO", "Duracion")
        - El sistema detecta automáticamente las columnas
        - Se eliminan automáticamente filas de encabezado duplicadas
        - Las fechas en formato serial de Excel se convierten automáticamente
        """)

    st.stop()


# ==============================================================================
# DASHBOARD PRINCIPAL (CON DATOS CARGADOS)
# ==============================================================================
df = st.session_state.df_filtrado
metricas = st.session_state.metricas

# Recalcular métricas con configuración actual
if 'config_turno' in st.session_state:
    metricas = calcular_mtbf_mttr_disponibilidad(
        df,
        minutos_turno=st.session_state.config_turno['minutos_turno'],
        turnos_por_dia=st.session_state.config_turno['turnos_dia']
    )
    st.session_state.metricas = metricas

# Indicador de filtros activos
if st.session_state.filtros_aplicados:
    st.markdown(f"""
    <div class="alert-box info">
        <strong>🔍 Filtros activos:</strong> Mostrando {len(df)} de {len(st.session_state.df_original)} registros | 
        Período: {df['fecha'].min().strftime('%d/%m/%Y')} - {df['fecha'].max().strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 1: KPIs PRINCIPALES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🎯</span> INDICADORES CLAVE DE PERFORMANCE</div>", 
            unsafe_allow_html=True)

# Calcular colores según umbrales
color_disp = calcular_kpi_color(metricas['disponibilidad'], 'disponibilidad')
color_mtbf = calcular_kpi_color(metricas['mtbf_horas'], 'mtbf')
color_mttr = calcular_kpi_color(metricas['mttr_horas'], 'mttr')

# Tarjetas KPI
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(render_kpi_card(
        label="Disponibilidad",
        valor=f"{metricas['disponibilidad']:.2f}%",
        color_class=color_disp,
        icon="📈",
        subtext=f"Objetivo: ≥95% | {metricas['dias_analizados']} días analizados"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(render_kpi_card(
        label="MTBF",
        valor=f"{metricas['mtbf_horas']:.2f}h",
        color_class=color_mtbf,
        icon="⏱️",
        subtext="Mean Time Between Failures"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(render_kpi_card(
        label="MTTR",
        valor=f"{metricas['mttr_horas']:.2f}h",
        color_class=color_mttr,
        icon="🔧",
        subtext="Mean Time To Repair"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(render_kpi_card(
        label="Total Paradas",
        valor=f"{metricas['total_fallas']}",
        color_class="purple",
        icon="⚠️",
        subtext=f"{metricas['tiempo_total_paradas']:.0f} min totales"
    ), unsafe_allow_html=True)

with col5:
    tiempo_prom = metricas['tiempo_promedio_parada']
    st.markdown(render_kpi_card(
        label="Tiempo Promedio",
        valor=f"{tiempo_prom:.1f} min",
        color_class="blue",
        icon="⏲️",
        subtext="Por evento de parada"
    ), unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 2: GAUGES Y VISUALIZACIONES DE MÉTRICAS
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🎚️</span> MEDIDORES DE PERFORMANCE</div>", 
            unsafe_allow_html=True)

col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    fig_gauge_disp = crear_gauge_chart(
        metricas['disponibilidad'],
        "Disponibilidad (%)",
        maximo=100,
        color_primario=COLORES_INSTITUCIONALES['exito'] if metricas['disponibilidad'] >= 85 else COLORES_INSTITUCIONALES['acento']
    )
    st.plotly_chart(fig_gauge_disp, use_container_width=True, config={'displayModeBar': False})

with col_g2:
    # MTBF gauge (escala 0-12 horas)
    max_mtbf = max(12, metricas['mtbf_horas'] * 1.2)
    fig_gauge_mtbf = crear_gauge_chart(
        metricas['mtbf_horas'],
        "MTBF (horas)",
        maximo=max_mtbf,
        color_primario=COLORES_INSTITUCIONALES['info']
    )
    st.plotly_chart(fig_gauge_mtbf, use_container_width=True, config={'displayModeBar': False})

with col_g3:
    # MTTR gauge (escala 0-5 horas)
    max_mttr = max(5, metricas['mttr_horas'] * 1.2)
    fig_gauge_mttr = crear_gauge_chart(
        metricas['mttr_horas'],
        "MTTR (horas)",
        maximo=max_mttr,
        color_primario=COLORES_INSTITUCIONALES['peligro'] if metricas['mttr_horas'] > 2 else COLORES_INSTITUCIONALES['exito']
    )
    st.plotly_chart(fig_gauge_mttr, use_container_width=True, config={'displayModeBar': False})

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 3: RESUMEN EJECUTIVO
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📋</span> RESUMEN EJECUTIVO PARA GERENCIA</div>", 
            unsafe_allow_html=True)

st.markdown(resumen_ejecutivo_texto(df, metricas), unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 4: PARETO Y ANÁLISIS DE PARADAS
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📊</span> ANÁLISIS DE PARETO - PRINCIPALES CAUSAS</div>", 
            unsafe_allow_html=True)

# Tabs para diferentes dimensiones de Pareto
tab_pareto = st.tabs(["🔴 Por Causa", "⚙️ Por Estación", "🔧 Por Sistema", "📦 Por Parte", "🕐 Por Turno"])

with tab_pareto[0]:
    if 'causa' in df.columns:
        fig_pareto_causa = crear_pareto(
            df, 'causa', 'tiempo',
            "Pareto de Paradas por Causa de Avería",
            top_n=15,
            color_barras=COLORES_INSTITUCIONALES['peligro']
        )
        st.plotly_chart(fig_pareto_causa, use_container_width=True)

        # Tabla de detalle
        with st.expander("📋 Ver tabla detallada de causas"):
            tabla_causas = df.groupby('causa').agg({
                'tiempo': ['sum', 'count', 'mean'],
                'fecha': 'nunique'
            }).reset_index()
            tabla_causas.columns = ['Causa', 'Tiempo Total (min)', 'Cantidad', 'Tiempo Prom (min)', 'Días Afectados']
            tabla_causas['% del Total'] = (tabla_causas['Tiempo Total (min)'] / tabla_causas['Tiempo Total (min)'].sum() * 100).round(2)
            tabla_causas = tabla_causas.sort_values('Tiempo Total (min)', ascending=False)
            st.dataframe(tabla_causas, use_container_width=True, hide_index=True)

            # Botón de descarga
            excel_data = generar_excel_descarga(tabla_causas, "Pareto_Causas")
            st.download_button(
                label="📥 Descargar tabla Excel",
                data=excel_data,
                file_name="pareto_causas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("ℹ️ No se encontró la columna de causa en los datos.")

with tab_pareto[1]:
    if 'estacion' in df.columns:
        fig_pareto_est = crear_pareto(
            df, 'estacion', 'tiempo',
            "Pareto de Paradas por Estación",
            top_n=15,
            color_barras=COLORES_INSTITUCIONALES['info']
        )
        st.plotly_chart(fig_pareto_est, use_container_width=True)

        with st.expander("📋 Ver tabla detallada de estaciones"):
            tabla_est = df.groupby('estacion').agg({
                'tiempo': ['sum', 'count', 'mean'],
                'fecha': 'nunique'
            }).reset_index()
            tabla_est.columns = ['Estación', 'Tiempo Total (min)', 'Cantidad', 'Tiempo Prom (min)', 'Días Afectados']
            tabla_est['% del Total'] = (tabla_est['Tiempo Total (min)'] / tabla_est['Tiempo Total (min)'].sum() * 100).round(2)
            tabla_est = tabla_est.sort_values('Tiempo Total (min)', ascending=False)
            st.dataframe(tabla_est, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No se encontró la columna de estación en los datos.")

with tab_pareto[2]:
    if 'sistema' in df.columns:
        fig_pareto_sist = crear_pareto(
            df, 'sistema', 'tiempo',
            "Pareto de Paradas por Sistema",
            top_n=15,
            color_barras=COLORES_INSTITUCIONALES['morado']
        )
        st.plotly_chart(fig_pareto_sist, use_container_width=True)
    else:
        st.info("ℹ️ No se encontró la columna de sistema en los datos.")

with tab_pareto[3]:
    if 'parte' in df.columns:
        fig_pareto_parte = crear_pareto(
            df, 'parte', 'tiempo',
            "Pareto de Paradas por Parte/Componente",
            top_n=15,
            color_barras=COLORES_INSTITUCIONALES['advertencia']
        )
        st.plotly_chart(fig_pareto_parte, use_container_width=True)
    else:
        st.info("ℹ️ No se encontró la columna de parte en los datos.")

with tab_pareto[4]:
    if 'turno' in df.columns:
        fig_pareto_turno = crear_pareto(
            df, 'turno', 'tiempo',
            "Pareto de Paradas por Turno",
            top_n=10,
            color_barras=COLORES_INSTITUCIONALES['exito']
        )
        st.plotly_chart(fig_pareto_turno, use_container_width=True)
    else:
        st.info("ℹ️ No se encontró la columna de turno en los datos.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 5: TENDENCIAS TEMPORALES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📈</span> TENDENCIAS TEMPORALES</div>", 
            unsafe_allow_html=True)

tab_tendencia = st.tabs(["📅 Por Día", "📆 Por Semana", "🗓️ Por Mes", "🌡️ Mapa de Calor"])

with tab_tendencia[0]:
    fig_tend_dia = crear_tendencia_temporal(df, agrupacion='D', titulo="Tendencia Diaria de Paradas")
    st.plotly_chart(fig_tend_dia, use_container_width=True)

with tab_tendencia[1]:
    fig_tend_sem = crear_tendencia_temporal(df, agrupacion='W', titulo="Tendencia Semanal de Paradas")
    st.plotly_chart(fig_tend_sem, use_container_width=True)

with tab_tendencia[2]:
    fig_tend_mes = crear_tendencia_temporal(df, agrupacion='M', titulo="Tendencia Mensual de Paradas")
    st.plotly_chart(fig_tend_mes, use_container_width=True)

with tab_tendencia[3]:
    if 'fecha' in df.columns:
        fig_heatmap = crear_heatmap_calendario(df, columna_valor='tiempo', 
                                               titulo="Mapa de Calor - Intensidad de Paradas por Día")
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("ℹ️ No se encontró información de fechas.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 6: ANÁLISIS JERÁRQUICO Y DISTRIBUCIONES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🗂️</span> ANÁLISIS JERÁRQUICO Y DISTRIBUCIONES</div>", 
            unsafe_allow_html=True)

col_j1, col_j2 = st.columns(2)

with col_j1:
    if 'estacion' in df.columns and 'sistema' in df.columns:
        st.markdown("<h4 style='color: #1e3a5f; margin-bottom: 1rem;'>Treemap: Jerarquía Estación → Sistema</h4>", 
                    unsafe_allow_html=True)
        fig_treemap = crear_treemap(
            df,
            path=['estacion', 'sistema'],
            valores='tiempo',
            titulo=""
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

with col_j2:
    if 'causa' in df.columns and 'parte' in df.columns:
        st.markdown("<h4 style='color: #1e3a5f; margin-bottom: 1rem;'>Sunburst: Causa → Parte</h4>", 
                    unsafe_allow_html=True)
        fig_sun = crear_sunburst(
            df,
            path=['causa', 'parte'],
            valores='tiempo',
            titulo=""
        )
        st.plotly_chart(fig_sun, use_container_width=True)

# Análisis de caja (Boxplot)
st.markdown("<h4 style='color: #1e3a5f; margin: 2rem 0 1rem 0;'>Distribución de Tiempos por Categoría</h4>", 
            unsafe_allow_html=True)

col_b1, col_b2 = st.columns(2)

with col_b1:
    if 'causa' in df.columns:
        fig_box_causa = crear_analisis_caja(df, 'causa', 'tiempo', 
                                            "Distribución de Tiempos por Causa")
        st.plotly_chart(fig_box_causa, use_container_width=True)

with col_b2:
    if 'estacion' in df.columns:
        fig_box_est = crear_analisis_caja(df, 'estacion', 'tiempo',
                                          "Distribución de Tiempos por Estación")
        st.plotly_chart(fig_box_est, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 7: ANÁLISIS CRUZADO Y COMPARATIVOS
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🔀</span> ANÁLISIS CRUZADO</div>", 
            unsafe_allow_html=True)

tab_cruzado = st.tabs(["📊 Barras Apiladas", "📈 Dispersión", "📉 Comparativo Temporal"])

with tab_cruzado[0]:
    if 'turno' in df.columns and 'causa' in df.columns:
        pivot_apilado = df.groupby(['turno', 'causa'])['tiempo'].sum().reset_index()
        fig_apilado = crear_grafico_barras_apiladas(
            pivot_apilado, 'turno', 'tiempo', 'causa',
            "Tiempo de Parada por Turno y Causa"
        )
        st.plotly_chart(fig_apilado, use_container_width=True)

with tab_cruzado[1]:
    if 'causa' in df.columns:
        scatter_data = df.groupby('causa').agg({
            'tiempo': ['sum', 'count', 'mean']
        }).reset_index()
        scatter_data.columns = ['causa', 'tiempo_total', 'cantidad', 'tiempo_promedio']
        scatter_data = scatter_data[scatter_data['cantidad'] >= 2]  # Filtrar causas con al menos 2 eventos

        if not scatter_data.empty:
            fig_scatter = crear_grafico_dispersion(
                scatter_data,
                'cantidad',
                'tiempo_total',
                'causa',
                'tiempo_promedio',
                "Relación Cantidad vs Tiempo Total de Paradas"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("💡 Tamaño de burbuja = Tiempo promedio por evento")

with tab_cruzado[2]:
    if 'fecha' in df.columns and 'turno' in df.columns:
        df['año_mes'] = df['fecha'].dt.to_period('M').astype(str)
        pivot_temporal = df.groupby(['año_mes', 'turno'])['tiempo'].sum().reset_index()

        fig_temporal = px.line(
            pivot_temporal,
            x='año_mes',
            y='tiempo',
            color='turno',
            markers=True,
            title="Evolución Temporal por Turno",
            labels={'tiempo': 'Tiempo (min)', 'año_mes': 'Período'},
            color_discrete_sequence=COLORES_INSTITUCIONALES['paleta']
        )
        fig_temporal.update_layout(
            height=450,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=60, r=40, t=80, b=60),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_temporal, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 8: ANÁLISIS DE TEXTO (NLP BÁSICO)
# ==============================================================================
if 'problema' in df.columns or 'trabajo' in df.columns:
    st.markdown("<div class='section-title'><span class='icon'>📝</span> ANÁLISIS DE DESCRIPCIONES</div>", 
                unsafe_allow_html=True)

    tab_texto = st.tabs(["🔍 Problemas", "🔧 Trabajos Realizados"])

    with tab_texto[0]:
        if 'problema' in df.columns:
            freq_problemas = analisis_texto_frecuencia(df, 'problema', top_n=20)
            if not freq_problemas.empty:
                fig_freq = px.bar(
                    freq_problemas,
                    x='Frecuencia',
                    y='Palabra',
                    orientation='h',
                    title="Palabras más frecuentes en descripciones de problemas",
                    color='Frecuencia',
                    color_continuous_scale='Oranges',
                    labels={'Frecuencia': 'N° de menciones', 'Palabra': ''}
                )
                fig_freq.update_layout(
                    height=500,
                    template='plotly_white',
                    margin=dict(l=100, r=40, t=60, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_freq, use_container_width=True)
            else:
                st.info("ℹ️ No hay suficientes descripciones para analizar.")

    with tab_texto[1]:
        if 'trabajo' in df.columns:
            freq_trabajos = analisis_texto_frecuencia(df, 'trabajo', top_n=20)
            if not freq_trabajos.empty:
                fig_freq_t = px.bar(
                    freq_trabajos,
                    x='Frecuencia',
                    y='Palabra',
                    orientation='h',
                    title="Palabras más frecuentes en trabajos realizados",
                    color='Frecuencia',
                    color_continuous_scale='Blues',
                    labels={'Frecuencia': 'N° de menciones', 'Palabra': ''}
                )
                fig_freq_t.update_layout(
                    height=500,
                    template='plotly_white',
                    margin=dict(l=100, r=40, t=60, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_freq_t, use_container_width=True)
            else:
                st.info("ℹ️ No hay suficientes descripciones para analizar.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 9: TABLA DE DATOS CRUDA Y EXPORTACIÓN
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📑</span> DATOS DETALLADOS Y EXPORTACIÓN</div>", 
            unsafe_allow_html=True)

with st.expander("📋 Ver tabla completa de datos", expanded=False):
    # Preparar datos para mostrar
    df_display = df.copy()
    if 'fecha' in df_display.columns:
        df_display['fecha'] = df_display['fecha'].dt.strftime('%d/%m/%Y')

    # Paginación simple
    rows_per_page = 50
    total_rows = len(df_display)
    total_pages = max(1, math.ceil(total_rows / rows_per_page))

    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        page = st.number_input("Página:", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)

    st.dataframe(
        df_display.iloc[start_idx:end_idx],
        use_container_width=True,
        hide_index=True,
        height=400
    )

    st.caption(f"Mostrando registros {start_idx + 1} - {end_idx} de {total_rows}")

    # Exportación
    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        excel_completo = generar_excel_descarga(df_display, "Datos_Completos")
        st.download_button(
            label="📥 Descargar Excel Completo",
            data=excel_completo,
            file_name=f"reporte_completo_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_e2:
        csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name=f"reporte_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 10: INFORME AUTOMÁTICO Y RECOMENDACIONES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>💡</span> INFORME AUTOMÁTICO Y RECOMENDACIONES</div>", 
            unsafe_allow_html=True)

# Generar recomendaciones automáticas basadas en datos
recomendaciones = []

# Recomendación 1: Disponibilidad
if metricas['disponibilidad'] < 85:
    recomendaciones.append({
        'tipo': 'crítico',
        'icono': '🔴',
        'titulo': 'Disponibilidad Crítica',
        'mensaje': f"La disponibilidad actual es del {metricas['disponibilidad']:.1f}%, muy por debajo del objetivo del 95%. Se requiere acción inmediata."
    })
elif metricas['disponibilidad'] < 95:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'Disponibilidad por Debajo del Objetivo',
        'mensaje': f"La disponibilidad es del {metricas['disponibilidad']:.1f}%. Se recomienda planificar acciones de mejora para alcanzar el 95%."
    })
else:
    recomendaciones.append({
        'tipo': 'exito',
        'icono': '🟢',
        'titulo': 'Disponibilidad Óptima',
        'mensaje': f"Excelente disponibilidad del {metricas['disponibilidad']:.1f}%. Mantener las prácticas actuales."
    })

# Recomendación 2: MTBF
if metricas['mtbf_horas'] < 4:
    recomendaciones.append({
        'tipo': 'crítico',
        'icono': '🔴',
        'titulo': 'MTBF Muy Bajo',
        'mensaje': f"El MTBF es de solo {metricas['mtbf_horas']:.1f} horas. Las fallas son demasiado frecuentes. Priorizar análisis de causa raíz."
    })
elif metricas['mtbf_horas'] < 8:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'MTBF Regular',
        'mensaje': f"MTBF de {metricas['mtbf_horas']:.1f} horas. Se recomienda implementar mantenimiento predictivo."
    })

# Recomendación 3: MTTR
if metricas['mttr_horas'] > 3:
    recomendaciones.append({
        'tipo': 'crítico',
        'icono': '🔴',
        'titulo': 'MTTR Elevado',
        'mensaje': f"El tiempo promedio de reparación es de {metricas['mttr_horas']:.1f} horas. Revisar procedimientos de mantenimiento y disponibilidad de repuestos."
    })
elif metricas['mttr_horas'] > 1:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'MTTR Regular',
        'mensaje': f"MTTR de {metricas['mttr_horas']:.1f} horas. Oportunidad de mejora en tiempos de respuesta."
    })

# Recomendación 4: Top causa
if 'causa' in df.columns:
    top_causa = df.groupby('causa')['tiempo'].sum().sort_values(ascending=False).head(1)
    if not top_causa.empty:
        causa_nombre = top_causa.index[0]
        causa_tiempo = top_causa.values[0]
        causa_pct = (causa_tiempo / metricas['tiempo_total_paradas']) * 100

        if causa_pct > 30:
            recomendaciones.append({
                'tipo': 'crítico',
                'icono': '🔴',
                'titulo': f'Causa Dominante: {causa_nombre}',
                'mensaje': f"Esta causa representa el {causa_pct:.1f}% del tiempo total de parada. Priorizar acciones correctivas enfocadas."
            })
        elif causa_pct > 15:
            recomendaciones.append({
                'tipo': 'advertencia',
                'icono': '🟡',
                'titulo': f'Causa Significativa: {causa_nombre}',
                'mensaje': f"Representa el {causa_pct:.1f}% del tiempo de parada. Incluir en plan de mejoras."
            })

# Mostrar recomendaciones
for rec in recomendaciones:
    color_map = {
        'crítico': '#fef2f2; border-left: 4px solid #dc2626;',
        'advertencia': '#fffbeb; border-left: 4px solid #f59e0b;',
        'exito': '#f0fdf4; border-left: 4px solid #22c55e;'
    }
    st.markdown(f"""
    <div style="{color_map[rec['tipo']]} padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.5rem 0; color: #1e293b;">{rec['icono']} {rec['titulo']}</h4>
        <p style="margin: 0; color: #475569;">{rec['mensaje']}</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 11: FOOTER INSTITUCIONAL
# ==============================================================================
st.markdown("""
<div class="footer">
    <p><strong>🏭 Sistema de Manufactura Inteligente</strong></p>
    <p>Dashboard Performance de Línea v3.0.0 | Desarrollado para Análisis Gerencial</p>
    <p style="margin-top: 0.5rem; font-size: 0.75rem;">
        © 2026 | Compatible con SharePoint y archivos Excel estándar | 
        Métricas calculadas según estándares SMRP e ISO 14224
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FIN DEL SCRIPT
# ==============================================================================
