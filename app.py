import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# CEDI OPERATIONS ANALYTICS
# Dashboard de operaciones para un Centro de Distribución
# ============================================================

st.set_page_config(
    page_title="CEDI Operations Analytics",
    page_icon="📦",
    layout="wide"
)

# ------------------------------------------------------------
# TÍTULO
# ------------------------------------------------------------

st.title("📦 CEDI Operations Analytics")
st.caption(
    "Dashboard de análisis operativo para Centros de Distribución"
)

# ------------------------------------------------------------
# GENERACIÓN DE DATOS SIMULADOS
# ------------------------------------------------------------

@st.cache_data
def generate_data():

    np.random.seed(42)

    n = 1000

    dates = pd.date_range(
        start="2026-01-01",
        end="2026-03-31",
        periods=n
    )

    pedidos = np.random.randint(20, 100, n)
    unidades = np.random.randint(300, 1800, n)

    pedidos_a_tiempo = np.random.randint(
        15,
        90,
        n
    )

    pedidos_completos = np.random.randint(
        18,
        100,
        n
    )

    # Evitamos que los valores sean mayores que los pedidos
    pedidos_completos = np.minimum(
        pedidos_completos,
        pedidos
    )

    pedidos_a_tiempo = np.minimum(
        pedidos_a_tiempo,
        pedidos_completos
    )

    unidades_correctas = (
        unidades * np.random.uniform(0.95, 1.00, n)
    ).astype(int)

    unidades_despachadas = (
        unidades * np.random.uniform(0.90, 1.00, n)
    ).astype(int)

    df = pd.DataFrame({
        "Fecha": dates,
        "Turno": np.random.choice(
            ["Turno A", "Turno B", "Turno C"],
            n
        ),
        "Operador": [
            f"OP-{str(x).zfill(3)}"
            for x in np.random.randint(1, 51, n)
        ],
        "Pedidos": pedidos,
        "Unidades": unidades,
        "Horas_Trabajadas": np.round(
            np.random.uniform(6, 9, n),
            2
        ),
        "Pedidos_Completos": pedidos_completos,
        "Pedidos_A_Tiempo": pedidos_a_tiempo,
        "Unidades_Correctas": unidades_correctas,
        "Unidades_Despachadas": unidades_despachadas
    })

    # --------------------------------------------------------
    # CÁLCULO DE KPIs
    # --------------------------------------------------------

    df["Productividad"] = (
        df["Unidades"] /
        df["Horas_Trabajadas"]
    ).round(2)

    df["OTIF"] = (
        df["Pedidos_A_Tiempo"] /
        df["Pedidos"] *
        100
    ).round(2)

    df["Exactitud_Inventario"] = (
        df["Unidades_Correctas"] /
        df["Unidades"] *
        100
    ).round(2)

    df["Fill_Rate"] = (
        df["Unidades_Despachadas"] /
        df["Unidades"] *
        100
    ).round(2)

    return df


df = generate_data()

# ------------------------------------------------------------
# FILTROS
# ------------------------------------------------------------

st.sidebar.header("Filtros")

turnos = st.sidebar.multiselect(
    "Turno",
    options=sorted(df["Turno"].unique()),
    default=sorted(df["Turno"].unique())
)

fecha_inicio = st.sidebar.date_input(
    "Fecha inicial",
    value=df["Fecha"].min().date()
)

fecha_fin = st.sidebar.date_input(
    "Fecha final",
    value=df["Fecha"].max().date()
)

filtered_df = df[
    (df["Turno"].isin(turnos)) &
    (df["Fecha"].dt.date >= fecha_inicio) &
    (df["Fecha"].dt.date <= fecha_fin)
]

# ------------------------------------------------------------
# KPIs PRINCIPALES
# ------------------------------------------------------------

st.subheader("KPIs Operativos")

col1, col2, col3, col4 = st.columns(4)

productividad = filtered_df["Productividad"].mean()
otif = filtered_df["OTIF"].mean()
exactitud = filtered_df["Exactitud_Inventario"].mean()
fill_rate = filtered_df["Fill_Rate"].mean()

