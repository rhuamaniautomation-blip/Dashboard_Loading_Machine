
"""
================================================================================
DASHBOARD PROFESIONAL DE PERFORMANCE DE LÍNEA - STREAMLIT CLOUD
================================================================================
Aplicación institucional para análisis de paradas, disponibilidad, MTBF y MTTR.
Compatible con archivos Excel estándar desde SharePoint o carga local.

Desarrollado por: CAVA Especialistas en Robotica y Automatizacion - Roger Huamani
Versión: 3.2.0
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

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Performance de Línea | CAVA",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Dashboard Performance de Línea v3.3.0 - Desarrollado por CAVA Especialistas en Robotica y Automatizacion - Roger Huamani"
    }
)

# ==============================================================================
# CSS PERSONALIZADO INSTITUCIONAL - TEMA CLARO Y ALTO CONTRASTE
# ==============================================================================
st.markdown("""
<style>
    /* ================================================================ */
    /* TEMA CORPORATIVO INSTITUCIONAL - CLARO Y LIMPIO                  */
    /* ================================================================ */

    /* Fuentes y base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
    }

    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    }

    /* ================================================================ */
    /* MARCA DE AGUA INSTITUCIONAL                                       */
    /* ================================================================ */
    body::before {
        content: "CAVA ESPECIALISTAS EN ROBOTICA Y AUTOMATIZACION\aROGER HUAMANI - DASHBOARD v3.3.0";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-25deg);
        font-size: 2.8rem;
        color: rgba(15, 76, 129, 0.035);
        z-index: 9999;
        pointer-events: none;
        font-weight: 800;
        white-space: pre;
        text-align: center;
        line-height: 1.4;
        letter-spacing: 2px;
    }

    /* ================================================================ */
    /* HEADER INSTITUCIONAL                                              */
    /* ================================================================ */
    .main-header {
        background: linear-gradient(90deg, #0f4c81 0%, #1e6ba3 50%, #0f4c81 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(15, 76, 129, 0.25);
        border-left: 6px solid #f59e0b;
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
        color: #e2e8f0 !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        margin: 0.5rem 0 0 0 !important;
    }

    .main-header .badge {
        background: #f59e0b;
        color: #1e293b;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
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
        box-shadow: 0 12px 40px rgba(0,0,0,0.10);
    }

    .kpi-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #f59e0b, #d97706);
    }

    .kpi-container.green::before {
        background: linear-gradient(180deg, #16a34a, #15803d);
    }

    .kpi-container.blue::before {
        background: linear-gradient(180deg, #2563eb, #1d4ed8);
    }

    .kpi-container.red::before {
        background: linear-gradient(180deg, #dc2626, #b91c1c);
    }

    .kpi-container.purple::before {
        background: linear-gradient(180deg, #7c3aed, #6d28d9);
    }

    .kpi-label {
        font-size: 0.85rem;
        color: #475569;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0f172a;
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
        color: #16a34a;
    }

    .kpi-delta.negative {
        color: #dc2626;
    }

    .kpi-subtext {
        font-size: 0.8rem;
        color: #64748b;
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
        color: #0f4c81;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #f59e0b;
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
        background: linear-gradient(90deg, #0f4c81, #1e6ba3);
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
        background: linear-gradient(180deg, #0f4c81 0%, #0f172a 100%);
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
        background: linear-gradient(90deg, #f59e0b, #d97706);
        color: #0f172a;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #d97706, #f59e0b);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
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
        color: #475569;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
        background: white;
        border-radius: 16px;
    }

    .footer strong {
        color: #0f4c81;
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
        color: #0f4c81 !important;
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

    .progress-bar.green { background: linear-gradient(90deg, #16a34a, #22c55e); }
    .progress-bar.yellow { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .progress-bar.red { background: linear-gradient(90deg, #dc2626, #ef4444); }

    /* ================================================================ */
    /* DIVISORES Y SEPARADORES                                           */
    /* ================================================================ */
    .divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #f59e0b, transparent);
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
    'primario': '#0f4c81',
    'secundario': '#1e6ba3',
    'acento': '#f59e0b',
    'exito': '#16a34a',
    'peligro': '#dc2626',
    'advertencia': '#d97706',
    'info': '#2563eb',
    'morado': '#7c3aed',
    'gris': '#64748b',
    'paleta': ['#0f4c81', '#f59e0b', '#16a34a', '#dc2626', '#7c3aed',
               '#2563eb', '#f97316', '#0891b2', '#475569', '#db2777']
}

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

DIAS_ES = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
           4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}


# ==============================================================================
# CONFIGURACIÓN PERSISTENTE MEDIANTE QUERY PARAMS
# ==============================================================================
def init_config():
    """Inicializa configuración desde query params (URL) o valores por defecto.
    CORREGIDO: Compatible con Streamlit 2026 - st.query_params API."""
    # CORRECCIÓN: st.query_params no tiene método .get() con default en versiones nuevas
    # Usamos to_dict() para obtener un diccionario plano y luego .get()
    try:
        qp = st.query_params.to_dict()
    except Exception:
        qp = {}

    def _get_float(key, default):
        val = qp.get(key)
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def _get_int(key, default):
        val = qp.get(key)
        if val is None:
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default

    config = {
        'minutos_turno': _get_int('mt', 480),
        'turnos_dia': _get_int('td', 2),
        'gauge_max_mtbf': _get_float('gmm', 12),
        'gauge_max_mttr': _get_float('gmtrm', 5),
        'umbral_disp_green': _get_float('udg', 95),
        'umbral_disp_yellow': _get_float('udy', 85),
        'umbral_mtbf_green': _get_float('umg', 8),
        'umbral_mtbf_yellow': _get_float('umy', 4),
        'umbral_mttr_green': _get_float('utg', 1),
        'umbral_mttr_yellow': _get_float('uty', 3),
    }
    return config


def save_config_to_url(config):
    """Guarda la configuración actual en los query params de la URL.
    CORREGIDO: Usa from_dict() para actualizar múltiples params de forma atómica."""
    params = {
        'mt': str(int(config['minutos_turno'])),
        'td': str(int(config['turnos_dia'])),
        'gmm': str(float(config['gauge_max_mtbf'])),
        'gmtrm': str(float(config['gauge_max_mttr'])),
        'udg': str(float(config['umbral_disp_green'])),
        'udy': str(float(config['umbral_disp_yellow'])),
        'umg': str(float(config['umbral_mtbf_green'])),
        'umy': str(float(config['umbral_mtbf_yellow'])),
        'utg': str(float(config['umbral_mttr_green'])),
        'uty': str(float(config['umbral_mttr_yellow'])),
    }
    try:
        st.query_params.from_dict(params)
    except Exception as e:
        st.error(f"Error al guardar configuración en URL: {str(e)}")


# ==============================================================================
# FUNCIONES DE UTILIDAD Y AYUDA
# ==============================================================================
def detectar_columnas(df):
    """
    Detecta automáticamente las columnas del DataFrame basándose en
    variantes conocidas de nombres de columnas estándar.
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
    CORREGIDO: Maneja mejor fechas mixtas (números, strings, datetime).
    """
    if pd.isna(valor):
        return pd.NaT

    # Si ya es datetime o Timestamp, devolverlo directamente
    if isinstance(valor, (pd.Timestamp, datetime)):
        return valor

    if isinstance(valor, (int, float)):
        try:
            # Fecha serial de Excel (número de días desde 1899-12-30)
            if valor > 30000:  # Evitar fechas inválidas pequeñas
                return pd.Timestamp('1899-12-30') + pd.Timedelta(days=int(valor))
            else:
                return pd.NaT
        except:
            return pd.NaT

    if isinstance(valor, str):
        valor = valor.strip()
        if not valor:
            return pd.NaT
        formatos = [
            '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y',
            '%d/%m/%y', '%Y/%m/%d', '%d.%m.%Y', '%Y%m%d',
            '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'
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
    CORREGIDO: Mejor manejo de encabezados duplicados y fechas.
    """
    df_limpio = df.copy()

    # Eliminar filas que parecen ser encabezados repetidos
    if len(df_limpio) > 0:
        primera_fila = df_limpio.iloc[0].astype(str).str.strip().str.lower()
        encabezados_comunes = ['fecha', 'turno', 'aviso', 'tiempo', 'maquina', 'estación', 'estacion', 'sistema']
        if any(primera_fila.isin(encabezados_comunes)):
            df_limpio = df_limpio.iloc[1:].reset_index(drop=True)

    # Renombrar columnas a nombres estándar
    rename_map = {v: k for k, v in columnas_map.items()}
    df_limpio = df_limpio.rename(columns=rename_map)

    # Procesar columna de fecha
    if 'fecha' in df_limpio.columns:
        df_limpio['fecha'] = df_limpio['fecha'].apply(convertir_fecha_excel)
        filas_antes = len(df_limpio)
        df_limpio = df_limpio.dropna(subset=['fecha'])
        filas_despues = len(df_limpio)
        if filas_despues < filas_antes:
            st.warning(f"⚠️ Se eliminaron {filas_antes - filas_despues} filas con fechas inválidas.")
        df_limpio['fecha'] = pd.to_datetime(df_limpio['fecha'], errors='coerce')
        df_limpio = df_limpio.dropna(subset=['fecha'])

    # Procesar columna de tiempo
    if 'tiempo' in df_limpio.columns:
        df_limpio['tiempo'] = pd.to_numeric(df_limpio['tiempo'], errors='coerce')
        df_limpio = df_limpio[df_limpio['tiempo'] > 0]
        df_limpio['tiempo_horas'] = df_limpio['tiempo'] / 60.0

    # Limpiar columnas categóricas
    for col in ['turno', 'maquina', 'estacion', 'sistema', 'parte', 'causa']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace(['nan', 'None', '', 'NaN'], 'No Especificado')

    # Limpiar textos largos
    for col in ['problema', 'trabajo']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace(['nan', 'None', 'NaN'], '')

    # Crear columnas derivadas de fecha
    if 'fecha' in df_limpio.columns:
        df_limpio['año'] = df_limpio['fecha'].dt.year
        df_limpio['mes'] = df_limpio['fecha'].dt.month
        df_limpio['mes_nombre'] = df_limpio['mes'].map(MESES_ES)
        df_limpio['dia_semana'] = df_limpio['fecha'].dt.dayofweek
        df_limpio['dia_nombre'] = df_limpio['dia_semana'].map(DIAS_ES)
        df_limpio['semana'] = df_limpio['fecha'].dt.isocalendar().week.astype(int)
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
    Maneja específicamente errores de autenticación de SharePoint empresarial.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, application/octet-stream, */*'
        }
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            # Detectar si SharePoint devolvió página de login en lugar del archivo
            if 'html' in content_type or b'<html' in response.content[:500].lower():
                st.error("🔒 La URL devolvió una página HTML (probablemente login de SharePoint) en lugar del archivo Excel.")
                st.markdown("""
                <div class="alert-box warning">
                    <strong>Soluciones para SharePoint Empresarial / Cuenta Profesional:</strong><br><br>
                    1. <strong>Descarga manual:</strong> Baje el archivo desde SharePoint y utilice la opción <em>Archivo Local</em>.<br>
                    2. <strong>Enlace anónimo:</strong> En SharePoint, genere un enlace de acceso <em>"Cualquiera con el enlace"</em> (requiere permisos de administrador).<br>
                    3. <strong>Descarga directa:</strong> Al copiar el enlace de SharePoint Online, reemplace <code>?web=1</code> por <code>?download=1</code> al final de la URL.<br>
                    4. <strong>Microsoft Graph API:</strong> Para integración automática se requiere registro de aplicación en Azure AD con autenticación OAuth2 (fuera del alcance de esta app estándar).<br><br>
                    <em>Nota: Las cuentas profesionales con MFA/Autenticación moderna no permiten descarga directa sin token de acceso.</em>
                </div>
                """, unsafe_allow_html=True)
                return None
            return BytesIO(response.content)
        elif response.status_code in [401, 403]:
            st.error(f"🔒 Acceso denegado (HTTP {response.status_code}). El archivo requiere autenticación.")
            st.info("Para SharePoint/OneDrive empresarial, use la opción 'Archivo Local' o genere un enlace de acceso anónimo.")
            return None
        else:
            st.error(f"❌ Error al descargar: Código HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        st.error("⏱️ Tiempo de espera agotado. El archivo es muy grande o la conexión es lenta.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Error de conexión. Verifique la URL y su conexión a internet.")
        return None
    except Exception as e:
        st.error(f"❌ Error al descargar archivo: {str(e)}")
        return None


def generar_excel_descarga(df, nombre_hoja='Reporte'):
    """
    Genera un archivo Excel en memoria para descarga.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=nombre_hoja, index=False)
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


def calcular_kpi_color(valor, tipo='disponibilidad', config=None):
    """
    Determina el color de un KPI basado en umbrales configurables.
    """
    if config is None:
        config = st.session_state.get('config', {})

    if tipo == 'disponibilidad':
        if valor >= config.get('umbral_disp_green', 95):
            return 'green'
        elif valor >= config.get('umbral_disp_yellow', 85):
            return 'yellow'
        else:
            return 'red'
    elif tipo == 'mtbf':
        if valor >= config.get('umbral_mtbf_green', 8):
            return 'green'
        elif valor >= config.get('umbral_mtbf_yellow', 4):
            return 'yellow'
        else:
            return 'red'
    elif tipo == 'mttr':
        if valor <= config.get('umbral_mttr_green', 1):
            return 'green'
        elif valor <= config.get('umbral_mttr_yellow', 3):
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
    """
    if pd.isna(valor) or valor == 0:
        return f"0{sufijo}"

    if valor >= 1000000:
        return f"{valor/1000000:.{decimales}f}M{sufijo}"
    elif valor >= 1000:
        return f"{valor/1000:.{decimales}f}K{sufijo}"
    else:
        return f"{valor:.{decimales}f}{sufijo}"


def crear_gauge_chart(valor, titulo, maximo=100, color_primario=None, umbral_linea=85):
    """
    Crea un gráfico gauge (medidor) profesional con Plotly.
    """
    if color_primario is None:
        color_primario = COLORES_INSTITUCIONALES['primario']

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo, 'font': {'size': 18, 'color': '#0f172a', 'family': 'Inter, sans-serif'}},
        number={'font': {'size': 28, 'color': '#0f172a', 'family': 'Inter, sans-serif'},
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
                'value': maximo * (umbral_linea / 100.0) if maximo == 100 else umbral_linea
            }
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'}
    )

    return fig


def crear_pareto(df, columna_categoria, columna_valor, titulo, top_n=15, color_barras=None):
    """
    Crea un gráfico de Pareto profesional con barras y línea acumulada.
    """
    if color_barras is None:
        color_barras = COLORES_INSTITUCIONALES['acento']

    pareto_data = df.groupby(columna_categoria)[columna_valor].sum().reset_index()
    pareto_data = pareto_data.sort_values(columna_valor, ascending=False).head(top_n)
    pareto_data['acumulado'] = pareto_data[columna_valor].cumsum()
    pareto_data['porcentaje_acumulado'] = (pareto_data['acumulado'] / pareto_data[columna_valor].sum()) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=pareto_data[columna_categoria],
            y=pareto_data[columna_valor],
            name='Tiempo (min)',
            marker_color=color_barras,
            text=pareto_data[columna_valor].round(1),
            textposition='outside',
            textfont={'size': 11, 'color': '#0f172a'},
            hovertemplate='<b>%{x}</b><br>Tiempo: %{y:.1f} min<extra></extra>'
        ),
        secondary_y=False
    )

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

    fig.add_hline(
        y=80, line_dash="dash", line_color="#dc2626", line_width=2,
        secondary_y=True,
        annotation_text="Regla 80/20",
        annotation_position="right",
        annotation_font_color="#dc2626"
    )

    fig.update_layout(
        title={
            'text': f"<b>{titulo}</b>",
            'font': {'size': 20, 'color': '#0f172a', 'family': 'Inter, sans-serif'},
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
    """
    df_temp = df.copy()
    df_temp = df_temp.dropna(subset=['fecha'])
    if df_temp.empty:
        fig = go.Figure()
        fig.update_layout(title=titulo + " (Sin datos)", height=400)
        return fig

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
            'font': {'size': 20, 'color': '#0f172a', 'family': 'Inter, sans-serif'},
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
    CORREGIDO: Usa estructura moderna de colorbar compatible con Plotly 5.x+.
    """
    df_cal = df.copy()
    df_cal = df_cal.dropna(subset=['fecha'])
    if df_cal.empty:
        fig = go.Figure()
        fig.update_layout(title=titulo + " (Sin datos)", height=400)
        return fig

    df_cal['dia_semana'] = df_cal['fecha'].dt.dayofweek
    df_cal['semana_año'] = df_cal['fecha'].dt.isocalendar().week.astype(int)
    df_cal['mes'] = df_cal['fecha'].dt.month

    pivot = df_cal.groupby(['semana_año', 'dia_semana'])[columna_valor].sum().reset_index()
    pivot_pivot = pivot.pivot(index='semana_año', columns='dia_semana', values=columna_valor).fillna(0)

    dias_labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    # CORRECCIÓN: colorbar title como dict en lugar de titleside (obsoleto)
    fig = go.Figure(data=go.Heatmap(
        z=pivot_pivot.values,
        x=dias_labels[:len(pivot_pivot.columns)],
        y=[f"Sem {s}" for s in pivot_pivot.index],
        colorscale=[
            [0, '#f0fdf4'],
            [0.2, '#fef3c7'],
            [0.5, '#fdba74'],
            [0.8, '#ef4444'],
            [1, '#7f1d1d']
        ],
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.0f} min<extra></extra>',
        colorbar=dict(
            title={"text": "Minutos", "side": "right"}
        )
    ))

    fig.update_layout(
        title={
            'text': f"<b>{titulo}</b>",
            'font': {'size': 18, 'color': '#0f172a'},
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
        title={'font': {'size': 18, 'color': '#0f172a'}, 'x': 0.5},
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
            'tiempo_promedio_parada': 0,
            'dias_analizados': 0,
            'tiempo_programado': 0
        }

    fecha_inicio = df['fecha'].min()
    fecha_fin = df['fecha'].max()

    if pd.isna(fecha_inicio) or pd.isna(fecha_fin):
        return {
            'mtbf_horas': 0, 'mttr_horas': 0, 'mtbf_minutos': 0, 'mttr_minutos': 0,
            'disponibilidad': 0, 'tiempo_total_paradas': 0, 'tiempo_operativo_total': 0,
            'total_fallas': len(df), 'tiempo_promedio_parada': 0,
            'dias_analizados': 0, 'tiempo_programado': 0
        }

    dias_totales = (fecha_fin - fecha_inicio).days + 1
    tiempo_programado = dias_totales * turnos_por_dia * minutos_turno
    tiempo_total_paradas = df['tiempo'].sum()
    tiempo_operativo = max(0, tiempo_programado - tiempo_total_paradas)
    total_fallas = len(df)

    if total_fallas > 0:
        mtbf_minutos = tiempo_operativo / total_fallas
        mttr_minutos = tiempo_total_paradas / total_fallas
    else:
        mtbf_minutos = tiempo_operativo
        mttr_minutos = 0

    mtbf_horas = mtbf_minutos / 60.0
    mttr_horas = mttr_minutos / 60.0

    if (mtbf_minutos + mttr_minutos) > 0:
        disponibilidad = (mtbf_minutos / (mtbf_minutos + mttr_minutos)) * 100
    else:
        disponibilidad = 100.0

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
    """
    if columna_texto not in df.columns:
        return pd.DataFrame()

    textos = df[columna_texto].dropna().astype(str)
    textos = textos[textos.str.len() > 3]

    if textos.empty:
        return pd.DataFrame()

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
        title={'font': {'size': 18, 'color': '#0f172a'}, 'x': 0.5},
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(
        textfont={'size': 13, 'family': 'Inter, sans-serif'},
        hovertemplate='<b>%{label}</b><br>Tiempo: %{value:.0f} min<extra></extra>'
    )

    return fig


def crear_sunburst(df, path, valores, titulo):
    """
    Crea un gráfico sunburst para análisis jerárquico circular.
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
        title={'font': {'size': 18, 'color': '#0f172a'}, 'x': 0.5},
        height=550,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(
        textfont={'size': 12, 'family': 'Inter, sans-serif'},
        hovertemplate='<b>%{label}</b><br>Tiempo: %{value:.0f} min<extra></extra>'
    )

    return fig


def crear_grafico_barras_apiladas(df, eje_x, eje_y, color, titulo):
    """
    Crea gráfico de barras apiladas para comparación cruzada.
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
        title={'font': {'size': 18, 'color': '#0f172a'}, 'x': 0.5},
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
        title={'font': {'size': 18, 'color': '#0f172a'}, 'x': 0.5},
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
    Maneja gracefulmente columnas faltantes.
    """
    if df.empty or 'fecha' not in df.columns:
        return """
        <div style="background: linear-gradient(135deg, #0f4c81 0%, #1e6ba3 100%);
                    padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
            <h3 style="color: #f59e0b; margin-bottom: 1rem; font-size: 1.4rem;">📊 RESUMEN EJECUTIVO</h3>
            <p style="font-size: 1.05rem; line-height: 1.8;">
                No hay datos suficientes para generar un resumen ejecutivo.
            </p>
        </div>
        """

    fecha_inicio_str = df['fecha'].min().strftime('%d/%m/%Y')
    fecha_fin_str = df['fecha'].max().strftime('%d/%m/%Y')

    resumen = f"""
    <div style="background: linear-gradient(135deg, #0f4c81 0%, #1e6ba3 100%);
                padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
        <h3 style="color: #fbbf24; margin-bottom: 1rem; font-size: 1.4rem;">📊 RESUMEN EJECUTIVO</h3>
        <p style="font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            Durante el período analizado (<strong>{fecha_inicio_str} - {fecha_fin_str}</strong>),
            la línea registró <strong>{metricas['total_fallas']} eventos</strong> de parada
            con un tiempo total de <strong>{metricas['tiempo_total_paradas']:.0f} minutos
            ({metricas['tiempo_total_paradas']/60:.1f} horas)</strong>.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            La <strong>disponibilidad</strong> de la línea fue del <strong>{metricas['disponibilidad']:.2f}%</strong>,
            con un <strong>MTBF de {metricas['mtbf_horas']:.2f} horas</strong> y un
            <strong>MTTR de {metricas['mttr_horas']:.2f} horas</strong>.
        </p>
    """

    # Top causas - solo si existe la columna
    if 'causa' in df.columns:
        top_causas = df.groupby('causa')['tiempo'].sum().sort_values(ascending=False).head(3)
        if not top_causas.empty:
            resumen += """<div style="margin-top: 1.5rem;">
            <h4 style="color: #fbbf24; font-size: 1.1rem;">🔴 Principales Causas de Parada:</h4>
            <ul style="line-height: 1.8;">
            """
            for causa, tiempo in top_causas.items():
                pct = (tiempo / metricas['tiempo_total_paradas']) * 100 if metricas['tiempo_total_paradas'] > 0 else 0
                resumen += f"<li><strong>{causa}</strong>: {tiempo:.0f} min ({pct:.1f}% del total)</li>\n"
            resumen += "</ul></div>"

    # Top estaciones - solo si existe la columna
    if 'estacion' in df.columns:
        top_estaciones = df.groupby('estacion')['tiempo'].sum().sort_values(ascending=False).head(3)
        if not top_estaciones.empty:
            resumen += """<div style="margin-top: 1.5rem;">
            <h4 style="color: #fbbf24; font-size: 1.1rem;">⚙️ Estaciones Críticas:</h4>
            <ul style="line-height: 1.8;">
            """
            for est, tiempo in top_estaciones.items():
                pct = (tiempo / metricas['tiempo_total_paradas']) * 100 if metricas['tiempo_total_paradas'] > 0 else 0
                resumen += f"<li><strong>{est}</strong>: {tiempo:.0f} min ({pct:.1f}% del total)</li>\n"
            resumen += "</ul></div>"

    resumen += "</div>"
    return resumen


def render_kpi_card(label, valor, delta=None, delta_type="normal",
                    subtext="", color_class="", icon="📊"):
    """
    Renderiza una tarjeta KPI HTML personalizada.
    """
    delta_html = ""
    if delta:
        delta_class = "positive" if delta_type == "normal" else "negative"
        try:
            if float(delta.replace('%', '').replace('+', '').replace('-', '')) < 0:
                delta_class = "negative" if delta_type == "normal" else "positive"
        except:
            pass
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
# INICIALIZACIÓN DE ESTADO DE SESIÓN Y CONFIGURACIÓN
# ==============================================================================
if 'datos_cargados' not in st.session_state:
    st.session_state.datos_cargados = False
    st.session_state.df_original = None
    st.session_state.df_filtrado = None
    st.session_state.columnas_map = {}
    st.session_state.metricas = {}
    st.session_state.nombre_archivo = ""
    st.session_state.filtros_aplicados = False

# Inicializar configuración persistente
if 'config' not in st.session_state:
    st.session_state.config = init_config()


# ==============================================================================
# SIDEBAR - PANEL DE CONTROL Y CONFIGURACIÓN
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0; border-bottom: 1px solid #334155; margin-bottom: 2rem;">
        <h1 style="color: #f59e0b; font-size: 1.8rem; margin: 0;">🏭</h1>
        <h2 style="color: #f8fafc; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 700;">
            CAVA ROBOTICA
        </h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 0.3rem 0 0 0;">
            Especialistas en Robotica y Automatizacion
        </p>
        <p style="color: #fbbf24; font-size: 0.75rem; margin: 0.5rem 0 0 0; font-weight: 600;">
            Roger Huamani
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #f59e0b; font-size: 1rem; margin-bottom: 1rem;'>📥 CARGA DE DATOS</h3>",
                unsafe_allow_html=True)

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
            help="Ingrese la URL directa del archivo Excel. Para SharePoint empresarial, prefiera 'Archivo Local' o use enlaces anónimos."
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
                xls = pd.ExcelFile(archivo_cargado)
                hojas_disponibles = xls.sheet_names

                hoja_seleccionada = hojas_disponibles[0]
                if len(hojas_disponibles) > 1:
                    hoja_seleccionada = st.selectbox(
                        "Hoja a analizar:",
                        hojas_disponibles,
                        index=0
                    )

                df_raw = pd.read_excel(archivo_cargado, sheet_name=hoja_seleccionada)
                columnas_detectadas = detectar_columnas(df_raw)

                if not columnas_detectadas:
                    st.error("❌ No se detectaron columnas válidas. Verifique el formato del archivo.")
                    st.info("Columnas esperadas: FECHA, TURNO, TIEMPO, MAQUINA, ESTACION, SISTEMA, PARTE, CAUSA")
                else:
                    df_limpio = limpiar_dataframe(df_raw, columnas_detectadas)

                    if df_limpio.empty:
                        st.error("❌ No se encontraron datos válidos después de la limpieza.")
                    else:
                        st.session_state.df_original = df_limpio
                        st.session_state.df_filtrado = df_limpio.copy()
                        st.session_state.columnas_map = columnas_detectadas
                        st.session_state.datos_cargados = True
                        st.session_state.filtros_aplicados = False

                        cfg = st.session_state.config
                        st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(
                            df_limpio,
                            minutos_turno=cfg['minutos_turno'],
                            turnos_por_dia=cfg['turnos_dia']
                        )

                        st.success(f"✅ Datos cargados exitosamente: {len(df_limpio)} registros")

                        with st.expander("📋 Columnas detectadas"):
                            for estandar, real in columnas_detectadas.items():
                                st.markdown(f"<span style='color: #16a34a;'>✓</span> <strong>{estandar}</strong>: `{real}`",
                                          unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error al procesar archivo: {str(e)}")
            st.info("💡 Verifique que el archivo sea un Excel válido y esté accesible.")

    st.markdown("<hr style='border-color: #334155; margin: 2rem 0;'>", unsafe_allow_html=True)

    # Filtros dinámicos
    if st.session_state.datos_cargados:
        st.markdown("<h3 style='color: #f59e0b; font-size: 1rem; margin-bottom: 1rem;'>🔍 FILTROS</h3>",
                    unsafe_allow_html=True)

        df = st.session_state.df_original

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

        if st.button("🎯 APLICAR FILTROS", use_container_width=True):
            df_filtrado = df.copy()

            if fecha_inicio and fecha_fin:
                df_filtrado = df_filtrado[
                    (df_filtrado['fecha'].dt.date >= fecha_inicio) &
                    (df_filtrado['fecha'].dt.date <= fecha_fin)
                ]

            for col, valores in filtros.items():
                df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]

            st.session_state.df_filtrado = df_filtrado
            cfg = st.session_state.config
            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(
                df_filtrado,
                minutos_turno=cfg['minutos_turno'],
                turnos_por_dia=cfg['turnos_dia']
            )
            st.session_state.filtros_aplicados = True
            st.success(f"✅ Filtros aplicados: {len(df_filtrado)} registros")
            st.rerun()

        if st.button("🧹 LIMPIAR FILTROS", use_container_width=True):
            st.session_state.df_filtrado = st.session_state.df_original.copy()
            cfg = st.session_state.config
            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(
                st.session_state.df_original,
                minutos_turno=cfg['minutos_turno'],
                turnos_por_dia=cfg['turnos_dia']
            )
            st.session_state.filtros_aplicados = False
            st.rerun()

    # Configuración de parámetros de turno y gauges
    st.markdown("<hr style='border-color: #334155; margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #f59e0b; font-size: 1rem; margin-bottom: 1rem;'>⚙️ CONFIGURACIÓN</h3>",
                unsafe_allow_html=True)

    cfg = st.session_state.config

    minutos_turno = st.number_input(
        "Minutos por turno:",
        min_value=1,
        max_value=1440,
        value=int(cfg['minutos_turno']),
        help="Duración de un turno en minutos (default: 480 = 8 horas)"
    )

    turnos_dia = st.number_input(
        "Turnos por día:",
        min_value=1,
        max_value=3,
        value=int(cfg['turnos_dia']),
        help="Cantidad de turnos operativos por día"
    )

    st.markdown("<h4 style='color: #94a3b8; font-size: 0.85rem; margin-top: 1.5rem;'>🎚️ LÍMITES DE MEDIDORES (GAUGES)</h4>",
                unsafe_allow_html=True)

    gauge_max_mtbf = st.number_input("Máximo gauge MTBF (h):", min_value=1.0, value=float(cfg['gauge_max_mtbf']), step=1.0)
    gauge_max_mttr = st.number_input("Máximo gauge MTTR (h):", min_value=1.0, value=float(cfg['gauge_max_mttr']), step=1.0)

    st.markdown("<h4 style='color: #94a3b8; font-size: 0.85rem; margin-top: 1rem;'>🚦 UMBRALES DE COLORES</h4>",
                unsafe_allow_html=True)

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        umbral_disp_green = st.number_input("Disp. Verde ≥", min_value=0.0, max_value=100.0, value=float(cfg['umbral_disp_green']), step=1.0)
        umbral_disp_yellow = st.number_input("Disp. Amarillo ≥", min_value=0.0, max_value=100.0, value=float(cfg['umbral_disp_yellow']), step=1.0)
    with col_u2:
        umbral_mtbf_green = st.number_input("MTBF Verde ≥", min_value=0.0, value=float(cfg['umbral_mtbf_green']), step=1.0)
        umbral_mtbf_yellow = st.number_input("MTBF Amarillo ≥", min_value=0.0, value=float(cfg['umbral_mtbf_yellow']), step=1.0)

    umbral_mttr_green = st.number_input("MTTR Verde ≤", min_value=0.0, value=float(cfg['umbral_mttr_green']), step=0.5)
    umbral_mttr_yellow = st.number_input("MTTR Amarillo ≤", min_value=0.0, value=float(cfg['umbral_mttr_yellow']), step=0.5)

    # Actualizar config en session state
    st.session_state.config.update({
        'minutos_turno': minutos_turno,
        'turnos_dia': turnos_dia,
        'gauge_max_mtbf': gauge_max_mtbf,
        'gauge_max_mttr': gauge_max_mttr,
        'umbral_disp_green': umbral_disp_green,
        'umbral_disp_yellow': umbral_disp_yellow,
        'umbral_mtbf_green': umbral_mtbf_green,
        'umbral_mtbf_yellow': umbral_mtbf_yellow,
        'umbral_mttr_green': umbral_mttr_green,
        'umbral_mttr_yellow': umbral_mttr_yellow,
    })

    if st.button("💾 GUARDAR CONFIGURACIÓN", use_container_width=True):
        save_config_to_url(st.session_state.config)
        st.success("✅ Configuración guardada en la URL. Guarde el enlace actual para recuperar estos ajustes en otra sesión.")
        st.info("🔗 Puede usar el botón 'Compartir' del navegador o copiar la URL actual.")

    # Footer sidebar
    st.markdown("""
    <div style="margin-top: 3rem; padding: 1rem; background: #0f172a; border-top: 1px solid #334155; text-align: center;">
        <p style="color: #94a3b8; font-size: 0.75rem; margin: 0;">
            v3.3.0 | CAVA Especialistas en Robotica y Automatizacion
        </p>
        <p style="color: #fbbf24; font-size: 0.7rem; margin: 0.2rem 0 0 0;">
            Roger Huamani
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
    <span class="badge">CAVA ESPECIALISTAS EN ROBOTICA Y AUTOMATIZACION - ROGER HUAMANI</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# PANTALLA DE BIENVENIDA (SIN DATOS)
# ==============================================================================
if not st.session_state.datos_cargados:
    st.markdown("""
    <div class="section-card" style="text-align: center; padding: 4rem 2rem;">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">📊</h1>
        <h2 style="color: #0f4c81; font-size: 1.8rem; margin-bottom: 1rem;">Bienvenido al Dashboard de Performance</h2>
        <p style="color: #475569; font-size: 1.1rem; max-width: 600px; margin: 0 auto 2rem auto; line-height: 1.8;">
            Este sistema permite analizar el performance de líneas de producción mediante
            el análisis de paradas, cálculo de disponibilidad, MTBF y MTTR.
            Cargue un archivo Excel desde SharePoint o localmente para comenzar.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; max-width: 900px; margin: 0 auto;">
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #f59e0b; font-size: 1.2rem;">📈 Pareto de Paradas</h3>
                <p style="color: #475569; font-size: 0.9rem;">Identifique las causas principales siguiendo la regla 80/20</p>
            </div>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #f59e0b; font-size: 1.2rem;">⏱️ MTBF / MTTR</h3>
                <p style="color: #475569; font-size: 0.9rem;">Métricas clave de confiabilidad y mantenibilidad</p>
            </div>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #f59e0b; font-size: 1.2rem;">📊 Disponibilidad</h3>
                <p style="color: #475569; font-size: 0.9rem;">Cálculo automático de disponibilidad de línea</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

        st.markdown("""
        **🔒 Nota sobre SharePoint Empresarial:**
        Si su archivo está en SharePoint/OneDrive de una cuenta profesional (con autenticación MFA),
        la descarga directa por URL no es posible por seguridad. Use la opción **Archivo Local** o
        genere un enlace de acceso anónimo desde SharePoint (requiere permisos de administrador).
        """)

    st.stop()


# ==============================================================================
# DASHBOARD PRINCIPAL (CON DATOS CARGADOS)
# ==============================================================================
df = st.session_state.df_filtrado
metricas = st.session_state.metricas
config = st.session_state.config

# Recalcular métricas con configuración actual
metricas = calcular_mtbf_mttr_disponibilidad(
    df,
    minutos_turno=config['minutos_turno'],
    turnos_por_dia=config['turnos_dia']
)
st.session_state.metricas = metricas

# Indicador de filtros activos
if st.session_state.filtros_aplicados:
    fecha_min_str = df['fecha'].min().strftime('%d/%m/%Y') if 'fecha' in df.columns and not df.empty else "N/A"
    fecha_max_str = df['fecha'].max().strftime('%d/%m/%Y') if 'fecha' in df.columns and not df.empty else "N/A"
    st.markdown(f"""
    <div class="alert-box info">
        <strong>🔍 Filtros activos:</strong> Mostrando {len(df)} de {len(st.session_state.df_original)} registros |
        Período: {fecha_min_str} - {fecha_max_str}
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 1: KPIs PRINCIPALES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🎯</span> INDICADORES CLAVE DE PERFORMANCE</div>",
            unsafe_allow_html=True)

color_disp = calcular_kpi_color(metricas['disponibilidad'], 'disponibilidad', config)
color_mtbf = calcular_kpi_color(metricas['mtbf_horas'], 'mtbf', config)
color_mttr = calcular_kpi_color(metricas['mttr_horas'], 'mttr', config)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(render_kpi_card(
        label="Disponibilidad",
        valor=f"{metricas['disponibilidad']:.2f}%",
        color_class=color_disp,
        icon="📈",
        subtext=f"Objetivo: ≥{config['umbral_disp_green']:.0f}% | {metricas['dias_analizados']} días analizados"
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
        color_primario=COLORES_INSTITUCIONALES['exito'] if metricas['disponibilidad'] >= config['umbral_disp_yellow'] else COLORES_INSTITUCIONALES['acento'],
        umbral_linea=config['umbral_disp_green']
    )
    st.plotly_chart(fig_gauge_disp, use_container_width=True)

with col_g2:
    max_mtbf = max(config['gauge_max_mtbf'], metricas['mtbf_horas'] * 1.2)
    fig_gauge_mtbf = crear_gauge_chart(
        metricas['mtbf_horas'],
        "MTBF (horas)",
        maximo=max_mtbf,
        color_primario=COLORES_INSTITUCIONALES['info'],
        umbral_linea=config['umbral_mtbf_green']
    )
    st.plotly_chart(fig_gauge_mtbf, use_container_width=True)

with col_g3:
    max_mttr = max(config['gauge_max_mttr'], metricas['mttr_horas'] * 1.2)
    fig_gauge_mttr = crear_gauge_chart(
        metricas['mttr_horas'],
        "MTTR (horas)",
        maximo=max_mttr,
        color_primario=COLORES_INSTITUCIONALES['peligro'] if metricas['mttr_horas'] > config['umbral_mttr_yellow'] else COLORES_INSTITUCIONALES['exito'],
        umbral_linea=config['umbral_mttr_yellow']
    )
    st.plotly_chart(fig_gauge_mttr, use_container_width=True)

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

# Verificar qué columnas están disponibles para Pareto
pareto_cols_disponibles = []
pareto_labels = []
if 'causa' in df.columns:
    pareto_cols_disponibles.append('causa')
    pareto_labels.append("🔴 Por Causa")
if 'estacion' in df.columns:
    pareto_cols_disponibles.append('estacion')
    pareto_labels.append("⚙️ Por Estación")
if 'sistema' in df.columns:
    pareto_cols_disponibles.append('sistema')
    pareto_labels.append("🔧 Por Sistema")
if 'parte' in df.columns:
    pareto_cols_disponibles.append('parte')
    pareto_labels.append("📦 Por Parte")
if 'turno' in df.columns:
    pareto_cols_disponibles.append('turno')
    pareto_labels.append("🕐 Por Turno")

if pareto_cols_disponibles:
    tab_pareto = st.tabs(pareto_labels)

    for i, col in enumerate(pareto_cols_disponibles):
        with tab_pareto[i]:
            color_map = {
                'causa': COLORES_INSTITUCIONALES['peligro'],
                'estacion': COLORES_INSTITUCIONALES['info'],
                'sistema': COLORES_INSTITUCIONALES['morado'],
                'parte': COLORES_INSTITUCIONALES['advertencia'],
                'turno': COLORES_INSTITUCIONALES['exito']
            }
            titulo_map = {
                'causa': "Pareto de Paradas por Causa de Avería",
                'estacion': "Pareto de Paradas por Estación",
                'sistema': "Pareto de Paradas por Sistema",
                'parte': "Pareto de Paradas por Parte/Componente",
                'turno': "Pareto de Paradas por Turno"
            }

            fig_pareto = crear_pareto(
                df, col, 'tiempo',
                titulo_map.get(col, f"Pareto por {col}"),
                top_n=15,
                color_barras=color_map.get(col, COLORES_INSTITUCIONALES['acento'])
            )
            st.plotly_chart(fig_pareto, use_container_width=True)

            with st.expander("📋 Ver tabla detallada"):
                tabla = df.groupby(col).agg({
                    'tiempo': ['sum', 'count', 'mean'],
                    'fecha': 'nunique'
                }).reset_index()
                tabla.columns = [col.capitalize(), 'Tiempo Total (min)', 'Cantidad', 'Tiempo Prom (min)', 'Días Afectados']
                total_tiempo = tabla['Tiempo Total (min)'].sum()
                tabla['% del Total'] = (tabla['Tiempo Total (min)'] / total_tiempo * 100).round(2) if total_tiempo > 0 else 0
                tabla = tabla.sort_values('Tiempo Total (min)', ascending=False)
                st.dataframe(tabla, use_container_width=True, hide_index=True)

                excel_data = generar_excel_descarga(tabla, f"Pareto_{col}")
                st.download_button(
                    label="📥 Descargar tabla Excel",
                    data=excel_data,
                    file_name=f"pareto_{col}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
else:
    st.info("ℹ️ No se encontraron columnas categóricas disponibles para el análisis de Pareto.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 5: TENDENCIAS TEMPORALES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📈</span> TENDENCIAS TEMPORALES</div>",
            unsafe_allow_html=True)

if 'fecha' in df.columns and not df.empty:
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
        fig_heatmap = crear_heatmap_calendario(df, columna_valor='tiempo',
                                               titulo="Mapa de Calor - Intensidad de Paradas por Día")
        st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("ℹ️ No se encontró información de fechas para análisis temporal.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 6: ANÁLISIS JERÁRQUICO Y DISTRIBUCIONES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🗂️</span> ANÁLISIS JERÁRQUICO Y DISTRIBUCIONES</div>",
            unsafe_allow_html=True)

col_j1, col_j2 = st.columns(2)

with col_j1:
    if 'estacion' in df.columns and 'sistema' in df.columns:
        st.markdown("<h4 style='color: #0f4c81; margin-bottom: 1rem;'>Treemap: Jerarquía Estación → Sistema</h4>",
                    unsafe_allow_html=True)
        fig_treemap = crear_treemap(
            df,
            path=['estacion', 'sistema'],
            valores='tiempo',
            titulo=""
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("ℹ️ Se requieren columnas 'estacion' y 'sistema' para el treemap.")

with col_j2:
    if 'causa' in df.columns and 'parte' in df.columns:
        st.markdown("<h4 style='color: #0f4c81; margin-bottom: 1rem;'>Sunburst: Causa → Parte</h4>",
                    unsafe_allow_html=True)
        fig_sun = crear_sunburst(
            df,
            path=['causa', 'parte'],
            valores='tiempo',
            titulo=""
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.info("ℹ️ Se requieren columnas 'causa' y 'parte' para el sunburst.")

st.markdown("<h4 style='color: #0f4c81; margin: 2rem 0 1rem 0;'>Distribución de Tiempos por Categoría</h4>",
            unsafe_allow_html=True)

col_b1, col_b2 = st.columns(2)

with col_b1:
    if 'causa' in df.columns:
        fig_box_causa = crear_analisis_caja(df, 'causa', 'tiempo',
                                            "Distribución de Tiempos por Causa")
        st.plotly_chart(fig_box_causa, use_container_width=True)
    else:
        st.info("ℹ️ Columna 'causa' no disponible.")

with col_b2:
    if 'estacion' in df.columns:
        fig_box_est = crear_analisis_caja(df, 'estacion', 'tiempo',
                                          "Distribución de Tiempos por Estación")
        st.plotly_chart(fig_box_est, use_container_width=True)
    else:
        st.info("ℹ️ Columna 'estacion' no disponible.")

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
    else:
        st.info("ℹ️ Se requieren columnas 'turno' y 'causa' para este análisis.")

with tab_cruzado[1]:
    if 'causa' in df.columns:
        scatter_data = df.groupby('causa').agg({
            'tiempo': ['sum', 'count', 'mean']
        }).reset_index()
        scatter_data.columns = ['causa', 'tiempo_total', 'cantidad', 'tiempo_promedio']
        scatter_data = scatter_data[scatter_data['cantidad'] >= 2]

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
        else:
            st.info("ℹ️ No hay suficientes datos para el gráfico de dispersión.")
    else:
        st.info("ℹ️ Columna 'causa' no disponible.")

with tab_cruzado[2]:
    if 'fecha' in df.columns and 'turno' in df.columns and not df.empty:
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
    else:
        st.info("ℹ️ Se requieren columnas 'fecha' y 'turno' para este análisis.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 8: ANÁLISIS DE TEXTO (NLP BÁSICO)
# ==============================================================================
if 'problema' in df.columns or 'trabajo' in df.columns:
    st.markdown("<div class='section-title'><span class='icon'>📝</span> ANÁLISIS DE DESCRIPCIONES</div>",
                unsafe_allow_html=True)

    tab_texto_disponibles = []
    tab_texto_labels = []
    if 'problema' in df.columns:
        tab_texto_disponibles.append('problema')
        tab_texto_labels.append("🔍 Problemas")
    if 'trabajo' in df.columns:
        tab_texto_disponibles.append('trabajo')
        tab_texto_labels.append("🔧 Trabajos Realizados")

    if tab_texto_disponibles:
        tab_texto = st.tabs(tab_texto_labels)

        for i, col in enumerate(tab_texto_disponibles):
            with tab_texto[i]:
                freq_data = analisis_texto_frecuencia(df, col, top_n=20)
                if not freq_data.empty:
                    color_scale = 'Oranges' if col == 'problema' else 'Blues'
                    titulo_texto = "Palabras más frecuentes en descripciones de problemas" if col == 'problema' else "Palabras más frecuentes en trabajos realizados"

                    fig_freq = px.bar(
                        freq_data,
                        x='Frecuencia',
                        y='Palabra',
                        orientation='h',
                        title=titulo_texto,
                        color='Frecuencia',
                        color_continuous_scale=color_scale,
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

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 9: TABLA DE DATOS CRUDA Y EXPORTACIÓN
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📑</span> DATOS DETALLADOS Y EXPORTACIÓN</div>",
            unsafe_allow_html=True)

with st.expander("📋 Ver tabla completa de datos", expanded=False):
    df_display = df.copy()
    if 'fecha' in df_display.columns:
        df_display['fecha'] = df_display['fecha'].dt.strftime('%d/%m/%Y')

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

recomendaciones = []

if metricas['disponibilidad'] < config['umbral_disp_yellow']:
    recomendaciones.append({
        'tipo': 'crítico',
        'icono': '🔴',
        'titulo': 'Disponibilidad Crítica',
        'mensaje': f"La disponibilidad actual es del {metricas['disponibilidad']:.1f}%, muy por debajo del objetivo del {config['umbral_disp_green']:.0f}%. Se requiere acción inmediata."
    })
elif metricas['disponibilidad'] < config['umbral_disp_green']:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'Disponibilidad por Debajo del Objetivo',
        'mensaje': f"La disponibilidad es del {metricas['disponibilidad']:.1f}%. Se recomienda planificar acciones de mejora para alcanzar el {config['umbral_disp_green']:.0f}%."
    })
else:
    recomendaciones.append({
        'tipo': 'exito',
        'icono': '🟢',
        'titulo': 'Disponibilidad Óptima',
        'mensaje': f"Excelente disponibilidad del {metricas['disponibilidad']:.1f}%. Mantener las prácticas actuales."
    })

if metricas['mtbf_horas'] < config['umbral_mtbf_yellow']:
    recomendaciones.append({
        'tipo': 'crítico',
        'icono': '🔴',
        'titulo': 'MTBF Muy Bajo',
        'mensaje': f"El MTBF es de solo {metricas['mtbf_horas']:.1f} horas. Las fallas son demasiado frecuentes. Priorizar análisis de causa raíz."
    })
elif metricas['mtbf_horas'] < config['umbral_mtbf_green']:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'MTBF Regular',
        'mensaje': f"MTBF de {metricas['mtbf_horas']:.1f} horas. Se recomienda implementar mantenimiento predictivo."
    })

if metricas['mttr_horas'] > config['umbral_mttr_yellow']:
    recomendaciones.append({
        'tipo': 'crítico',
        'icono': '🔴',
        'titulo': 'MTTR Elevado',
        'mensaje': f"El tiempo promedio de reparación es de {metricas['mttr_horas']:.1f} horas. Revisar procedimientos de mantenimiento y disponibilidad de repuestos."
    })
elif metricas['mttr_horas'] > config['umbral_mttr_green']:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'MTTR Regular',
        'mensaje': f"MTTR de {metricas['mttr_horas']:.1f} horas. Oportunidad de mejora en tiempos de respuesta."
    })

if 'causa' in df.columns:
    top_causa = df.groupby('causa')['tiempo'].sum().sort_values(ascending=False).head(1)
    if not top_causa.empty:
        causa_nombre = top_causa.index[0]
        causa_tiempo = top_causa.values[0]
        causa_pct = (causa_tiempo / metricas['tiempo_total_paradas']) * 100 if metricas['tiempo_total_paradas'] > 0 else 0

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

for rec in recomendaciones:
    color_map = {
        'crítico': '#fef2f2; border-left: 4px solid #dc2626;',
        'advertencia': '#fffbeb; border-left: 4px solid #f59e0b;',
        'exito': '#f0fdf4; border-left: 4px solid #16a34a;'
    }
    st.markdown(f"""
    <div style="{color_map[rec['tipo']]} padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.5rem 0; color: #0f172a;">{rec['icono']} {rec['titulo']}</h4>
        <p style="margin: 0; color: #475569;">{rec['mensaje']}</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN 11: FOOTER INSTITUCIONAL
# ==============================================================================
st.markdown("""
<div class="footer">
    <p><strong>🏭 CAVA Especialistas en Robotica y Automatizacion</strong></p>
    <p>Dashboard Performance de Línea v3.3.0 | Desarrollado por Roger Huamani</p>
    <p style="margin-top: 0.5rem; font-size: 0.75rem;">
        © 2026 | Compatible con SharePoint y archivos Excel estándar |
        Métricas calculadas según estándares SMRP e ISO 14224
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FIN DEL SCRIPT
# ==============================================================================
