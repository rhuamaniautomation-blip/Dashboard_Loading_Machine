
"""
================================================================================
DASHBOARD PROFESIONAL DE PERFORMANCE DE LINEA - STREAMLIT CLOUD v3.1.0
================================================================================
CORRECCIONES v3.1.0:
- Fix SharePoint: Conversion automatica de URLs de vista previa a download directo
- Fix Plotly Heatmap: colorbar.title.side en lugar de titleside (deprecated)
- Nuevo: Exportacion a PDF formato A4 con Paretos y analisis detallado
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import re
import requests
from urllib.parse import urlparse
from io import BytesIO
import math

# Librerias para PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image as RLImage, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Dashboard Performance de Linea | Gerencia",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Dashboard Profesional de Performance de Linea v3.1.0"
    }
)

# ==============================================================================
# CSS PERSONALIZADO INSTITUCIONAL
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }

    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2c5282 50%, #1e3a5f 100%);
        padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3); border-left: 6px solid #e67e22;
    }
    .main-header h1 {
        color: #ffffff !important; font-size: 2.2rem !important;
        font-weight: 800 !important; margin: 0 !important; letter-spacing: -0.5px; text-transform: uppercase;
    }
    .main-header h2 {
        color: #94a3b8 !important; font-size: 1.1rem !important;
        font-weight: 400 !important; margin: 0.5rem 0 0 0 !important;
    }
    .main-header .badge {
        background: #e67e22; color: white; padding: 4px 12px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 600;
        display: inline-block; margin-top: 8px;
    }

    .kpi-container {
        background: white; border-radius: 16px; padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
        transition: all 0.3s ease; height: 100%; position: relative; overflow: hidden;
    }
    .kpi-container:hover {
        transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }
    .kpi-container::before {
        content: ''; position: absolute; top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, #e67e22, #d35400);
    }
    .kpi-container.green::before { background: linear-gradient(180deg, #27ae60, #219a52); }
    .kpi-container.blue::before { background: linear-gradient(180deg, #3498db, #2980b9); }
    .kpi-container.red::before { background: linear-gradient(180deg, #e74c3c, #c0392b); }
    .kpi-container.purple::before { background: linear-gradient(180deg, #9b59b6, #8e44ad); }

    .kpi-label {
        font-size: 0.85rem; color: #64748b; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 2.4rem; font-weight: 800; color: #1e293b;
        line-height: 1.2; margin-bottom: 0.5rem;
    }
    .kpi-subtext { font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem; }

    .section-card {
        background: white; border-radius: 16px; padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; margin-bottom: 1.5rem;
    }
    .section-title {
        font-size: 1.3rem; font-weight: 700; color: #1e3a5f;
        margin-bottom: 1.5rem; padding-bottom: 0.75rem;
        border-bottom: 3px solid #e67e22; display: flex; align-items: center; gap: 10px;
    }
    .section-title .icon { font-size: 1.5rem; }

    .alert-box {
        padding: 1rem 1.5rem; border-radius: 12px; margin: 1rem 0;
        border-left: 4px solid; font-weight: 500;
    }
    .alert-box.info { background: #eff6ff; border-color: #3b82f6; color: #1e40af; }
    .alert-box.success { background: #f0fdf4; border-color: #22c55e; color: #166534; }
    .alert-box.warning { background: #fffbeb; border-color: #f59e0b; color: #92400e; }
    .alert-box.error { background: #fef2f2; border-color: #ef4444; color: #991b1b; }

    .footer {
        text-align: center; padding: 2rem; color: #64748b;
        font-size: 0.85rem; border-top: 1px solid #e2e8f0; margin-top: 3rem;
    }
    .footer strong { color: #1e3a5f; }

    .divider {
        height: 3px; background: linear-gradient(90deg, transparent, #e67e22, transparent);
        margin: 2rem 0; border-radius: 2px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in { animation: fadeIn 0.6s ease-out forwards; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.5rem !important; }
        .kpi-value { font-size: 1.8rem; }
    }
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
    'estacion': ['ESTACION', 'Estacion', 'estacion', 'STATION', 'Station', 'AREA', 'Area'],
    'sistema': ['SISTEMA', 'Sistema', 'sistema', 'SYSTEM', 'System'],
    'parte': ['PARTE', 'Parte', 'parte', 'PART', 'Part', 'COMPONENTE', 'Componente'],
    'causa': ['CAUSA DE AVERIA', 'CAUSA DE AVERÍA', 'Causa de averia', 'causa', 
              'CAUSA', 'Causa', 'CAUSE', 'Cause', 'MODO FALLA', 'Modo Falla'],
    'problema': ['DESCRIPCION DEL PROBLEMA', 'DESCRIPCIÓN DEL PROBLEMA', 'Descripcion del problema',
                 'problema', 'PROBLEMA', 'Problema', 'FALLA', 'Falla', 'DESCRIPCION'],
    'trabajo': ['DESCRIPCION DEL TRABAJO', 'DESCRIPCIÓN DEL TRABAJO', 'Descripcion del trabajo',
                'trabajo', 'TRABAJO', 'Trabajo', 'ACCION', 'Accion', 'SOLUCION']
}

COLORES_INSTITUCIONALES = {
    'primario': '#1e3a5f', 'secundario': '#2c5282', 'acento': '#e67e22',
    'exito': '#27ae60', 'peligro': '#e74c3c', 'advertencia': '#f39c12',
    'info': '#3498db', 'morado': '#9b59b6', 'gris': '#95a5a6',
    'paleta': ['#1e3a5f', '#e67e22', '#27ae60', '#e74c3c', '#9b59b6', 
               '#3498db', '#f39c12', '#1abc9c', '#34495e', '#e91e63']
}

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

DIAS_ES = {0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves',
           4: 'Viernes', 5: 'Sabado', 6: 'Domingo'}

# ==============================================================================
# FUNCIONES DE UTILIDAD Y AYUDA
# ==============================================================================
def detectar_columnas(df):
    """Detecta automaticamente las columnas del DataFrame."""
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
    """Convierte valores de fecha de Excel a datetime."""
    if pd.isna(valor):
        return pd.NaT

    if isinstance(valor, (int, float)):
        try:
            return pd.Timestamp('1899-12-30') + pd.Timedelta(days=int(valor))
        except:
            return pd.NaT

    if isinstance(valor, str):
        formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y',
                    '%d/%m/%y', '%Y/%m/%d', '%d.%m.%Y', '%Y%m%d']
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
    """Limpia y estandariza el DataFrame para analisis."""
    df_limpio = df.copy()

    primera_fila = df_limpio.iloc[0].astype(str).str.strip().str.lower()
    if any(primera_fila.isin(['fecha', 'turno', 'aviso', 'tiempo'])):
        df_limpio = df_limpio.iloc[1:].reset_index(drop=True)

    rename_map = {v: k for k, v in columnas_map.items()}
    df_limpio = df_limpio.rename(columns=rename_map)

    if 'fecha' in df_limpio.columns:
        df_limpio['fecha'] = df_limpio['fecha'].apply(convertir_fecha_excel)
        df_limpio = df_limpio.dropna(subset=['fecha'])
        df_limpio['fecha'] = pd.to_datetime(df_limpio['fecha'], errors='coerce')

    if 'tiempo' in df_limpio.columns:
        df_limpio['tiempo'] = pd.to_numeric(df_limpio['tiempo'], errors='coerce')
        df_limpio = df_limpio[df_limpio['tiempo'] > 0]
        df_limpio['tiempo_horas'] = df_limpio['tiempo'] / 60.0

    for col in ['turno', 'maquina', 'estacion', 'sistema', 'parte', 'causa']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace(['nan', 'None', ''], 'No Especificado')

    for col in ['problema', 'trabajo']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace(['nan', 'None'], '')

    if 'fecha' in df_limpio.columns:
        df_limpio['anio'] = df_limpio['fecha'].dt.year
        df_limpio['mes'] = df_limpio['fecha'].dt.month
        df_limpio['mes_nombre'] = df_limpio['mes'].map(MESES_ES)
        df_limpio['dia_semana'] = df_limpio['fecha'].dt.dayofweek
        df_limpio['dia_nombre'] = df_limpio['dia_semana'].map(DIAS_ES)
        df_limpio['semana'] = df_limpio['fecha'].dt.isocalendar().week
        df_limpio['dia_mes'] = df_limpio['fecha'].dt.day
        df_limpio['trimestre'] = df_limpio['fecha'].dt.quarter
        df_limpio['anio_mes'] = df_limpio['fecha'].dt.to_period('M').astype(str)

    if 'fecha' in df_limpio.columns:
        df_limpio = df_limpio.sort_values('fecha').reset_index(drop=True)

    return df_limpio


def convertir_url_sharepoint(url):
    """
    Convierte URL de vista previa de SharePoint a URL de descarga directa.
    Las URLs de SharePoint compartidas son URLs de vista previa, no directas.
    """
    if not url or not isinstance(url, str):
        return url

    url = url.strip()

    # Si ya es download.aspx, retornar
    if 'download.aspx' in url.lower():
        return url

    # Extraer sourcedoc/UniqueId
    sourcedoc_match = re.search(r'sourcedoc=\{([^}]+)\}', url)
    if sourcedoc_match:
        unique_id = sourcedoc_match.group(1)
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return f"{base_url}/_layouts/15/download.aspx?UniqueId={unique_id}"

    # Formato moderno /:x:/
    if '/:x:/' in url or '/:w:/' in url or '/:f:/' in url:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        clean_path = re.sub(r'^/:[xwf]:/r', '', parsed.path)
        direct_url = f"{base_url}{clean_path}"
        if '?' in direct_url:
            return direct_url + "&download=1"
        return direct_url + "?download=1"

    # Cualquier URL de sharepoint
    if 'sharepoint.com' in url.lower():
        if '?' in url:
            return url + "&download=1"
        return url + "?download=1"

    return url


def descargar_desde_url(url):
    """Descarga archivo Excel desde URL con soporte SharePoint."""
    try:
        url_procesada = convertir_url_sharepoint(url)

        if url_procesada != url:
            st.info("Convirtiendo URL de SharePoint a descarga directa...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, */*'
        }

        response = requests.get(url_procesada, headers=headers, timeout=60, allow_redirects=True)

        if response.status_code == 200:
            content = BytesIO(response.content)
            return content
        else:
            st.error(f"Error HTTP {response.status_code}")
            if response.status_code == 401:
                st.info("El archivo requiere autenticacion. Use carga local o comparta con acceso publico.")
            return None

    except requests.exceptions.Timeout:
        st.error("Tiempo de espera agotado.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Error de conexion.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def leer_excel_con_fallback(archivo_bytes, sheet_name=0):
    """Lee Excel intentando multiples motores."""
    motores = ['openpyxl', 'xlrd']

    for motor in motores:
        try:
            archivo_bytes.seek(0)
            df = pd.read_excel(archivo_bytes, sheet_name=sheet_name, engine=motor)
            return df
        except Exception:
            continue

    try:
        archivo_bytes.seek(0)
        df = pd.read_excel(archivo_bytes, sheet_name=sheet_name)
        return df
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {str(e)}")
        st.info("Sugerencias: Verifique que no este corrupto. Intente carga local.")
        return None


def generar_excel_descarga(df, nombre_hoja='Reporte'):
    """Genera archivo Excel en memoria."""
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


def calcular_kpi_color(valor, tipo='disponibilidad'):
    """Determina color de KPI segun umbrales."""
    if tipo == 'disponibilidad':
        if valor >= 95: return 'green'
        elif valor >= 85: return 'yellow'
        else: return 'red'
    elif tipo == 'mtbf':
        if valor >= 8: return 'green'
        elif valor >= 4: return 'yellow'
        else: return 'red'
    elif tipo == 'mttr':
        if valor <= 1: return 'green'
        elif valor <= 3: return 'yellow'
        else: return 'red'
    return 'blue'


def formato_numero(valor, decimales=2, sufijo=''):
    """Formatea numero para KPIs."""
    if pd.isna(valor) or valor == 0:
        return f"0{sufijo}"
    if valor >= 1000000:
        return f"{valor/1000000:.{decimales}f}M{sufijo}"
    elif valor >= 1000:
        return f"{valor/1000:.{decimales}f}K{sufijo}"
    else:
        return f"{valor:.{decimales}f}{sufijo}"

def crear_gauge_chart(valor, titulo, maximo=100, color_primario=None):
    """Crea gauge profesional con Plotly."""
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
        height=280, margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'}
    )
    return fig


def crear_pareto(df, columna_categoria, columna_valor, titulo, top_n=15, color_barras=None):
    """Crea grafico de Pareto con barras y linea acumulada."""
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
            textfont={'size': 11, 'color': '#1e293b'},
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
        y=80, line_dash="dash", line_color="#e74c3c", line_width=2,
        secondary_y=True,
        annotation_text="Regla 80/20", 
        annotation_position="right",
        annotation_font_color="#e74c3c"
    )

    fig.update_layout(
        title={'text': f"<b>{titulo}</b>", 'font': {'size': 20, 'color': '#1e293b', 'family': 'Inter'}, 'x': 0.5},
        xaxis_title="", yaxis_title="Tiempo Total (minutos)", yaxis2_title="Porcentaje Acumulado (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500, template='plotly_white', hovermode='x unified',
        margin=dict(l=60, r=60, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_xaxes(tickangle=-35, tickfont={'size': 11}, gridcolor='#f1f5f9')
    fig.update_yaxes(gridcolor='#f1f5f9', secondary_y=False)
    fig.update_yaxes(range=[0, 105], ticksuffix='%', secondary_y=True)

    return fig


def crear_tendencia_temporal(df, agrupacion='D', titulo="Tendencia Temporal"):
    """Grafico de tendencia temporal."""
    df_temp = df.copy()
    df_temp['periodo'] = df_temp['fecha'].dt.to_period(agrupacion)

    resumen = df_temp.groupby('periodo').agg({
        'tiempo': ['sum', 'count', 'mean'],
        'fecha': 'nunique'
    }).reset_index()

    resumen.columns = ['periodo', 'tiempo_total', 'cantidad_paradas', 'tiempo_promedio', 'dias_activos']
    resumen['periodo_str'] = resumen['periodo'].astype(str)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
        subplot_titles=('Tiempo Total de Paradas (min)', 'Cantidad de Paradas')
    )

    fig.add_trace(
        go.Bar(x=resumen['periodo_str'], y=resumen['tiempo_total'], name='Tiempo Total',
               marker_color=COLORES_INSTITUCIONALES['acento'],
               text=resumen['tiempo_total'].round(0).astype(int),
               textposition='outside',
               hovertemplate='<b>%{x}</b><br>Tiempo Total: %{y:.0f} min<extra></extra>'),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=resumen['periodo_str'], y=resumen['tiempo_total'], mode='lines',
                   line={'color': COLORES_INSTITUCIONALES['primario'], 'width': 2, 'dash': 'dot'},
                   name='Tendencia', showlegend=False), row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=resumen['periodo_str'], y=resumen['cantidad_paradas'], name='N Paradas',
               marker_color=COLORES_INSTITUCIONALES['info'],
               text=resumen['cantidad_paradas'].astype(int),
               textposition='outside',
               hovertemplate='<b>%{x}</b><br>Paradas: %{y}<extra></extra>'),
        row=2, col=1
    )

    fig.update_layout(
        title={'text': f"<b>{titulo}</b>", 'font': {'size': 20, 'color': '#1e293b', 'family': 'Inter'}, 'x': 0.5},
        height=600, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white', hovermode='x unified',
        margin=dict(l=60, r=40, t=100, b=60),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_xaxes(tickangle=-45, row=2, col=1)
    fig.update_yaxes(gridcolor='#f1f5f9', row=1, col=1)
    fig.update_yaxes(gridcolor='#f1f5f9', row=2, col=1)

    return fig


def crear_heatmap_calendario(df, columna_valor='tiempo', titulo="Mapa de Calor - Calendario"):
    """
    Crea heatmap de calendario. 
    FIX v3.1.0: colorbar title usa dict con 'text' en lugar de 'titleside'.
    """
    df_cal = df.copy()
    df_cal['dia_semana'] = df_cal['fecha'].dt.dayofweek
    df_cal['semana_anio'] = df_cal['fecha'].dt.isocalendar().week.astype(int)
    df_cal['mes'] = df_cal['fecha'].dt.month

    pivot = df_cal.groupby(['semana_anio', 'dia_semana'])[columna_valor].sum().reset_index()

    if pivot.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos suficientes", showarrow=False, font_size=20)
        return fig

    pivot_pivot = pivot.pivot(index='semana_anio', columns='dia_semana', values=columna_valor).fillna(0)

    dias_labels = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']

    # FIX: Usar colorbar con title como dict con 'text' en vez de 'titleside'
    fig = go.Figure(data=go.Heatmap(
        z=pivot_pivot.values,
        x=dias_labels[:pivot_pivot.shape[1]] if pivot_pivot.shape[1] <= 7 else dias_labels,
        y=[f"Sem {s}" for s in pivot_pivot.index],
        colorscale=[
            [0, '#f0fdf4'], [0.2, '#fef3c7'], [0.5, '#fdba74'],
            [0.8, '#ef4444'], [1, '#7f1d1d']
        ],
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.0f} min<extra></extra>',
        colorbar=dict(
            title=dict(text="Minutos"),
            titleside="right"
        )
    ))

    fig.update_layout(
        title={'text': f"<b>{titulo}</b>", 'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=500, template='plotly_white',
        margin=dict(l=60, r=40, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def crear_analisis_caja(df, columna_categoria, columna_valor, titulo):
    """Boxplot para analisis de distribucion."""
    categorias = df[columna_categoria].value_counts().head(10).index.tolist()
    df_filtrado = df[df[columna_categoria].isin(categorias)]

    fig = px.box(
        df_filtrado, x=columna_categoria, y=columna_valor,
        color=columna_categoria,
        color_discrete_sequence=COLORES_INSTITUCIONALES['paleta'],
        title=titulo,
        labels={columna_categoria: '', columna_valor: 'Tiempo (minutos)'}
    )

    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=450, template='plotly_white', showlegend=False,
        margin=dict(l=60, r=40, t=60, b=80),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-35
    )
    return fig


def calcular_mtbf_mttr_disponibilidad(df, minutos_turno=480, turnos_por_dia=2):
    """Calcula MTBF, MTTR y Disponibilidad."""
    if df.empty:
        return {
            'mtbf_horas': 0, 'mttr_horas': 0, 'mtbf_minutos': 0, 'mttr_minutos': 0,
            'disponibilidad': 0, 'tiempo_total_paradas': 0, 'tiempo_operativo_total': 0,
            'total_fallas': 0, 'tiempo_promedio_parada': 0
        }

    fecha_inicio = df['fecha'].min()
    fecha_fin = df['fecha'].max()
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

    if (mtbf_minutos + mttr_minutos) > 0:
        disponibilidad = (mtbf_minutos / (mtbf_minutos + mttr_minutos)) * 100
    else:
        disponibilidad = 100.0

    return {
        'mtbf_horas': mtbf_minutos / 60.0,
        'mttr_horas': mttr_minutos / 60.0,
        'mtbf_minutos': mtbf_minutos,
        'mttr_minutos': mttr_minutos,
        'disponibilidad': disponibilidad,
        'tiempo_total_paradas': tiempo_total_paradas,
        'tiempo_operativo_total': tiempo_operativo,
        'total_fallas': total_fallas,
        'tiempo_promedio_parada': df['tiempo'].mean() if total_fallas > 0 else 0,
        'dias_analizados': dias_totales,
        'tiempo_programado': tiempo_programado
    }

def analisis_texto_frecuencia(df, columna_texto, top_n=20):
    """Analisis de frecuencia de palabras en descripciones."""
    if columna_texto not in df.columns:
        return pd.DataFrame()

    textos = df[columna_texto].dropna().astype(str)
    textos = textos[textos.str.len() > 3]

    if textos.empty:
        return pd.DataFrame()

    stopwords = {
        'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para',
        'con', 'no', 'una', 'su', 'al', 'lo', 'mas', 'pero', 'sus', 'le', 'ya', 'o', 'este',
        'si', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'tambien', 'me',
        'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos',
        'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto',
        'mi', 'antes', 'algunos', 'que', 'unos', 'yo', 'otro', 'otras', 'otra', 'el', 'tanto',
        'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar',
        'estas', 'algunas', 'algo', 'nosotros', 'mis', 'tu', 'te', 'ti', 'tus',
        'ellas', 'os', 'mio', 'mia', 'mios', 'mias', 'tuyo', 'tuya', 'tuyos', 'tuyas',
        'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras',
        'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas',
        'estoy', 'estas', 'esta', 'estamos', 'estais', 'estan', 'este', 'estes', 'estemos',
        'esteis', 'esten', 'estare', 'estaras', 'estara', 'estaremos', 'estareis', 'estaran',
        'estaria', 'estarias', 'estariamos', 'estariais', 'estarian', 'estaba', 'estabas',
        'estabamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos',
        'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras', 'estuvieramos', 'estuvierais',
        'estuvieran', 'estuviese', 'estuvieses', 'estuviesemos', 'estuvieseis', 'estuviesen',
        'estando', 'estado', 'estada', 'estados', 'estadas', 'estad', 'he', 'has', 'ha',
        'hemos', 'habeis', 'han', 'haya', 'hayas', 'hayamos', 'hayais', 'hayan', 'habre',
        'habras', 'habra', 'habremos', 'habreis', 'habran', 'habria', 'habrias', 'habriamos',
        'habriais', 'habrian', 'habia', 'habias', 'habiamos', 'habiais', 'habian', 'hube',
        'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
        'hubieramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiesemos',
        'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
        'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seais',
        'sean', 'sere', 'seras', 'sera', 'seremos', 'sereis', 'seran', 'seria', 'serias',
        'seriamos', 'seriais', 'serian', 'era', 'eras', 'eramos', 'erais', 'eran', 'fui',
        'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera', 'fueras', 'fueramos',
        'fuerais', 'fueran', 'fuese', 'fueses', 'fuesemos', 'fueseis', 'fuesen', 'siendo',
        'sido', 'tengo', 'tienes', 'tiene', 'tenemos', 'teneis', 'tienen', 'tenga', 'tengas',
        'tengamos', 'tengais', 'tengan', 'tendre', 'tendras', 'tendra', 'tendremos',
        'tendreis', 'tendran', 'tendria', 'tendrias', 'tendriamos', 'tendriais', 'tendrian',
        'tenia', 'tenias', 'teniamos', 'teniais', 'tenian', 'tuve', 'tuviste', 'tuvo',
        'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuvieramos', 'tuvierais',
        'tuvieran', 'tuviese', 'tuvieses', 'tuviesemos', 'tuvieseis', 'tuviesen', 'teniendo',
        'tenido', 'tenida', 'tenidos', 'tenidas', 'tened'
    }

    todas_palabras = []
    for texto in textos:
        palabras = re.findall(r'\b[a-zA-ZaeiouunAEIOUUN]{4,}\b', texto.lower())
        palabras = [p for p in palabras if p not in stopwords]
        todas_palabras.extend(palabras)

    if not todas_palabras:
        return pd.DataFrame()

    freq = pd.Series(todas_palabras).value_counts().head(top_n).reset_index()
    freq.columns = ['Palabra', 'Frecuencia']
    return freq


def crear_treemap(df, path, valores, titulo):
    """Treemap jerarquico para analisis drill-down."""
    fig = px.treemap(
        df, path=path, values=valores, color=valores,
        color_continuous_scale=['#f0fdf4', '#dcfce7', '#86efac', '#22c55e', '#16a34a', '#15803d', '#166534'],
        title=titulo
    )
    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=500, margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_traces(
        textfont={'size': 13, 'family': 'Inter'},
        hovertemplate='<b>%{label}</b><br>Tiempo: %{value:.0f} min<extra></extra>'
    )
    return fig


def crear_sunburst(df, path, valores, titulo):
    """Sunburst para analisis jerarquico circular."""
    fig = px.sunburst(
        df, path=path, values=valores, color=valores,
        color_continuous_scale='Blues', title=titulo
    )
    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=550, margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_traces(
        textfont={'size': 12, 'family': 'Inter'},
        hovertemplate='<b>%{label}</b><br>Tiempo: %{value:.0f} min<extra></extra>'
    )
    return fig


def crear_grafico_barras_apiladas(df, eje_x, eje_y, color, titulo):
    """Barras apiladas para comparacion cruzada."""
    fig = px.bar(
        df, x=eje_x, y=eje_y, color=color,
        title=titulo,
        color_discrete_sequence=COLORES_INSTITUCIONALES['paleta'],
        barmode='stack'
    )
    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=450, template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=100, b=80),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-35
    )
    return fig


def crear_grafico_dispersion(df, x, y, color, size, titulo):
    """Grafico de dispersion para analisis de correlacion."""
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size,
        title=titulo,
        color_discrete_sequence=COLORES_INSTITUCIONALES['paleta'],
        hover_data=[x, y, color, size]
    )
    fig.update_layout(
        title={'font': {'size': 18, 'color': '#1e293b'}, 'x': 0.5},
        height=450, template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=100, b=60),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def resumen_ejecutivo_texto(df, metricas):
    """Genera resumen ejecutivo para gerencia."""
    fecha_inicio = df['fecha'].min().strftime('%d/%m/%Y')
    fecha_fin = df['fecha'].max().strftime('%d/%m/%Y')

    top_causas = df.groupby('causa')['tiempo'].sum().sort_values(ascending=False).head(3)
    top_estaciones = df.groupby('estacion')['tiempo'].sum().sort_values(ascending=False).head(3)

    resumen = f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%); 
                padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;">
        <h3 style="color: #e67e22; margin-bottom: 1rem; font-size: 1.4rem;">RESUMEN EJECUTIVO</h3>
        <p style="font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            Periodo: <strong>{fecha_inicio} - {fecha_fin}</strong> | 
            <strong>{metricas['total_fallas']} eventos</strong> | 
            <strong>{metricas['tiempo_total_paradas']:.0f} min ({metricas['tiempo_total_paradas']/60:.1f} h)</strong> de parada.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            <strong>Disponibilidad: {metricas['disponibilidad']:.2f}%</strong> | 
            MTBF: {metricas['mtbf_horas']:.2f}h | 
            MTTR: {metricas['mttr_horas']:.2f}h
        </p>
        <div style="margin-top: 1.5rem;">
            <h4 style="color: #e67e22; font-size: 1.1rem;">Top Causas:</h4>
            <ul style="line-height: 1.8;">
    """

    for causa, tiempo in top_causas.items():
        pct = (tiempo / metricas['tiempo_total_paradas']) * 100
        resumen += f"                <li><strong>{causa}</strong>: {tiempo:.0f} min ({pct:.1f}%)</li>\n"

    resumen += """            </ul>
        </div>
        <div style="margin-top: 1.5rem;">
            <h4 style="color: #e67e22; font-size: 1.1rem;">Top Estaciones:</h4>
            <ul style="line-height: 1.8;">
    """

    for est, tiempo in top_estaciones.items():
        pct = (tiempo / metricas['tiempo_total_paradas']) * 100
        resumen += f"                <li><strong>{est}</strong>: {tiempo:.0f} min ({pct:.1f}%)</li>\n"

    resumen += """            </ul>
        </div>
    </div>
    """
    return resumen


