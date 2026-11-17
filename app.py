import pandas as pd
import streamlit as st

# ---------- Configuración de la página ----------
st.set_page_config(page_title="Panel de ventas", page_icon="📊", layout="wide")

st.title("📊 Panel de ventas 2026")
st.caption("Datos ficticios de una tienda de ropa, generados para la demostración.")


# ---------- Carga de datos ----------
@st.cache_data
def cargar_datos(ruta):
    df = pd.read_csv(ruta, parse_dates=["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    return df


df = cargar_datos("ventas.csv")

# ---------- Filtros en la barra lateral ----------
st.sidebar.header("Filtros")

ciudades = st.sidebar.multiselect(
    "Ciudad", sorted(df["ciudad"].unique()), default=sorted(df["ciudad"].unique())
)
categorias = st.sidebar.multiselect(
    "Categoría", sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique())
)
vendedores = st.sidebar.multiselect(
    "Vendedor", sorted(df["vendedor"].unique()), default=sorted(df["vendedor"].unique())
)

fecha_min, fecha_max = df["fecha"].min().date(), df["fecha"].max().date()
rango = st.sidebar.date_input(
    "Rango de fechas", (fecha_min, fecha_max), min_value=fecha_min, max_value=fecha_max
)

filtrado = df[
    df["ciudad"].isin(ciudades)
    & df["categoria"].isin(categorias)
    & df["vendedor"].isin(vendedores)
]
if len(rango) == 2:
    filtrado = filtrado[
        (filtrado["fecha"].dt.date >= rango[0]) & (filtrado["fecha"].dt.date <= rango[1])
    ]

if filtrado.empty:
    st.warning("No hay datos con esos filtros. Prueba ampliando la selección.")
    st.stop()

# ---------- Indicadores principales ----------
total_ventas = filtrado["total"].sum()
unidades = filtrado["unidades"].sum()
num_ventas = len(filtrado)
ticket_promedio = total_ventas / num_ventas

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas totales", f"${total_ventas:,.0f}")
c2.metric("Unidades vendidas", f"{unidades:,}")
c3.metric("Número de ventas", f"{num_ventas:,}")
c4.metric("Ticket promedio", f"${ticket_promedio:,.0f}")

st.divider()

# ---------- Pestañas ----------
tab1, tab2, tab3 = st.tabs(["📈 Tendencia", "🏆 Rankings", "🗂️ Datos"])

with tab1:
    st.subheader("Ventas por mes")
    por_mes = filtrado.groupby("mes")["total"].sum()
    st.line_chart(por_mes)

    st.subheader("Ventas por mes y categoría")
    por_mes_cat = filtrado.pivot_table(
        index="mes", columns="categoria", values="total", aggfunc="sum", fill_value=0
    )
    st.bar_chart(por_mes_cat)

with tab2:
    izq, der = st.columns(2)

    with izq:
        st.subheader("Top productos")
        top_prod = (
            filtrado.groupby("producto")["total"].sum().sort_values(ascending=False)
        )
        st.bar_chart(top_prod)

        st.subheader("Ventas por ciudad")
        st.bar_chart(filtrado.groupby("ciudad")["total"].sum().sort_values(ascending=False))

    with der:
        st.subheader("Ventas por vendedor")
        st.bar_chart(filtrado.groupby("vendedor")["total"].sum().sort_values(ascending=False))

        st.subheader("Detalle de productos")
        resumen = (
            filtrado.groupby("producto")
            .agg(unidades=("unidades", "sum"), total=("total", "sum"))
            .sort_values("total", ascending=False)
            .reset_index()
        )
        st.dataframe(resumen, width="stretch", hide_index=True)

with tab3:
    st.subheader("Tabla de ventas")
    st.dataframe(filtrado.drop(columns="mes"), width="stretch", hide_index=True)

    st.download_button(
        "⬇️ Descargar datos filtrados (CSV)",
        data=filtrado.drop(columns="mes").to_csv(index=False).encode("utf-8"),
        file_name="ventas_filtradas.csv",
        mime="text/csv",
    )