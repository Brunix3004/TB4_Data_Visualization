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