def render_kpi_card(label, valor, subtext="", color_class="", icon=""):
    """Renderiza tarjeta KPI HTML."""
    return f"""
    <div class="kpi-container {color_class} animate-in">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """

# ==============================================================================
# FUNCIONES DE GENERACION DE PDF PROFESIONAL FORMATO A4
# ==============================================================================
def generar_pdf_reporte(df, metricas, nombre_maquina="Linea"):
    """
    Genera un reporte PDF profesional en formato A4 con Paretos y analisis detallado.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos filtrados
    metricas : dict
        Diccionario con metricas calculadas
    nombre_maquina : str
        Nombre de la maquina o linea

    Retorna:
    --------
    bytes : Contenido del PDF
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_principal = ParagraphStyle(
        'TituloPrincipal',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#1e3a5f'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#e67e22'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=HexColor('#e67e22'),
        borderWidth=1,
        borderPadding=5
    )

    texto_normal = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY
    )

    texto_kpi = ParagraphStyle(
        'KPI',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )

    story = []

    # ===== PORTADA =====
    story.append(Paragraph(
        f"<b>REPORTE DE PERFORMANCE</b><br/><font size=12 color='#64748b'>{nombre_maquina}</font>",
        titulo_principal
    ))

    fecha_reporte = datetime.now().strftime('%d/%m/%Y %H:%M')
    story.append(Paragraph(
        f"<font size=8 color='#64748b'>Generado: {fecha_reporte}</font>",
        ParagraphStyle('Fecha', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8)
    ))
    story.append(Spacer(1, 1*cm))

    # ===== SECCION 1: RESUMEN =====
    story.append(Paragraph("RESUMEN EJECUTIVO", subtitulo))

    fecha_inicio = df['fecha'].min().strftime('%d/%m/%Y')
    fecha_fin = df['fecha'].max().strftime('%d/%m/%Y')

    resumen = f"""
    <b>Periodo:</b> {fecha_inicio} - {fecha_fin}<br/>
    <b>Dias Analizados:</b> {metricas['dias_analizados']}<br/>
    <b>Total Eventos:</b> {metricas['total_fallas']} paradas<br/>
    <b>Tiempo Total Parada:</b> {metricas['tiempo_total_paradas']:.0f} min ({metricas['tiempo_total_paradas']/60:.1f} h)<br/>
    <b>Tiempo Promedio/Parada:</b> {metricas['tiempo_promedio_parada']:.1f} min
    """
    story.append(Paragraph(resumen, texto_normal))
    story.append(Spacer(1, 0.5*cm))

    # ===== SECCION 2: KPIs =====
    story.append(Paragraph("INDICADORES CLAVE", subtitulo))

    kpi_data = [
        ['Indicador', 'Valor', 'Estado', 'Referencia'],
        ['Disponibilidad', f"{metricas['disponibilidad']:.2f}%", 
         'OPTIMO' if metricas['disponibilidad'] >= 95 else ('REGULAR' if metricas['disponibilidad'] >= 85 else 'CRITICO'),
         '>= 95%'],
        ['MTBF', f"{metricas['mtbf_horas']:.2f} h",
         'OPTIMO' if metricas['mtbf_horas'] >= 8 else ('REGULAR' if metricas['mtbf_horas'] >= 4 else 'CRITICO'),
         '>= 8 h'],
        ['MTTR', f"{metricas['mttr_horas']:.2f} h",
         'OPTIMO' if metricas['mttr_horas'] <= 1 else ('REGULAR' if metricas['mttr_horas'] <= 3 else 'CRITICO'),
         '<= 1 h'],
        ['Total Paradas', f"{metricas['total_fallas']}", '-', '-'],
        ['Tiempo Promedio', f"{metricas['tiempo_promedio_parada']:.1f} min", '-', '-']
    ]

    kpi_table = Table(kpi_data, colWidths=[5*cm, 3.5*cm, 3*cm, 3*cm])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f1f5f9')]),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.8*cm))

    # ===== SECCION 3: PARETO POR CAUSA =====
    story.append(Paragraph("PARETO - CAUSAS DE PARADA", subtitulo))

    if 'causa' in df.columns:
        pareto_causas = df.groupby('causa')['tiempo'].sum().sort_values(ascending=False).head(10)
        total_tiempo = pareto_causas.sum()

        pareto_data = [['Causa', 'Tiempo (min)', '% del Total', 'Acumulado %']]
        acumulado = 0
        for causa, tiempo in pareto_causas.items():
            pct = (tiempo / total_tiempo) * 100
            acumulado += pct
            pareto_data.append([
                str(causa)[:40],
                f"{tiempo:.0f}",
                f"{pct:.1f}%",
                f"{acumulado:.1f}%"
            ])

        pareto_table = Table(pareto_data, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
        pareto_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e67e22')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#fff7ed')]),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(pareto_table)
        story.append(Spacer(1, 0.5*cm))

        # Nota sobre regla 80/20
        story.append(Paragraph(
            f"<font size=8 color='#64748b'><i>Regla 80/20: Las principales causas representan el {acumulado:.1f}% del tiempo total de parada.</i></font>",
            ParagraphStyle('Nota', parent=styles['Normal'], fontSize=8, textColor=HexColor('#64748b'))
        ))

    story.append(PageBreak())

    # ===== SECCION 4: PARETO POR ESTACION =====
    story.append(Paragraph("PARETO - ESTACIONES CRITICAS", subtitulo))

    if 'estacion' in df.columns:
        pareto_est = df.groupby('estacion')['tiempo'].sum().sort_values(ascending=False).head(10)
        total_tiempo_est = pareto_est.sum()

        est_data = [['Estacion', 'Tiempo (min)', '% del Total', 'Acumulado %']]
        acum_est = 0
        for est, tiempo in pareto_est.items():
            pct = (tiempo / total_tiempo_est) * 100
            acum_est += pct
            est_data.append([
                str(est)[:40],
                f"{tiempo:.0f}",
                f"{pct:.1f}%",
                f"{acum_est:.1f}%"
            ])

        est_table = Table(est_data, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
        est_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#eff6ff')]),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(est_table)

    story.append(Spacer(1, 0.8*cm))

    # ===== SECCION 5: INCIDENCIAS DETALLADAS =====
    story.append(Paragraph("INCIDENCIAS DETALLADAS (TOP 15)", subtitulo))

    # Top 15 eventos mas largos
    top_eventos = df.nlargest(15, 'tiempo')[['fecha', 'turno', 'estacion', 'sistema', 'parte', 'causa', 'tiempo', 'problema']].copy()
    top_eventos['fecha_str'] = top_eventos['fecha'].dt.strftime('%d/%m/%Y')

    eventos_data = [['Fecha', 'Turno', 'Estacion', 'Causa', 'Tiempo (min)', 'Descripcion']]
    for _, row in top_eventos.iterrows():
        desc = str(row.get('problema', ''))[:50] if pd.notna(row.get('problema', '')) else ''
        eventos_data.append([
            row['fecha_str'],
            str(row.get('turno', ''))[:10],
            str(row.get('estacion', ''))[:20],
            str(row.get('causa', ''))[:20],
            f"{row['tiempo']:.0f}",
            desc
        ])

    eventos_table = Table(eventos_data, colWidths=[2*cm, 2*cm, 3.5*cm, 3*cm, 2*cm, 5.5*cm])
    eventos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f8fafc')]),
        ('ALIGN', (0, 1), (3, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(eventos_table)

    story.append(Spacer(1, 0.5*cm))

    # ===== SECCION 6: RECOMENDACIONES =====
    story.append(Paragraph("RECOMENDACIONES", subtitulo))

    recomendaciones = []
    if metricas['disponibilidad'] < 85:
        recomendaciones.append("Disponibilidad CRITICA. Se requiere accion inmediata.")
    elif metricas['disponibilidad'] < 95:
        recomendaciones.append("Disponibilidad por debajo del objetivo. Planificar mejoras.")

    if metricas['mtbf_horas'] < 4:
        recomendaciones.append("MTBF muy bajo. Priorizar analisis de causa raiz.")

    if metricas['mttr_horas'] > 3:
        recomendaciones.append("MTTR elevado. Revisar procedimientos y disponibilidad de repuestos.")

    if not recomendaciones:
        recomendaciones.append("Performance dentro de parametros aceptables. Mantener practicas actuales.")

    for i, rec in enumerate(recomendaciones, 1):
        story.append(Paragraph(f"{i}. {rec}", texto_normal))
        story.append(Spacer(1, 0.2*cm))

    # ===== FOOTER =====
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e2e8f0')))
    story.append(Paragraph(
        f"<font size=7 color='#94a3b8'>Reporte generado automaticamente por Dashboard Performance de Linea v3.1.0 | {datetime.now().strftime('%d/%m/%Y')}</font>",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=7, textColor=HexColor('#94a3b8'))
    ))

    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# INICIALIZACION DE ESTADO DE SESION
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
# SIDEBAR - PANEL DE CONTROL
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0; border-bottom: 1px solid #334155; margin-bottom: 2rem;">
        <h1 style="color: #e67e22; font-size: 1.8rem; margin: 0;">🏭</h1>
        <h2 style="color: #f8fafc; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 700;">
            PERFORMANCE LINE
        </h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 0.3rem 0 0 0;">
            Sistema de Analisis de Paradas
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #e67e22; font-size: 1rem; margin-bottom: 1rem;'>CARGA DE DATOS</h3>", 
                unsafe_allow_html=True)

    metodo_carga = st.radio(
        "Metodo de carga:",
        ["URL (SharePoint)", "Archivo Local"],
        index=0,
        help="Seleccione si desea cargar desde una URL o subir un archivo local"
    )

    archivo_cargado = None

    if metodo_carga == "URL (SharePoint)":
        url_input = st.text_input(
            "URL del archivo Excel:",
            placeholder="https://.../Reporte.xlsx",
            help="URL del archivo Excel en SharePoint u otro servicio"
        )

        if st.button("CARGAR DESDE URL", use_container_width=True):
            if url_input and url_input.strip():
                with st.spinner("Descargando archivo..."):
                    archivo_cargado = descargar_desde_url(url_input.strip())
                    if archivo_cargado:
                        st.session_state.nombre_archivo = url_input.split('/')[-1].split('?')[0] or "archivo_sharepoint.xlsx"
            else:
                st.warning("Ingrese una URL valida")

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
                # Leer Excel con fallback de motores
                df_raw = leer_excel_con_fallback(archivo_cargado, sheet_name=0)

                if df_raw is None:
                    st.error("No se pudo leer el archivo Excel.")
                else:
                    # Detectar columnas
                    columnas_detectadas = detectar_columnas(df_raw)

                    if not columnas_detectadas:
                        st.error("No se detectaron columnas validas.")
                        st.info("Columnas esperadas: FECHA, TURNO, TIEMPO, MAQUINA, ESTACION, SISTEMA, PARTE, CAUSA")
                    else:
                        # Limpiar datos
                        df_limpio = limpiar_dataframe(df_raw, columnas_detectadas)

                        if df_limpio.empty:
                            st.error("No se encontraron datos validos despues de la limpieza.")
                        else:
                            st.session_state.df_original = df_limpio
                            st.session_state.df_filtrado = df_limpio.copy()
                            st.session_state.columnas_map = columnas_detectadas
                            st.session_state.datos_cargados = True
                            st.session_state.filtros_aplicados = False
                            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(df_limpio)

                            st.success(f"Datos cargados: {len(df_limpio)} registros")

                            with st.expander("Columnas detectadas"):
                                for estandar, real in columnas_detectadas.items():
                                    st.markdown(f"✓ **{estandar}**: `{real}`")

        except Exception as e:
            st.error(f"Error al procesar: {str(e)}")

    st.markdown("<hr style='border-color: #334155; margin: 2rem 0;'>", unsafe_allow_html=True)

    # Filtros dinamicos
    if st.session_state.datos_cargados:
        st.markdown("<h3 style='color: #e67e22; font-size: 1rem; margin-bottom: 1rem;'>FILTROS</h3>", 
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
                seleccion = st.multiselect(f"{col.upper()}:", options=opciones, default=['Todos'])
                if 'Todos' not in seleccion:
                    filtros[col] = seleccion

        if st.button("APLICAR FILTROS", use_container_width=True):
            df_filtrado = df.copy()
            if fecha_inicio and fecha_fin:
                df_filtrado = df_filtrado[
                    (df_filtrado['fecha'].dt.date >= fecha_inicio) & 
                    (df_filtrado['fecha'].dt.date <= fecha_fin)
                ]
            for col, valores in filtros.items():
                df_filtrado = df_filtrado[df_filtrado[col].isin(valores)]

            st.session_state.df_filtrado = df_filtrado
            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(df_filtrado)
            st.session_state.filtros_aplicados = True
            st.success(f"Filtros aplicados: {len(df_filtrado)} registros")
            st.rerun()

        if st.button("LIMPIAR FILTROS", use_container_width=True):
            st.session_state.df_filtrado = st.session_state.df_original.copy()
            st.session_state.metricas = calcular_mtbf_mttr_disponibilidad(st.session_state.df_original)
            st.session_state.filtros_aplicados = False
            st.rerun()

    # Configuracion de turno
    st.markdown("<hr style='border-color: #334155; margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e67e22; font-size: 1rem; margin-bottom: 1rem;'>CONFIGURACION</h3>", 
                unsafe_allow_html=True)

    minutos_turno = st.number_input("Minutos por turno:", min_value=1, max_value=1440, value=480)
    turnos_dia = st.number_input("Turnos por dia:", min_value=1, max_value=3, value=2)

    st.session_state.config_turno = {
        'minutos_turno': minutos_turno,
        'turnos_dia': turnos_dia
    }

    # Footer sidebar
    st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; padding: 1rem; 
                background: #0f172a; border-top: 1px solid #334155; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">
            v3.1.0 | Sistema de Manufactura Inteligente
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# CONTENIDO PRINCIPAL
# ==============================================================================

# Header institucional
st.markdown("""
<div class="main-header animate-in">
    <h1>🏭 Dashboard Performance de Linea</h1>
    <h2>Analisis de Paradas, Disponibilidad y Eficiencia para Toma de Decisiones Gerenciales</h2>
    <span class="badge">VERSION INSTITUCIONAL 3.1.0</span>
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
            Este sistema permite analizar el performance de lineas de produccion mediante 
            el analisis de paradas, calculo de disponibilidad, MTBF y MTTR. 
            Cargue un archivo Excel desde SharePoint o localmente para comenzar.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; max-width: 900px; margin: 0 auto;">
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #e67e22; font-size: 1.2rem;">📈 Pareto de Paradas</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Identifique las causas principales siguiendo la regla 80/20</p>
            </div>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #e67e22; font-size: 1.2rem;">⏱️ MTBF / MTTR</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Metricas clave de confiabilidad y mantenibilidad</p>
            </div>
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #e67e22; font-size: 1.2rem;">📊 Disponibilidad</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Calculo automatico de disponibilidad de linea</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("FORMATO ESPERADO DEL ARCHIVO EXCEL", expanded=False):
        st.markdown("""
        El archivo Excel debe contener las siguientes columnas (nombres flexibles):

        | Columna | Descripcion | Ejemplo |
        |---------|-------------|---------|
        | **FECHA** | Fecha del evento | 15/01/2026 |
        | **TURNO** | Turno de operacion | Turno 1, Turno 2 |
        | **AVISO** | Codigo de aviso (opcional) | 120253513 |
        | **TIEMPO** | Duracion en minutos | 45 |
        | **MAQUINA** | Identificacion de maquina | M 219 |
        | **ESTACION** | Estacion o area afectada | ST1- Alimentacion |
        | **SISTEMA** | Sistema involucrado | Alimentador de casquillos |
        | **PARTE** | Parte o componente | Pin volteador |
        | **CAUSA** | Causa de la averia | Trabamiento |
        | **PROBLEMA** | Descripcion del problema | Operador reporta fallas... |
        | **TRABAJO** | Descripcion del trabajo realizado | Se verifica funcionamiento... |

        **Notas:**
        - Los nombres de columnas pueden variar (ej: "Tiempo", "TIEMPO", "Duracion")
        - El sistema detecta automaticamente las columnas
        - Se eliminan automaticamente filas de encabezado duplicadas
        - Las fechas en formato serial de Excel se convierten automaticamente
        """)

    st.stop()


