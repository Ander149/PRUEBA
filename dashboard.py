import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import itertools

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

# Aseguramos el orden de los meses
df_grouped["Mes"] = pd.Categorical(df_grouped["Mes"], categories=meses_ordenados, ordered=True)

# ================================
#  5. Construir la aplicación Dash
# ================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# ============================
#  6. Diseño (Layout) con Tabs
# ============================
app.layout = html.Div(style={"fontFamily": "Arial, sans-serif"}, children=[

    # Encabezado (Logo + Título)
    html.Div([
        html.Img(src=logo_path, style={"width": "120px", "float": "right", "marginRight": "20px"}),
        html.H1(
            "📌 Análisis de atenciones LARI - 2024",
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

    # Contenido que se despliega según la pestaña
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
    """Devuelve el contenido de cada pestaña."""
    if tab == "mes":
        return html.Div([
            html.Label("🔍 Selecciona un Mes",
                       style={"fontWeight": "bold", "color": colores_pluz["azul"]}),
            dcc.Dropdown(
                id="mes-selector",
                options=[{"label": mes, "value": mes} for mes in meses_ordenados],
                value="Noviembre",  # Valor por defecto, opcional
                clearable=True,
                style={"width": "60%", "margin": "auto"}
            ),
            # Agregamos 5 gráficos + 1 texto
            dcc.Graph(id="heatmap-mes", style={"width": "95%", "height": "700px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="ranking-mas-casos", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="barras-falla-mas-casos", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="ranking-menos-casos", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="barras-falla-menos-casos", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),

            html.H3(id="total-casos-mes", style={"textAlign": "center", "marginTop": "20px"})
        ])

    elif tab == "falla":
        return html.Div([
            html.Label("🔍 Selecciona un Tipo de Falla",
                       style={"fontWeight": "bold", "color": colores_pluz["azul"]}),
            dcc.Dropdown(
                id="falla-selector",
                options=[{"label": falla, "value": falla} for falla in todos_tipos_falla],
                clearable=True,
                style={"width": "60%", "margin": "auto"}
            ),
            dcc.Graph(id="heatmap-falla", style={"width": "95%", "height": "700px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="ranking-falla", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),

            html.H3(id="total-casos-falla", style={"textAlign": "center", "marginTop": "20px"})
        ])

    elif tab == "tendencia":
        return html.Div([
            # 5 gráficos + 1 texto, igual que en tu callback
            dcc.Graph(id="heatmap-total", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="ranking-mas-casos-total", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="barras-falla-mas-casos-total", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="ranking-menos-casos-total", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),
            dcc.Graph(id="barras-falla-menos-casos-total", style={"width": "95%", "height": "600px", "margin": "auto", "padding": "20px"}),

            html.H3(id="total-casos-total", style={"textAlign": "center", "marginTop": "20px"})
        ])

    return html.Div()  # Si no coincide la pestaña

# =========================================
#  8. ANÁLISIS "POR MES" (5 gráficos + texto)
# =========================================
@app.callback(
    [
        Output("heatmap-mes", "figure"),
        Output("ranking-mas-casos", "figure"),
        Output("barras-falla-mas-casos", "figure"),
        Output("ranking-menos-casos", "figure"),
        Output("barras-falla-menos-casos", "figure"),
        Output("total-casos-mes", "children")
    ],
    Input("mes-selector", "value")
)
def actualizar_graficos_mes(mes_seleccionado):
    df_filtrado = df_grouped[df_grouped["Mes"] == mes_seleccionado]

    if df_filtrado.empty:
        return (
            px.imshow([]), px.bar([]), px.bar([]),
            px.bar([]), px.bar([]),
            "No hay datos para este mes"
        )

    # 1) Heatmap: Tipo de Fallas vs. Distrito
    heatmap_data = df_filtrado.pivot(
        index="Tipo de Fallas",
        columns="Distrito",
        values="Cantidad_Fallas"
    ).fillna(0)
    heatmap_data = heatmap_data.replace(0, None)
    heatmap_data.dropna(axis="columns", how="all", inplace=True)
    heatmap_data.dropna(axis="index", how="all", inplace=True)

    heatmap_fig = px.imshow(
        heatmap_data,
        color_continuous_scale="YlOrRd",
        text_auto=True,
        height=600,
        width=1100,
        title=f"Mapa de Calor de Fallas - {mes_seleccionado}"
    )

    # 2) Top 5 distritos con MÁS fallas
    ranking_mas_data = df_filtrado.groupby("Distrito")[["Cantidad_Fallas", "Clientes_Afectados"]].sum().reset_index()
    ranking_mas_data = ranking_mas_data.sort_values(by="Cantidad_Fallas", ascending=False).head(5)

    ranking_mas_melted = ranking_mas_data.melt(
        id_vars="Distrito",
        value_vars=["Cantidad_Fallas", "Clientes_Afectados"],
        var_name="Métrica",
        value_name="Valor"
    )

    ranking_mas_fig = px.bar(
        ranking_mas_melted,
        x="Valor",
        y="Distrito",
        color="Métrica",
        orientation="h",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "Cantidad_Fallas": colores_pluz["naranja"],
            "Clientes_Afectados": colores_pluz["verde"]
        },
        height=600,
        width=1100,
        title=f"🔝 Top 5 Distritos con Más Fallas - {mes_seleccionado}"
    )

    # Barras apiladas para esos mismos top 5
    top5_distritos_mas = ranking_mas_data["Distrito"].tolist()
    df_barras_mas = df_filtrado[df_filtrado["Distrito"].isin(top5_distritos_mas)]

    barras_mas_fig = px.bar(
        df_barras_mas,
        x="Cantidad_Fallas",
        y="Distrito",
        color="Tipo de Fallas",
        orientation="h",
        barmode="stack",
        text_auto=True,
        height=600,
        width=1100,
        title=f"📊 Tipos de Fallas (Top 5 con Más Fallas) - {mes_seleccionado}"
    )

    # 3) Top 5 distritos con MENOS fallas
    ranking_menos_data = df_filtrado.groupby("Distrito")[["Cantidad_Fallas", "Clientes_Afectados"]].sum().reset_index()

    # FILTRAMOS los distritos con fallas entre 1 y 100
    ranking_menos_data = ranking_menos_data.sort_values(by="Cantidad_Fallas", ascending=True).head(5)


    # Ordenamos de menor a mayor cantidad de fallas
    ranking_menos_data = ranking_menos_data.sort_values(by="Cantidad_Fallas", ascending=True)


    ranking_menos_melted = ranking_menos_data.melt(
        id_vars="Distrito",
        value_vars=["Cantidad_Fallas", "Clientes_Afectados"],
        var_name="Métrica",
        value_name="Valor"
    )

    ranking_menos_fig = px.bar(
        ranking_menos_melted,
        x="Valor",
        y="Distrito",
        color="Métrica",
        orientation="h",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "Cantidad_Fallas": colores_pluz["naranja"],
            "Clientes_Afectados": colores_pluz["verde"]
        },
        height=600,
        width=1100,
        title=f"🔻 Top 5 Distritos con Menos Fallas - {mes_seleccionado}"
    )

    # Barras apiladas para esos top 5 (menos)
    # Filtrar los distritos con fallas entre 1 y 100
    ranking_menos_data = df_filtrado.groupby("Distrito")[["Cantidad_Fallas", "Clientes_Afectados"]].sum().reset_index()
    ranking_menos_data = ranking_menos_data.sort_values(by="Cantidad_Fallas", ascending=True).head(5)
    # Obtener la lista de distritos filtrados
    distritos_menos_fallas = ranking_menos_data["Distrito"].tolist()

    # Filtrar el dataframe original con estos distritos
    df_barras_menos = df_filtrado[df_filtrado["Distrito"].isin(distritos_menos_fallas)]

    barras_menos_fig = px.bar(
        df_barras_menos,
        x="Cantidad_Fallas",
        y="Distrito",
        color="Tipo de Fallas",
        orientation="h",
        barmode="stack",
        text_auto=True,
        height=600,
        width=1100,
        title=f"📊 Tipos de Fallas (Top 5 con Menos Fallas) - {mes_seleccionado}"
    )

    # 4) Texto total de fallas y clientes
    total_fallas = df_filtrado["Cantidad_Fallas"].sum()
    total_clientes = df_filtrado["Clientes_Afectados"].sum()
    texto_total = f"📌 Total de Fallas: {int(total_fallas):,} | Total de Clientes Afectados: {int(total_clientes):,}"

    return (
        heatmap_fig,
        ranking_mas_fig,
        barras_mas_fig,
        ranking_menos_fig,
        barras_menos_fig,
        texto_total
    )

# ===========================================
#  9. ANÁLISIS "POR TIPO DE FALLA" (Fila TOTAL sin color)
# ===========================================
@app.callback(
    [
        Output("heatmap-falla", "figure"),
        Output("ranking-falla", "figure"),
        Output("total-casos-falla", "children")
    ],
    Input("falla-selector", "value")
)
def actualizar_graficos_falla(falla_seleccionada):
    if not falla_seleccionada:
        return px.imshow([]), px.bar([]), "No hay datos para este tipo de falla"

    # Filtrar datos para el tipo de falla elegido
    df_filtrado = df_grouped[df_grouped["Tipo de Fallas"] == falla_seleccionada]
    if df_filtrado.empty:
        return px.imshow([]), px.bar([]), "No hay datos para este tipo de falla"

    # 1) Generar la matriz para el heatmap (Mes vs Distrito)
    heatmap_data = df_filtrado.pivot(
        index="Mes",
        columns="Distrito",
        values="Cantidad_Fallas"
    ).fillna(0)

    # (A) Calcular la suma de cada columna (distrito) para anotar en la fila 'TOTAL'
    col_sums = heatmap_data.sum(numeric_only=True)

    # (B) Insertar la fila "TOTAL" con None para que no se pinte con color
    heatmap_data.loc["TOTAL"] = None

    # (C) Reordenar para que "TOTAL" sea la primera fila
    new_index = ["TOTAL"] + [idx for idx in heatmap_data.index if idx != "TOTAL"]
    heatmap_data = heatmap_data.reindex(index=new_index)

    # Reemplazar 0 por None (para no colorear celdas con cero)
    heatmap_data = heatmap_data.replace(0, None)

    # 2) Crear la figura del heatmap
    heatmap_fig = px.imshow(
        heatmap_data,
        color_continuous_scale="YlOrRd",
        text_auto=True,  # Mostrará números en celdas != None
        height=700,
        width=1100,
        title=f"Mapa de Calor de Fallas - {falla_seleccionada}"
    )

    # (D) Agregar anotaciones manuales para la fila "TOTAL"
    for col_i, col_name in enumerate(heatmap_data.columns):
        valor_total = col_sums.get(col_name, None)
        if pd.notna(valor_total):
            heatmap_fig.add_annotation(
                x=col_i,
                y=0,  # fila "TOTAL" está en índice 0
                text=f"{int(valor_total):,}",  # formato con separador de miles
                showarrow=False,
                font=dict(color="black", size=14, family="Arial"),
                xref="x",
                yref="y"
            )

    # 3) Ranking de distritos (Top 5) para este tipo de falla
    ranking_data = df_filtrado.groupby("Distrito")[["Cantidad_Fallas", "Clientes_Afectados"]] \
                              .sum() \
                              .reset_index() \
                              .sort_values(by="Cantidad_Fallas", ascending=False) \
                              .head(5)

    ranking_melted = ranking_data.melt(
        id_vars="Distrito",
        value_vars=["Cantidad_Fallas", "Clientes_Afectados"],
        var_name="Métrica",
        value_name="Valor"
    )

    ranking_fig = px.bar(
        ranking_melted,
        x="Valor",
        y="Distrito",
        color="Métrica",
        orientation="h",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "Cantidad_Fallas": colores_pluz["naranja"],
            "Clientes_Afectados": colores_pluz["verde"]
        },
        height=700,
        width=1100,
        title=f"Top 5 Distritos - Falla: {falla_seleccionada}"
    )

    # 4) Totales (Texto debajo de los gráficos)
    total_fallas = df_filtrado["Cantidad_Fallas"].sum()
    total_clientes = df_filtrado["Clientes_Afectados"].sum()
    texto_total = f"Total de Fallas: {int(total_fallas):,} | Total de Clientes Afectados: {int(total_clientes):,}"

    return heatmap_fig, ranking_fig, texto_total

# =====================================
# 10. Callback para "Tendencia" Global
# =====================================
@app.callback(
    [
        Output("heatmap-total", "figure"),
        Output("ranking-mas-casos-total", "figure"),
        Output("barras-falla-mas-casos-total", "figure"),
        Output("ranking-menos-casos-total", "figure"),
        Output("barras-falla-menos-casos-total", "figure"),
        Output("total-casos-total", "children")
    ],
    Input("tabs", "value")
)
def actualizar_analisis_total(tab):
    """Muestra análisis total cuando la pestaña 'tendencia' está activa."""
    if tab != "tendencia":
        # Devolvemos gráficos vacíos si no estamos en la pestaña "tendencia"
        return (px.imshow([]), px.bar([]), px.bar([]), px.bar([]), px.bar([]), "")

    # 1) Mapa de Calor Total: Tipo de Fallas vs. Distrito
    heatmap_data = df_grouped.pivot(
        index="Tipo de Fallas",
        columns="Distrito",
        values="Cantidad_Fallas"
    ).fillna(0)

    heatmap_data = heatmap_data.replace(0, None)
    heatmap_data.dropna(axis="columns", how="all", inplace=True)
    heatmap_data.dropna(axis="index", how="all", inplace=True)

    heatmap_fig = px.imshow(
        heatmap_data,
        color_continuous_scale="YlOrRd",
        text_auto=True,
        height=600,
        width=1100,
        title="📊 Mapa de Calor Total de Fallas (Distrito vs. Tipo de Falla)"
    )

    # 2) TOP 5 DISTRITOS CON MÁS FALLAS (TOTAL)
    ranking_mas_data = df_grouped.groupby("Distrito")[["Cantidad_Fallas", "Clientes_Afectados"]] \
                                 .sum().reset_index() \
                                 .sort_values(by="Cantidad_Fallas", ascending=False) \
                                 .head(5)

    ranking_mas_melted = ranking_mas_data.melt(
        id_vars="Distrito",
        value_vars=["Cantidad_Fallas", "Clientes_Afectados"],
        var_name="Métrica",
        value_name="Valor"
    )

    ranking_mas_fig = px.bar(
        ranking_mas_melted,
        x="Valor",
        y="Distrito",
        color="Métrica",
        orientation="h",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "Cantidad_Fallas": colores_pluz["naranja"],
            "Clientes_Afectados": colores_pluz["verde"]
        },
        height=600,
        width=1100,
        title="🔝 Top 5 Distritos con Más Fallas (Total)"
    )

    # Barras apiladas para esos mismos distritos
    top5_distritos_mas = ranking_mas_data["Distrito"].tolist()
    df_barras_mas = df_grouped[df_grouped["Distrito"].isin(top5_distritos_mas)]

    barras_mas_fig = px.bar(
        df_barras_mas,
        x="Cantidad_Fallas",
        y="Distrito",
        color="Tipo de Fallas",
        orientation="h",
        barmode="stack",
        text_auto=True,
        height=600,
        width=1100,
        title="📊 Tipos de Fallas en Top 5 con Más Fallas (Total)"
    )

    # 3) TOP 5 DISTRITOS CON MENOS FALLAS (TOTAL)
    ranking_menos_data = df_grouped.groupby("Distrito")[["Cantidad_Fallas", "Clientes_Afectados"]] \
                                   .sum().reset_index() \
                                   .sort_values(by="Cantidad_Fallas", ascending=True) \
                                   .head(5)

    ranking_menos_melted = ranking_menos_data.melt(
        id_vars="Distrito",
        value_vars=["Cantidad_Fallas", "Clientes_Afectados"],
        var_name="Métrica",
        value_name="Valor"
    )

    ranking_menos_fig = px.bar(
        ranking_menos_melted,
        x="Valor",
        y="Distrito",
        color="Métrica",
        orientation="h",
        barmode="group",
        text_auto=True,
        color_discrete_map={
            "Cantidad_Fallas": colores_pluz["naranja"],
            "Clientes_Afectados": colores_pluz["verde"]
        },
        height=600,
        width=1100,
        title="🔻 Top 5 Distritos con Menos Fallas (Total)"
    )

    # Barras apiladas para esos distritos
    top5_distritos_menos = ranking_menos_data["Distrito"].tolist()
    df_barras_menos = df_grouped[df_grouped["Distrito"].isin(top5_distritos_menos)]

    barras_menos_fig = px.bar(
        df_barras_menos,
        x="Cantidad_Fallas",
        y="Distrito",
        color="Tipo de Fallas",
        orientation="h",
        barmode="stack",
        text_auto=True,
        height=600,
        width=1100,
        title="📊 Tipos de Fallas en Top 5 con Menos Fallas (Total)"
    )

    # 4) Texto total de fallas y clientes (GLOBAL)
    total_fallas = df_grouped["Cantidad_Fallas"].sum()
    total_clientes = df_grouped["Clientes_Afectados"].sum()
    texto_total = f"📌 Total de Fallas: {int(total_fallas):,} | Total de Clientes Afectados: {int(total_clientes):,}"

    return (
        heatmap_fig,
        ranking_mas_fig,
        barras_mas_fig,
        ranking_menos_fig,
        barras_menos_fig,
        texto_total
    )

# =========================
#  11. Ejecutar la aplicación
# =========================
if __name__ == "__main__":
    app.run_server(debug=True, host="10.155.247.72", port=8050)


