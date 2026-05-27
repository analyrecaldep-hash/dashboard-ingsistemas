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
    tasa_pago = (total_cancelados / total_registros * 100) if total_registros else 0

    html_kpis = f"""
    <style>
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(5, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 20px;
            margin-bottom: 30px;
        }}

        .kpi-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
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

    <div class="kpi-container">
        <div class="kpi-card info">
            <div class="kpi-title">Total registros</div>
            <div class="kpi-value">{total_registros:,}</div>
        </div>

        <div class="kpi-card purple">
            <div class="kpi-title">Personas únicas</div>
            <div class="kpi-value">{personas_unicas:,}</div>
        </div>

        <div class="kpi-card success">
            <div class="kpi-title">Tasa de pago</div>
            <div class="kpi-value">{tasa_pago:.1f}%</div>
        </div>

        <div class="kpi-card danger">
            <div class="kpi-title">Cancelados</div>
            <div class="kpi-value">{total_cancelados:,}</div>
        </div>

        <div class="kpi-card warning">
            <div class="kpi-title">Pendientes</div>
            <div class="kpi-value">{total_pendientes:,}</div>
        </div>
    </div>
    """

    st.markdown(html_kpis, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