# ==============================================================================
# DASHBOARD PRINCIPAL (CON DATOS CARGADOS)
# ==============================================================================
df = st.session_state.df_filtrado
metricas = st.session_state.metricas

# Recalcular metricas con configuracion actual
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
        <strong>Filtros activos:</strong> Mostrando {len(df)} de {len(st.session_state.df_original)} registros | 
        Periodo: {df['fecha'].min().strftime('%d/%m/%Y')} - {df['fecha'].max().strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECCION 1: KPIs PRINCIPALES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🎯</span> INDICADORES CLAVE DE PERFORMANCE</div>", 
            unsafe_allow_html=True)

color_disp = calcular_kpi_color(metricas['disponibilidad'], 'disponibilidad')
color_mtbf = calcular_kpi_color(metricas['mtbf_horas'], 'mtbf')
color_mttr = calcular_kpi_color(metricas['mttr_horas'], 'mttr')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(render_kpi_card(
        label="Disponibilidad",
        valor=f"{metricas['disponibilidad']:.2f}%",
        color_class=color_disp,
        icon="📈",
        subtext=f"Objetivo: >=95% | {metricas['dias_analizados']} dias analizados"
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
# SECCION 2: GAUGES Y VISUALIZACIONES
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
    max_mtbf = max(12, metricas['mtbf_horas'] * 1.2)
    fig_gauge_mtbf = crear_gauge_chart(
        metricas['mtbf_horas'],
        "MTBF (horas)",
        maximo=max_mtbf,
        color_primario=COLORES_INSTITUCIONALES['info']
    )
    st.plotly_chart(fig_gauge_mtbf, use_container_width=True, config={'displayModeBar': False})

with col_g3:
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
# SECCION 3: RESUMEN EJECUTIVO
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📋</span> RESUMEN EJECUTIVO PARA GERENCIA</div>", 
            unsafe_allow_html=True)

st.markdown(resumen_ejecutivo_texto(df, metricas), unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 4: PARETO Y ANALISIS DE PARADAS
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📊</span> ANALISIS DE PARETO - PRINCIPALES CAUSAS</div>", 
            unsafe_allow_html=True)

tab_pareto = st.tabs(["Por Causa", "Por Estacion", "Por Sistema", "Por Parte", "Por Turno"])

with tab_pareto[0]:
    if 'causa' in df.columns:
        fig_pareto_causa = crear_pareto(
            df, 'causa', 'tiempo',
            "Pareto de Paradas por Causa de Averia",
            top_n=15,
            color_barras=COLORES_INSTITUCIONALES['peligro']
        )
        st.plotly_chart(fig_pareto_causa, use_container_width=True)

        with st.expander("Ver tabla detallada de causas"):
            tabla_causas = df.groupby('causa').agg({
                'tiempo': ['sum', 'count', 'mean'],
                'fecha': 'nunique'
            }).reset_index()
            tabla_causas.columns = ['Causa', 'Tiempo Total (min)', 'Cantidad', 'Tiempo Prom (min)', 'Dias Afectados']
            tabla_causas['% del Total'] = (tabla_causas['Tiempo Total (min)'] / tabla_causas['Tiempo Total (min)'].sum() * 100).round(2)
            tabla_causas = tabla_causas.sort_values('Tiempo Total (min)', ascending=False)
            st.dataframe(tabla_causas, use_container_width=True, hide_index=True)

            excel_data = generar_excel_descarga(tabla_causas, "Pareto_Causas")
            st.download_button(
                label="Descargar tabla Excel",
                data=excel_data,
                file_name="pareto_causas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No se encontro la columna de causa en los datos.")

with tab_pareto[1]:
    if 'estacion' in df.columns:
        fig_pareto_est = crear_pareto(
            df, 'estacion', 'tiempo',
            "Pareto de Paradas por Estacion",
            top_n=15,
            color_barras=COLORES_INSTITUCIONALES['info']
        )
        st.plotly_chart(fig_pareto_est, use_container_width=True)

        with st.expander("Ver tabla detallada de estaciones"):
            tabla_est = df.groupby('estacion').agg({
                'tiempo': ['sum', 'count', 'mean'],
                'fecha': 'nunique'
            }).reset_index()
            tabla_est.columns = ['Estacion', 'Tiempo Total (min)', 'Cantidad', 'Tiempo Prom (min)', 'Dias Afectados']
            tabla_est['% del Total'] = (tabla_est['Tiempo Total (min)'] / tabla_est['Tiempo Total (min)'].sum() * 100).round(2)
            tabla_est = tabla_est.sort_values('Tiempo Total (min)', ascending=False)
            st.dataframe(tabla_est, use_container_width=True, hide_index=True)
    else:
        st.info("No se encontro la columna de estacion en los datos.")

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
        st.info("No se encontro la columna de sistema en los datos.")

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
        st.info("No se encontro la columna de parte en los datos.")

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
        st.info("No se encontro la columna de turno en los datos.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 5: TENDENCIAS TEMPORALES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📈</span> TENDENCIAS TEMPORALES</div>", 
            unsafe_allow_html=True)

tab_tendencia = st.tabs(["Por Dia", "Por Semana", "Por Mes", "Mapa de Calor"])

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
                                               titulo="Mapa de Calor - Intensidad de Paradas por Dia")
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No se encontro informacion de fechas.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 6: ANALISIS JERARQUICO Y DISTRIBUCIONES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🗂️</span> ANALISIS JERARQUICO Y DISTRIBUCIONES</div>", 
            unsafe_allow_html=True)

