import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import itertools
import base64  # Para convertir la imagen a base64
import os

# ============================
#  1. Configuración Inicial
# ============================
file_path = r"C:\Users\2501TK0505236\Desktop\SUMINISTROS\LARI2024.xlsx"
logo_path = r"C:\Users\2501TK0505236\Desktop\SUMINISTROS\logo2.png"

colores_pluz = {
    "azul": "#2B3990",
    "naranja": "#FBB03B",
    "verde": "#78BE20"
}

# Convertir la imagen a base64 para que se muestre correctamente en Dash
def encode_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return "data:image/png;base64," + base64.b64encode(image_file.read()).decode()
    return None

logo_base64 = encode_image(logo_path)

# ============================
#  2. Lectura de Datos
# ============================
try:
    df = pd.read_excel(file_path, sheet_name="1")
except FileNotFoundError:
    print("❌ Error: Archivo no encontrado.")
    exit()
except ValueError:
    print("❌ Error: La hoja '1' no existe en el archivo.")
    exit()

df_selected = df[["Distrito", "Mes", "Tipo de Fallas", "Clientes Afectados"]].copy()

# ================================
#  3. Conversión de Mes a Texto
# ================================
meses_dict = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df_selected["Mes"] = pd.to_numeric(df_selected["Mes"], errors="coerce").map(meses_dict).fillna("Desconocido")
meses_ordenados = list(meses_dict.values())

# =========================================
#  4. Agrupar datos y rellenar ceros
# =========================================
df_grouped = df_selected.groupby(["Distrito", "Mes", "Tipo de Fallas"]).agg(
    Cantidad_Fallas=("Tipo de Fallas", "count"),
    Clientes_Afectados=("Clientes Afectados", "sum")
).reset_index()

todos_distritos = df_grouped["Distrito"].dropna().unique()
todos_tipos_falla = df_grouped["Tipo de Fallas"].dropna().unique()

# Para no perder combinaciones (distrito-mes-falla) que estén vacías
combinaciones = pd.DataFrame(
    itertools.product(todos_distritos, meses_ordenados, todos_tipos_falla),
    columns=["Distrito", "Mes", "Tipo de Fallas"]
)
df_grouped = combinaciones.merge(df_grouped, on=["Distrito", "Mes", "Tipo de Fallas"], how="left").fillna(0)

# Asegurar el orden de los meses
df_grouped["Mes"] = pd.Categorical(df_grouped["Mes"], categories=meses_ordenados, ordered=True)

# ================================
#  5. Construir la Aplicación Dash
# ================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# ============================
#  6. Diseño (Layout) con Tabs
# ============================
app.layout = html.Div(style={"fontFamily": "Arial, sans-serif"}, children=[

    # Encabezado (Logo + Título)
    html.Div([
        html.Img(src=logo_base64, style={"width": "120px", "float": "right", "marginRight": "20px"}) if logo_base64 else None,
        html.H1(
            "📌 Análisis de Atenciones LARI - 2024",
            style={
                "color": colores_pluz["azul"],
                "textAlign": "center",
                "fontSize": 32,
                "marginBottom": "10px"
            }
        ),
    ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "marginBottom": "20px"}),

    # Pestañas
    dcc.Tabs(
        id="tabs",
        value="mes",
        children=[
            dcc.Tab(label="📆 Análisis por Mes", value="mes"),
            dcc.Tab(label="⚡ Análisis por Tipo de Falla", value="falla"),
            dcc.Tab(label="📊 Tendencia de Fallas (Total)", value="tendencia"),
        ],
        style={"fontWeight": "bold"}
    ),

    # Contenido de las pestañas
    html.Div(id="tabs-content")
])

# ===============================
#  7. Callback para cambiar de Tab
# ===============================
@app.callback(
    Output("tabs-content", "children"),
    Input("tabs", "value")
)
def render_content(tab):
    if tab == "mes":
        return html.Div([html.H3("📆 Selección de Mes")])
    elif tab == "falla":
        return html.Div([html.H3("⚡ Análisis por Tipo de Falla")])
    elif tab == "tendencia":
        return html.Div([html.H3("📊 Tendencia de Fallas (Total)")])
    return html.Div()

# =========================
#  8. Ejecutar la Aplicación
# =========================
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
