# Dashboard de Programaciones por Servicio

Proyecto desarrollado con **Python + Streamlit** para cargar un archivo Excel y generar automáticamente KPIs, gráficos, filtros y una tabla descargable.

## Tecnologías usadas

- Python
- Streamlit
- Pandas
- Plotly
- OpenPyXL

## Estructura del proyecto

```text
dashboard-programaciones/
│
├── dashboard_programaciones.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── data/
    └── .gitkeep
```

## Instalación local

Abre una terminal dentro de la carpeta del proyecto y ejecuta:

```bash
python -m venv venv
```

Activa el entorno virtual.

En Windows CMD:

```bash
venv\Scripts\activate
```

En Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run dashboard_programaciones.py
```

También puedes usar:

```bash
python -m streamlit run dashboard_programaciones.py
```

Luego abre la URL que aparece en la terminal, normalmente:

```text
http://localhost:8501
```

## Uso del dashboard

1. Ejecuta la aplicación.
2. Carga tu archivo Excel desde el botón **Cargar archivo Excel**.
3. Usa los filtros del panel lateral.
4. Revisa los KPIs y gráficos.
5. Descarga la información filtrada en Excel.

## Columnas mínimas esperadas

El Excel debe contener como mínimo estas columnas:

- Carrera
- Periodo
- Codigo
- Dni
- Servicio
- Importe
- Estado

Columnas opcionales recomendadas:

- Apellidos
- Nombres
- FechaPago
- Recibo
- Correos
- Telefonos

## Nota de seguridad

No subas archivos Excel reales con información sensible a GitHub. El archivo `.gitignore` está configurado para evitar subir archivos `.xlsx` y `.xls`.