col_j1, col_j2 = st.columns(2)

with col_j1:
    if 'estacion' in df.columns and 'sistema' in df.columns:
        st.markdown("<h4 style='color: #1e3a5f; margin-bottom: 1rem;'>Treemap: Jerarquia Estacion → Sistema</h4>", 
                    unsafe_allow_html=True)
        fig_treemap = crear_treemap(df, path=['estacion', 'sistema'], valores='tiempo', titulo="")
        st.plotly_chart(fig_treemap, use_container_width=True)

with col_j2:
    if 'causa' in df.columns and 'parte' in df.columns:
        st.markdown("<h4 style='color: #1e3a5f; margin-bottom: 1rem;'>Sunburst: Causa → Parte</h4>", 
                    unsafe_allow_html=True)
        fig_sun = crear_sunburst(df, path=['causa', 'parte'], valores='tiempo', titulo="")
        st.plotly_chart(fig_sun, use_container_width=True)

st.markdown("<h4 style='color: #1e3a5f; margin: 2rem 0 1rem 0;'>Distribucion de Tiempos por Categoria</h4>", 
            unsafe_allow_html=True)

col_b1, col_b2 = st.columns(2)

with col_b1:
    if 'causa' in df.columns:
        fig_box_causa = crear_analisis_caja(df, 'causa', 'tiempo', 
                                            "Distribucion de Tiempos por Causa")
        st.plotly_chart(fig_box_causa, use_container_width=True)