col1.metric(
    "Productividad",
    f"{productividad:,.0f} u/h"
)

col2.metric(
    "OTIF",
    f"{otif:.1f}%"
)

col3.metric(
    "Exactitud",
    f"{exactitud:.1f}%"
)

col4.metric(
    "Fill Rate",
    f"{fill_rate:.1f}%"
)

st.divider()

# ------------------------------------------------------------
# PRODUCTIVIDAD POR TURNO
# ------------------------------------------------------------

st.subheader("Productividad por turno")

productividad_turno = (
    filtered_df
    .groupby("Turno")["Productividad"]
    .mean()
    .reset_index()
)

fig_turno = px.bar(
    productividad_turno,
    x="Turno",
    y="Productividad",
    text_auto=".0f",
    title="Productividad promedio por turno",
    labels={
        "Productividad": "Unidades por hora",
        "Turno": "Turno"
    }
)

st.plotly_chart(
    fig_turno,
    use_container_width=True
)

# ------------------------------------------------------------
# EVOLUCIÓN DE KPIs
# ------------------------------------------------------------

st.subheader("Evolución de indicadores")

daily = (
    filtered_df
    .set_index("Fecha")
    .resample("D")
    .agg({
        "Productividad": "mean",
        "OTIF": "mean",
        "Exactitud_Inventario": "mean",
        "Fill_Rate": "mean"
    })
    .reset_index()
)

metric = st.selectbox(
    "Selecciona el indicador",
    [
        "Productividad",
        "OTIF",
        "Exactitud_Inventario",
        "Fill_Rate"
    ]
)

fig_trend = px.line(
    daily,
    x="Fecha",
    y=metric,
    markers=True,
    title=f"Evolución de {metric}"
)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)

# ------------------------------------------------------------
# ANÁLISIS POR OPERADOR
# ------------------------------------------------------------

st.subheader("Desempeño por operador")

operator_analysis = (
    filtered_df
    .groupby("Operador")
    .agg(
        Productividad=("Productividad", "mean"),
        OTIF=("OTIF", "mean"),
        Exactitud=("Exactitud_Inventario", "mean"),
        Unidades=("Unidades", "sum")
    )
    .reset_index()
    .sort_values(
        "Productividad",
        ascending=False
    )
)

st.dataframe(
    operator_analysis,
    use_container_width=True,
    hide_index=True
)

# ------------------------------------------------------------
# ALERTAS OPERATIVAS
# ------------------------------------------------------------

st.subheader("Alertas operativas")

OBJETIVO_PRODUCTIVIDAD = 150
OBJETIVO_OTIF = 95
OBJETIVO_EXACTITUD = 98

alertas = []

if productividad < OBJETIVO_PRODUCTIVIDAD:
    alertas.append(
        f"Productividad por debajo del objetivo: "
        f"{productividad:.0f} u/h"
    )

if otif < OBJETIVO_OTIF:
    alertas.append(
        f"OTIF por debajo del objetivo: "
        f"{otif:.1f}%"
    )

if exactitud < OBJETIVO_EXACTITUD:
    alertas.append(
        f"Exactitud de inventario por debajo del objetivo: "
        f"{exactitud:.1f}%"
    )

if not alertas:
    st.success(
        "Los principales indicadores se encuentran "
        "dentro de los objetivos definidos."
    )
else:
    for alerta in alertas:
        st.warning(alerta)

# ------------------------------------------------------------
# RESUMEN
# ------------------------------------------------------------

st.divider()

st.subheader("Resumen del análisis")

st.write(
    f"""
    El análisis considera **{len(filtered_df):,} registros
    operativos**.

    La productividad promedio es de
    **{productividad:,.0f} unidades/hora**.

    El OTIF promedio es de **{otif:.1f}%**,
    la exactitud de inventario es de
    **{exactitud:.1f}%** y el Fill Rate es de
    **{fill_rate:.1f}%**.

    Los datos utilizados son simulados con fines
    demostrativos y no representan información
    confidencial de ninguna empresa.
    """
)

st.caption(
    "CEDI Operations Analytics | Supply Chain & Data Analytics"
)
