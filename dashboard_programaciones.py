# dashboard_programaciones.py
# Dashboard interactivo para analizar Excel de inscritos al Congreso
# Ejecutar con: streamlit run dashboard_programaciones.py

import io

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Dashboard de Seguimiento de Inscritos al Congreso 2026",
    page_icon="📊",
    layout="wide",
)

COLUMNAS_MINIMAS = {
    "Carrera",
    "Periodo",
    "Codigo",
    "Dni",
    "Servicio",
    "Importe",
    "Estado",
}


def encontrar_fila_header(archivo_excel, hoja=0) -> int:
    """Busca automáticamente la fila donde están las cabeceras reales."""
    preview = pd.read_excel(archivo_excel, sheet_name=hoja, header=None, nrows=25)
    archivo_excel.seek(0)

    for idx, row in preview.iterrows():
        valores = [str(x).strip() for x in row.dropna().tolist()]
        if "Carrera" in valores and "Periodo" in valores and "Estado" in valores:
            return idx

    return 0


def limpiar_texto_serie(serie: pd.Series) -> pd.Series:
    """Convierte una serie a texto limpio."""
    return serie.astype(str).str.strip().replace({"nan": "", "None": ""})


def cargar_excel(archivo_excel) -> pd.DataFrame:
    """Carga el Excel, detecta encabezado y limpia tipos de datos."""
    header_row = encontrar_fila_header(archivo_excel)
    archivo_excel.seek(0)

    df = pd.read_excel(archivo_excel, header=header_row)

    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]

    if "Carrera" in df.columns:
        df = df[df["Carrera"].astype(str).str.strip().str.lower() != "carrera"]

    faltantes = COLUMNAS_MINIMAS - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas necesarias: {', '.join(sorted(faltantes))}")

    for columna in ["Estado", "Carrera", "Servicio", "Periodo", "Codigo", "Dni"]:
        if columna in df.columns:
            df[columna] = limpiar_texto_serie(df[columna])

    df["Estado"] = df["Estado"].str.upper()
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)

    if "FechaPago" in df.columns:
        df["FechaPago"] = pd.to_datetime(df["FechaPago"], errors="coerce", dayfirst=True)

    apellidos = limpiar_texto_serie(df["Apellidos"]) if "Apellidos" in df.columns else ""
    nombres = limpiar_texto_serie(df["Nombres"]) if "Nombres" in df.columns else ""
    df["NombreCompleto"] = (apellidos + " " + nombres).str.strip()

    return df.reset_index(drop=True)


def formato_soles(valor: float) -> str:
    return f"S/ {valor:,.2f}"


def opciones_columna(df: pd.DataFrame, columna: str) -> list[str]:
    return sorted(
        [
            x
            for x in df[columna].dropna().unique().tolist()
            if str(x).strip() != ""
        ]
    )


def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    estados = opciones_columna(df, "Estado")
    carreras = opciones_columna(df, "Carrera")
    servicios = opciones_columna(df, "Servicio")

    estado_sel = st.sidebar.multiselect("Estado", estados, default=estados)
    carrera_sel = st.sidebar.multiselect("Carrera", carreras, default=carreras)
    servicio_sel = st.sidebar.multiselect("Servicio", servicios, default=servicios)

    df_filtrado = df[
        df["Estado"].isin(estado_sel)
        & df["Carrera"].isin(carrera_sel)
        & df["Servicio"].isin(servicio_sel)
    ].copy()

    if "FechaPago" in df_filtrado.columns and df_filtrado["FechaPago"].notna().any():
        fecha_min = df_filtrado["FechaPago"].min().date()
        fecha_max = df_filtrado["FechaPago"].max().date()

        rango = st.sidebar.date_input(
            "Rango de FechaPago",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max,
        )

        if isinstance(rango, tuple) and len(rango) == 2:
            inicio, fin = rango
            df_filtrado = df_filtrado[
                df_filtrado["FechaPago"].isna()
                | (
                    (df_filtrado["FechaPago"].dt.date >= inicio)
                    & (df_filtrado["FechaPago"].dt.date <= fin)
                )
            ]

    return df_filtrado


