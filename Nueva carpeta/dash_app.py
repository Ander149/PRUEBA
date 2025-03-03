import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import itertools

# ============================
#  1. Configuración Inicial
# ============================
file_path = r"C:\Users\2501TK0505236\Documents\GitHub\PRUEBA\LARI2024.xlsx"

colores_pluz = {
    "azul": "#2B3990",
    "naranja": "#FBB03B",
    "verde": "#78BE20"
}

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
    1: "Enero", 2: "Febrero",  3: "Marzo",     4: "Abril",
    5: "Mayo",  6: "Junio",    7: "Julio",     8: "Agosto",
    9: "Septiembre", 10: "Octubre",
    11: "Noviembre", 12: "Diciembre"
}
df_selected["Mes"] = pd.to_numeric(df_selected["Mes"], errors="coerce").map(meses_dict).fillna("Desconocido")
meses_ordenados = list(meses_dict.values())

# ================================
#  4. Crear la Aplicación Dash
# ================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("📌 Dashboard de Fallas"),
    dcc.Graph(id="grafico-fallas"),
])

@app.callback(
    Output("grafico-fallas", "figure"),
    Input("grafico-fallas", "id")
)
def actualizar_grafico(_):
    df_grouped = df_selected.groupby(["Distrito"])["Clientes Afectados"].sum().reset_index()
    fig = px.bar(df_grouped, x="Distrito", y="Clientes Afectados", title="Clientes Afectados por Distrito")
    return fig

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
