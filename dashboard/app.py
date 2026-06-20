import pandas as pd
import plotly.express as px
import streamlit as st

# ==================================================
# CONFIGURACIÓN
# ==================================================
st.set_page_config(
    page_title="Global Energy Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ==================================================
# CARGAR DATA
# ==================================================
df = pd.read_csv("data/merged_imputed.csv")

# Solo años del trabajo
df = df[(df["year"] >= 2000) & (df["year"] <= 2020)].copy()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("⚙️ Filtros")

years = sorted(df["year"].unique())

year_range = st.sidebar.slider(
    "Rango de años",
    min_value=min(years),
    max_value=max(years),
    value=(2000, 2020)
)

df = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# ==================================================
# TÍTULO
# ==================================================
st.title("🌍 Global Energy Transition Dashboard")
st.caption("Análisis de energía mundial (2000 - 2020)")

st.divider()

# ==================================================
# DOS COLUMNAS
# ==================================================
col1, col2 = st.columns(2)

# ==================================================
# GRÁFICO 1
# ==================================================
with col1:

    st.subheader("🌱 Top 5 países con mayor crecimiento en energías renovables")

    df_q1 = df[
        ["country", "year", "renewable_share_of_total_energy"]
    ].copy()

    pivot = (
        df_q1
        .pivot_table(
            index="country",
            columns="year",
            values="renewable_share_of_total_energy",
            aggfunc="mean"
        )
    )

    # Solo países con información en ambos años
    if 2000 in pivot.columns and 2020 in pivot.columns:

        pivot = pivot.dropna(subset=[2000, 2020])

        pivot["Incremento"] = pivot[2020] - pivot[2000]

        top5 = (
            pivot
            .sort_values("Incremento", ascending=False)
            .head(5)
            .reset_index()
        )

        fig1 = px.bar(
            top5,
            x="Incremento",
            y="country",
            orientation="h",
            text="Incremento",
            color="Incremento",
            color_continuous_scale="Greens"
        )

        fig1.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig1.update_layout(
            xaxis_title="Incremento (puntos porcentuales)",
            yaxis_title="",
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
            height=500
        )

        st.plotly_chart(fig1, width="stretch")

    else:
        st.warning("El rango seleccionado debe incluir los años 2000 y 2020.")

# ==================================================
# GRÁFICO 2
# ==================================================
with col2:

    st.subheader("🌍 Evolución de la intensidad de carbono por región")

    if "region" in df.columns:

        region_df = (
            df.groupby(
                ["region", "year"],
                as_index=False
            )["carbon_intensity_elec"]
            .mean()
        )

        fig2 = px.line(
            region_df,
            x="year",
            y="carbon_intensity_elec",
            color="region",
            markers=True
        )

        fig2.update_layout(
            xaxis_title="Año",
            yaxis_title="Intensidad de carbono",
            legend_title="Región",
            height=500
        )

        st.plotly_chart(fig2, width="stretch")

    else:
        st.error(
            "No existe la columna 'region'. "
            "Debes crearla antes de generar este gráfico."
        )

st.divider()

# ==================================================
# GRÁFICO 5 - Ranking de consumo per cápita
# ==================================================
st.subheader("📊 Ranking de los 12 mayores consumidores de energía per cápita")

top12 = (
    df[df["year"].between(2000, 2020)]
    .groupby("year")[["country", "year", "energy_per_capita"]]
    .apply(lambda g: g.nlargest(12, "energy_per_capita"))
    .reset_index(drop=True)
)
top12["rank"] = top12.groupby("year")["energy_per_capita"].rank(
    ascending=False, method="first"
)

fig5 = px.line(
    top12, x="year", y="rank", color="country", markers=True,
    title="Qatar lideró el ranking de consumo energético per cápita entre 2000 y 2020"
)

fig5.update_yaxes(autorange="reversed", dtick=1, title="Ranking")
fig5.update_xaxes(dtick=2, title="Año")
fig5.update_layout(height=600, hovermode="x unified")

st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ==================================================
# GRÁFICO 6 — Mix eléctrico por país
# ==================================================
st.subheader("⚡ Mix eléctrico por país (año de mayor producción renovable)")

paises = sorted(df["country"].unique())
pais_seleccionado = st.selectbox("Selecciona un país", paises, key="pais_mix")

fuentes = ["coal_electricity", "gas_electricity", "nuclear_electricity", "solar_electricity", "wind_electricity", "hydro_electricity"]
etiquetas = ["Carbón", "Gas", "Nuclear", "Solar", "Eólica", "Hidro"]

datos_pais = df[df["country"] == pais_seleccionado].copy()
if not datos_pais.empty:
    anio_max_ren = datos_pais.loc[datos_pais["renewables_electricity"].idxmax(), "year"]
    fila = datos_pais[datos_pais["year"] == anio_max_ren].iloc[0]
    valores = [fila[f] for f in fuentes]
    pct = [v / sum(valores) * 100 if sum(valores) > 0 else 0 for v in valores]

    tabla_mix = pd.DataFrame({"fuente": etiquetas, "porcentaje": pct, "categoria": ""})
    tabla_mix = tabla_mix.sort_values("porcentaje", ascending=False)

    fig6 = px.bar(
        tabla_mix, x="porcentaje", y="categoria", color="fuente", orientation="h",
        barmode="stack", text_auto=".1f",
        title=f"Mix eléctrico ({pais_seleccionado} - {int(anio_max_ren)})",
        labels={"porcentaje": "Porcentaje (%)", "categoria": ""},
        category_orders={"fuente": tabla_mix["fuente"].tolist()}
    )

    fig6.update_xaxes(range=[0, 100])
    fig6.update_layout(height=400)

    st.plotly_chart(fig6, use_container_width=True)
else:
    st.warning(f"No hay datos para {pais_seleccionado}.")

st.divider()

# ==================================================
# GRÁFICO 7 — América Latina: intensidad de carbono
# ==================================================
st.subheader("🌿 P7 · ¿Quiénes mejoraron en América Latina? (intensidad de carbono 2000–2020)")

df_latam = df[df["region"] == "Latin America & Caribbean"].copy()

# Delta por país entre 2000 y 2020
pivot_ci = (
    df_latam[df_latam["year"].isin([2000, 2020])]
    .pivot_table(index="country", columns="year", values="carbon_intensity_elec", aggfunc="mean")
)

if 2000 in pivot_ci.columns and 2020 in pivot_ci.columns:
    pivot_ci = pivot_ci.dropna(subset=[2000, 2020])
    pivot_ci["delta"] = pivot_ci[2020] - pivot_ci[2000]
    pivot_ci["direction"] = pivot_ci["delta"].apply(lambda x: "Mejoró ↓" if x < 0 else "Empeoró ↑")
    pivot_ci = pivot_ci.reset_index().sort_values("delta")

    # ← FIX: renombrar columnas enteras a strings legibles
    pivot_ci = pivot_ci.rename(columns={2000: "ci_2000", 2020: "ci_2020"})

    fig7 = px.bar(
        pivot_ci,
        x="delta",
        y="country",
        orientation="h",
        color="direction",
        color_discrete_map={"Mejoró ↓": "#1a9850", "Empeoró ↑": "#d73027"},
        text="delta",
        hover_data={
            "country": True,
            "delta": ":.2f",
            "ci_2000": ":.2f",   # ← ahora sí existe
            "ci_2020": ":.2f",   # ← ahora sí existe
            "direction": False,
        },
        labels={"delta": "Δ Intensidad de carbono (gCO₂/kWh)", "country": ""},
    )

    fig7.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig7.update_layout(
        xaxis_title="Cambio en intensidad de carbono (gCO₂/kWh) — negativo = mejora",
        yaxis=dict(categoryorder="total ascending"),
        legend_title="Dirección",
        height=600,
        shapes=[dict(
            type="line", x0=0, x1=0, y0=-0.5, y1=len(pivot_ci) - 0.5,
            line=dict(color="black", width=1.5, dash="dash")
        )]
    )

    st.plotly_chart(fig7, use_container_width=True)

else:
    st.warning("No hay datos de carbon_intensity_elec para 2000 y 2020 en América Latina.")

st.divider()

# ==================================================
# GRÁFICO 8 — Perú vs. promedio América Latina
# ==================================================
st.subheader("🇵🇪 P8 · Perú en la región — 3 dimensiones vs. promedio latinoamericano")

DIMS = {
    "renewable_share_of_total_energy": "Renovables (% energía total)",
    "access_to_electricity":           "Acceso electricidad (%)",
    "energy_intensity_primary_energy": "Intensidad energética (MJ/$)",
}

# Usar el último año disponible con datos completos para las 3 métricas
df_latam_full = df[df["region"] == "Latin America & Caribbean"].copy()

years_available = (
    df_latam_full.dropna(subset=list(DIMS.keys()))
    ["year"].unique()
)

if len(years_available) == 0:
    st.warning("Sin datos completos para las 3 dimensiones en América Latina.")
else:
    ref_year = int(max(years_available))

    df_ref = df_latam_full[df_latam_full["year"] == ref_year]
    la_mean = df_ref[list(DIMS.keys())].mean()

    peru_row = df_ref[df_ref["country"] == "Peru"]

    if peru_row.empty:
        st.warning(f"No hay datos de Perú para {ref_year}.")
    else:
        peru_vals = peru_row[list(DIMS.keys())].iloc[0]

        # Normalizar 0-1 dentro de los valores LA de ese año (para radar)
        col_min = df_ref[list(DIMS.keys())].min()
        col_max = df_ref[list(DIMS.keys())].max()

        def normalize(series):
            return ((series - col_min) / (col_max - col_min)).fillna(0)

        peru_norm  = normalize(peru_vals)
        la_norm    = normalize(la_mean)

        categories = list(DIMS.values())

        import plotly.graph_objects as go

        fig8 = go.Figure()

        fig8.add_trace(go.Scatterpolar(
            r=list(la_norm) + [la_norm.iloc[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=f"Promedio AL ({ref_year})",
            line_color="#4393c3",
            fillcolor="rgba(67,147,195,0.2)",
            hovertemplate=(
                "<b>Promedio AL</b><br>"
                + "<br>".join(
                    f"{lab}: {la_mean[col]:.2f}"
                    for col, lab in DIMS.items()
                )
                + "<extra></extra>"
            ),
        ))

        fig8.add_trace(go.Scatterpolar(
            r=list(peru_norm) + [peru_norm.iloc[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=f"Perú ({ref_year})",
            line_color="#d6604d",
            fillcolor="rgba(214,96,77,0.2)",
            hovertemplate=(
                "<b>Perú</b><br>"
                + "<br>".join(
                    f"{lab}: {peru_vals[col]:.2f}"
                    for col, lab in DIMS.items()
                )
                + "<extra></extra>"
            ),
        ))

        fig8.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            legend=dict(orientation="h", y=-0.15),
            height=520,
        )

        # Tabla de valores reales debajo del radar
        col_a, col_b, col_c = st.columns(3)
        for i, (col_key, label) in enumerate(DIMS.items()):
            val_peru = peru_vals[col_key]
            val_la   = la_mean[col_key]
            diff     = val_peru - val_la
            arrow    = "▲" if diff > 0 else "▼"
            color    = "green" if diff > 0 else "red"
            [col_a, col_b, col_c][i].metric(
                label=label,
                value=f"{val_peru:.2f}",
                delta=f"{arrow} {abs(diff):.2f} vs. prom. AL"
            )

        st.plotly_chart(fig8, use_container_width=True)
        st.caption(f"Valores normalizados 0-1 dentro de América Latina. Año de referencia: {ref_year}. Valores reales en las métricas superiores.")

st.divider()

# ==================================================
# GRÁFICO 9 — Consumo de energía per cápita
# ==================================================
st.subheader("📈 P9 · Trayectoria de Perú en consumo de energía per cápita")

P9_COUNTRIES = ["Peru", "Chile", "Colombia", "Brazil"]
P9_COLORS = {
    "Peru": "#d6604d",
    "Chile": "#4393c3",
    "Colombia": "#74add1",
    "Brazil": "#8073ac",
}

df_p9 = (
    df[df["country"].isin(P9_COUNTRIES)]
    [["country", "year", "energy_per_capita"]]
    .dropna(subset=["energy_per_capita"])
    .sort_values(["year", "country"])
)

missing_countries = set(P9_COUNTRIES) - set(df_p9["country"].unique())

if missing_countries:
    st.warning(
        "No hay datos de consumo energético per cápita para: "
        + ", ".join(sorted(missing_countries))
        + "."
    )
else:
    fig9 = px.line(
        df_p9,
        x="year",
        y="energy_per_capita",
        color="country",
        markers=True,
        category_orders={"country": P9_COUNTRIES},
        color_discrete_map=P9_COLORS,
        labels={
            "year": "Año",
            "energy_per_capita": "Consumo de energía per cápita (kWh)",
            "country": "País",
        },
    )

    # Destacar Perú frente a los tres países de comparación.
    for trace in fig9.data:
        if trace.name == "Peru":
            trace.update(line=dict(width=4), marker=dict(size=8))
        else:
            trace.update(line=dict(width=2), marker=dict(size=6))

    fig9.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Año: %{x}<br>"
            "Consumo: %{y:,.0f} kWh por persona"
            "<extra></extra>"
        )
    )
    fig9.update_layout(
        legend_title="País",
        height=540,
        hovermode="x unified",
    )

    st.plotly_chart(fig9, use_container_width=True)

    # Medir la distancia de Perú respecto al promedio de Chile, Colombia y Brasil.
    p9_pivot = df_p9.pivot_table(
        index="year",
        columns="country",
        values="energy_per_capita",
        aggfunc="mean",
    ).dropna(subset=P9_COUNTRIES)

    if not p9_pivot.empty:
        p9_pivot["promedio_comparacion"] = p9_pivot[
            ["Chile", "Colombia", "Brazil"]
        ].mean(axis=1)
        p9_pivot["brecha_peru"] = (
            p9_pivot["Peru"] - p9_pivot["promedio_comparacion"]
        ).abs()

        year_closest = p9_pivot["brecha_peru"].idxmin()
        year_farthest = p9_pivot["brecha_peru"].idxmax()

        st.caption(
            f"En el rango seleccionado, Perú estuvo más cerca del promedio de Chile, "
            f"Colombia y Brasil en {year_closest} "
            f"(brecha de {p9_pivot.loc[year_closest, 'brecha_peru']:,.0f} kWh por persona) "
            f"y más lejos en {year_farthest} "
            f"(brecha de {p9_pivot.loc[year_farthest, 'brecha_peru']:,.0f} kWh por persona)."
        )
