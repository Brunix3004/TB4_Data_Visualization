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