with col_b2:
    if 'estacion' in df.columns:
        fig_box_est = crear_analisis_caja(df, 'estacion', 'tiempo',
                                          "Distribucion de Tiempos por Estacion")
        st.plotly_chart(fig_box_est, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 7: ANALISIS CRUZADO Y COMPARATIVOS
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>🔀</span> ANALISIS CRUZADO</div>", 
            unsafe_allow_html=True)

tab_cruzado = st.tabs(["Barras Apiladas", "Dispersion", "Comparativo Temporal"])

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
        scatter_data = scatter_data[scatter_data['cantidad'] >= 2]

        if not scatter_data.empty:
            fig_scatter = crear_grafico_dispersion(
                scatter_data, 'cantidad', 'tiempo_total', 'causa', 'tiempo_promedio',
                "Relacion Cantidad vs Tiempo Total de Paradas"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("Tamano de burbuja = Tiempo promedio por evento")

with tab_cruzado[2]:
    if 'fecha' in df.columns and 'turno' in df.columns:
        df['anio_mes'] = df['fecha'].dt.to_period('M').astype(str)
        pivot_temporal = df.groupby(['anio_mes', 'turno'])['tiempo'].sum().reset_index()

        fig_temporal = px.line(
            pivot_temporal, x='anio_mes', y='tiempo', color='turno',
            markers=True, title="Evolucion Temporal por Turno",
            labels={'tiempo': 'Tiempo (min)', 'anio_mes': 'Periodo'},
            color_discrete_sequence=COLORES_INSTITUCIONALES['paleta']
        )
        fig_temporal.update_layout(
            height=450, template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=60, r=40, t=80, b=60),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_temporal, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 8: ANALISIS DE TEXTO (NLP BASICO)
# ==============================================================================
if 'problema' in df.columns or 'trabajo' in df.columns:
    st.markdown("<div class='section-title'><span class='icon'>📝</span> ANALISIS DE DESCRIPCIONES</div>", 
                unsafe_allow_html=True)

    tab_texto = st.tabs(["Problemas", "Trabajos Realizados"])

    with tab_texto[0]:
        if 'problema' in df.columns:
            freq_problemas = analisis_texto_frecuencia(df, 'problema', top_n=20)
            if not freq_problemas.empty:
                fig_freq = px.bar(
                    freq_problemas, x='Frecuencia', y='Palabra', orientation='h',
                    title="Palabras mas frecuentes en descripciones de problemas",
                    color='Frecuencia', color_continuous_scale='Oranges',
                    labels={'Frecuencia': 'N de menciones', 'Palabra': ''}
                )
                fig_freq.update_layout(
                    height=500, template='plotly_white',
                    margin=dict(l=100, r=40, t=60, b=40),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_freq, use_container_width=True)
            else:
                st.info("No hay suficientes descripciones para analizar.")

    with tab_texto[1]:
        if 'trabajo' in df.columns:
            freq_trabajos = analisis_texto_frecuencia(df, 'trabajo', top_n=20)
            if not freq_trabajos.empty:
                fig_freq_t = px.bar(
                    freq_trabajos, x='Frecuencia', y='Palabra', orientation='h',
                    title="Palabras mas frecuentes en trabajos realizados",
                    color='Frecuencia', color_continuous_scale='Blues',
                    labels={'Frecuencia': 'N de menciones', 'Palabra': ''}
                )
                fig_freq_t.update_layout(
                    height=500, template='plotly_white',
                    margin=dict(l=100, r=40, t=60, b=40),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_freq_t, use_container_width=True)
            else:
                st.info("No hay suficientes descripciones para analizar.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 9: TABLA DE DATOS Y EXPORTACION
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📑</span> DATOS DETALLADOS Y EXPORTACION</div>", 
            unsafe_allow_html=True)

with st.expander("Ver tabla completa de datos", expanded=False):
    df_display = df.copy()
    if 'fecha' in df_display.columns:
        df_display['fecha'] = df_display['fecha'].dt.strftime('%d/%m/%Y')

    rows_per_page = 50
    total_rows = len(df_display)
    total_pages = max(1, math.ceil(total_rows / rows_per_page))

    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        page = st.number_input("Pagina:", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)

    st.dataframe(df_display.iloc[start_idx:end_idx], use_container_width=True, hide_index=True, height=400)
    st.caption(f"Mostrando registros {start_idx + 1} - {end_idx} de {total_rows}")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        excel_completo = generar_excel_descarga(df_display, "Datos_Completos")
        st.download_button(
            label="Descargar Excel Completo",
            data=excel_completo,
            file_name=f"reporte_completo_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_e2:
        csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name=f"reporte_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==============================================================================
# SECCION 10: EXPORTACION A PDF FORMATO A4
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>📄</span> EXPORTACION A PDF (FORMATO A4)</div>", 
            unsafe_allow_html=True)

st.markdown("""
<div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem;">
    <p style="color: #64748b; margin: 0;">
        Genere un reporte PDF profesional en formato A4 con los Paretos de paradas, 
        indicadores clave, incidencias detalladas y recomendaciones para gerencia.
    </p>
</div>
""", unsafe_allow_html=True)

# Obtener nombre de maquina para el PDF
nombre_maquina_pdf = "Linea"
if 'maquina' in df.columns and len(df) > 0:
    maquinas = df['maquina'].unique()
    if len(maquinas) == 1:
        nombre_maquina_pdf = str(maquinas[0])
    else:
        nombre_maquina_pdf = f"Linea ({len(maquinas)} maquinas)"

if st.button("📄 GENERAR REPORTE PDF A4", use_container_width=True, type="primary"):
    with st.spinner("Generando reporte PDF profesional... Esto puede tomar unos segundos."):
        try:
            pdf_bytes = generar_pdf_reporte(df, metricas, nombre_maquina=nombre_maquina_pdf)

            st.success("✅ Reporte PDF generado exitosamente!")

            st.download_button(
                label="📥 DESCARGAR REPORTE PDF",
                data=pdf_bytes,
                file_name=f"Reporte_Performance_{nombre_maquina_pdf.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.info("""
            **El PDF incluye:**
            - Resumen ejecutivo con periodo y metricas
            - Tabla de KPIs (Disponibilidad, MTBF, MTTR) con estados
            - Pareto de causas de parada (Top 10) con tabla detallada
            - Pareto de estaciones criticas (Top 10) con tabla detallada
            - Incidencias detalladas (Top 15 eventos mas largos)
            - Recomendaciones automaticas basadas en umbrales
            - Formato profesional A4 listo para imprimir o presentar
            """)

        except Exception as e:
            st.error(f"Error al generar PDF: {str(e)}")
            st.info("Sugerencia: Verifique que las librerias reportlab esten instaladas correctamente.")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ==============================================================================
# SECCION 11: INFORME AUTOMATICO Y RECOMENDACIONES
# ==============================================================================
st.markdown("<div class='section-title'><span class='icon'>💡</span> INFORME AUTOMATICO Y RECOMENDACIONES</div>", 
            unsafe_allow_html=True)

recomendaciones = []

if metricas['disponibilidad'] < 85:
    recomendaciones.append({
        'tipo': 'critico',
        'icono': '🔴',
        'titulo': 'Disponibilidad Critica',
        'mensaje': f"La disponibilidad actual es del {metricas['disponibilidad']:.1f}%, muy por debajo del objetivo del 95%. Se requiere accion inmediata."
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
        'titulo': 'Disponibilidad Optima',
        'mensaje': f"Excelente disponibilidad del {metricas['disponibilidad']:.1f}%. Mantener las practicas actuales."
    })

if metricas['mtbf_horas'] < 4:
    recomendaciones.append({
        'tipo': 'critico',
        'icono': '🔴',
        'titulo': 'MTBF Muy Bajo',
        'mensaje': f"El MTBF es de solo {metricas['mtbf_horas']:.1f} horas. Las fallas son demasiado frecuentes. Priorizar analisis de causa raiz."
    })
elif metricas['mtbf_horas'] < 8:
    recomendaciones.append({
        'tipo': 'advertencia',
        'icono': '🟡',
        'titulo': 'MTBF Regular',
        'mensaje': f"MTBF de {metricas['mtbf_horas']:.1f} horas. Se recomienda implementar mantenimiento predictivo."
    })

if metricas['mttr_horas'] > 3:
    recomendaciones.append({
        'tipo': 'critico',
        'icono': '🔴',
        'titulo': 'MTTR Elevado',
        'mensaje': f"El tiempo promedio de reparacion es de {metricas['mttr_horas']:.1f} horas. Revisar procedimientos de mantenimiento y disponibilidad de repuestos."
    })
elif metricas['mttr_horas'] > 1:
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
        causa_pct = (causa_tiempo / metricas['tiempo_total_paradas']) * 100

        if causa_pct > 30:
            recomendaciones.append({
                'tipo': 'critico',
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
        'critico': '#fef2f2; border-left: 4px solid #dc2626;',
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
# SECCION 12: FOOTER INSTITUCIONAL
# ==============================================================================
st.markdown("""
<div class="footer">
    <p><strong>Sistema de Manufactura Inteligente</strong></p>
    <p>Dashboard Performance de Linea v3.1.0 | Desarrollado para Analisis Gerencial</p>
    <p style="margin-top: 0.5rem; font-size: 0.75rem;">
        2026 | Compatible con SharePoint y archivos Excel estandar | 
        Metricas calculadas segun estandares SMRP e ISO 14224
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FIN DEL SCRIPT
# ==============================================================================