def mostrar_kpis(df: pd.DataFrame) -> None:
    total_registros = len(df)

    personas_unicas = (
        df["Dni"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .nunique()
        if "Dni" in df.columns
        else 0
    )

    cancelado = df[df["Estado"].eq("CANCELADO")]
    pendiente = df[df["Estado"].eq("PENDIENTE")]

    total_cancelados = len(cancelado)
    total_pendientes = len(pendiente)

    importe_cancelado = cancelado["Importe"].sum() if "Importe" in cancelado.columns else 0
    importe_pendiente = pendiente["Importe"].sum() if "Importe" in pendiente.columns else 0

    tasa_pago = (total_cancelados / total_registros * 100) if total_registros else 0

    html_kpis = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background: transparent;
            }}

            .kpi-container {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 14px;
                margin-top: 5px;
                margin-bottom: 5px;
            }}

            .kpi-card {{
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 16px 18px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
                min-height: 95px;
                box-sizing: border-box;
            }}

            .kpi-title {{
                font-size: 14px;
                font-weight: 600;
                color: #6b7280;
                margin-bottom: 8px;
            }}

            .kpi-value {{
                font-size: 30px;
                font-weight: 800;
                color: #111827;
                line-height: 1.2;
            }}

            .kpi-subtitle {{
                font-size: 12px;
                color: #9ca3af;
                margin-top: 6px;
            }}

            .kpi-card.info {{
                border-left: 6px solid #2563eb;
            }}

            .kpi-card.purple {{
                border-left: 6px solid #7c3aed;
            }}

            .kpi-card.success {{
                border-left: 6px solid #16a34a;
            }}

            .kpi-card.danger {{
                border-left: 6px solid #dc2626;
            }}

            .kpi-card.warning {{
                border-left: 6px solid #f59e0b;
            }}

            @media (max-width: 1100px) {{
                .kpi-container {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}

            @media (max-width: 700px) {{
                .kpi-container {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="kpi-container">
            <div class="kpi-card info">
                <div class="kpi-title">Total registros</div>
                <div class="kpi-value">{total_registros:,}</div>
            </div>

            <div class="kpi-card purple">
                <div class="kpi-title">Personas únicas</div>
                <div class="kpi-value">{personas_unicas:,}</div>
                <div class="kpi-subtitle">Calculado por DNI</div>
            </div>

            <div class="kpi-card success">
                <div class="kpi-title">Tasa de pago</div>
                <div class="kpi-value">{tasa_pago:.1f}%</div>
                <div class="kpi-subtitle">Cancelados / Total</div>
            </div>

            <div class="kpi-card danger">
                <div class="kpi-title">Cancelados</div>
                <div class="kpi-value">{total_cancelados:,}</div>
                <div class="kpi-subtitle">{formato_soles(importe_cancelado)}</div>
            </div>

            <div class="kpi-card warning">
                <div class="kpi-title">Pendientes</div>
                <div class="kpi-value">{total_pendientes:,}</div>
                <div class="kpi-subtitle">{formato_soles(importe_pendiente)}</div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(html_kpis, height=155, scrolling=False)


def grafico_vacio(mensaje: str) -> None:
    st.info(mensaje)


def mostrar_graficos(df: pd.DataFrame) -> None:
    st.subheader("Gráficos principales")

    col1, col2 = st.columns(2)

    with col1:
        estado_count = df.groupby("Estado", as_index=False).size()

        if estado_count.empty:
            grafico_vacio("No hay datos para graficar estados.")
        else:
            fig_estado = px.pie(
                estado_count,
                names="Estado",
                values="size",
                title="Distribución por estado",
                hole=0.45,
            )
            st.plotly_chart(fig_estado, use_container_width=True)

    with col2:
        carrera_count = (
            df.groupby("Carrera", as_index=False)
            .size()
            .sort_values("size", ascending=False)
        )

        if carrera_count.empty:
            grafico_vacio("No hay datos para graficar carreras.")
        else:
            fig_carrera = px.bar(
                carrera_count,
                x="Carrera",
                y="size",
                title="Cantidad de registros por carrera",
                text_auto=True,
            )
            fig_carrera.update_layout(xaxis_title="", yaxis_title="Registros")
            st.plotly_chart(fig_carrera, use_container_width=True)

    if "FechaPago" in df.columns and df["FechaPago"].notna().any():
        st.subheader("Evolución de pagos")

        pagos_dia = (
            df[df["FechaPago"].notna()]
            .groupby(df["FechaPago"].dt.date)
            .agg(Registros=("Importe", "size"), Importe=("Importe", "sum"))
            .reset_index()
            .rename(columns={"FechaPago": "Fecha"})
        )

        fig_pagos = px.line(
            pagos_dia,
            x="Fecha",
            y="Importe",
            markers=True,
            title="Importe pagado por fecha",
        )
        fig_pagos.update_layout(xaxis_title="Fecha", yaxis_title="Importe S/")
        st.plotly_chart(fig_pagos, use_container_width=True)


def mostrar_tablas(df: pd.DataFrame) -> None:
    st.subheader("Detalle de datos")

    columnas_mostrar = [
        c
        for c in [
            "Carrera",
            "Periodo",
            "Codigo",
            "Dni",
            "NombreCompleto",
            "Servicio",
            "Importe",
            "Estado",
            "FechaPago",
            "Recibo",
            "Correos",
            "Telefonos",
        ]
        if c in df.columns
    ]

    st.dataframe(df[columnas_mostrar], use_container_width=True, hide_index=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df[columnas_mostrar].to_excel(writer, index=False, sheet_name="Datos Filtrados")

    st.download_button(
        label="Descargar datos filtrados en Excel",
        data=buffer.getvalue(),
        file_name="datos_filtrados_dashboard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def main() -> None:
    st.title("📊 Dashboard de Seguimiento de Inscritos al Congreso 2026")
    st.caption(
        "Carga tu archivo Excel para generar KPIs, gráficos, filtros y una tabla descargable."
    )

    with st.expander("Columnas mínimas esperadas", expanded=False):
        st.write(", ".join(sorted(COLUMNAS_MINIMAS)))

    archivo = st.file_uploader(
        "Cargar archivo Excel",
        type=["xlsx", "xls"],
        help="Selecciona el reporte de inscritos al congreso.",
    )

    if archivo is None:
        st.info("Carga un archivo Excel para visualizar el dashboard.")
        st.stop()

    try:
        df = cargar_excel(archivo)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo: {e}")
        st.stop()

    st.success(f"Archivo cargado correctamente. Registros encontrados: {len(df):,}")

    df_filtrado = aplicar_filtros(df)

    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    mostrar_kpis(df_filtrado)
    mostrar_graficos(df_filtrado)
    mostrar_tablas(df_filtrado)


if __name__ == "__main__":
    main()
