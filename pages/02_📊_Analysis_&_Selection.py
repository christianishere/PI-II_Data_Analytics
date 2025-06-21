import yfinance as yf
import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

import ta
import time


# from selenium.webdriver import Firefox, FirefoxOptions
# from selenium.webdriver.common.by import By


df_bh = pd.read_csv("data/berkshire_porfolio.csv")


# DATAFRAME

st.header("Berkshire Hathaway Portfolio")
cant_empresas = len(df_bh)

st.write(
    f"""
      Size: **{cant_empresas} companies**.
"""
)

st.dataframe(df_bh)

st.write(
    f"""
      Source: **[hedgefollow.com](https://hedgefollow.com/funds/Berkshire+Hathaway)**

"""
)

hide_st_style = """
            <style>
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# MULTISELECCION DE EMPRESAS PARA ANALIZAR

selected_stocks = st.sidebar.multiselect(
    "Companies Selection to Analyze",
    df_bh["Stock"].unique(),
    default=df_bh["Stock"].unique()[:5],
)


# GRAFICO MULTI-INDICES (MEDIA MOVIL, RSI, CORRELACION MOVIL)

# Define los tickers que queremos visualizar
# tickers = ['AAPL', 'BAC', 'CVX', 'KO', 'AXP', 'KHC']


st.header("Technical Chart (Indicators) Selection")

# Crea un botón para cada ticker
ticker = st.radio("Choose an Option", selected_stocks)

# Descarga los datos del ticker utilizando yfinance
data = yf.download(ticker, start="2000-01-01")

# Debugging: Verificar la estructura de los datos descargados
print("Selected ticker:", ticker)
print("Data shape:", data.shape)
print("Close shape:", data["Close"].shape)
print("Close type:", type(data["Close"]))

# Calcula las medias móviles
sma50 = data["Close"].rolling(window=50).mean()
sma200 = data["Close"].rolling(window=200).mean()

# Debugging: Confirm data availability for price and moving averages
if isinstance(data["Close"], pd.DataFrame):
    close_values = data["Close"].iloc[:, 0].head().tolist()
else:
    close_values = data["Close"].head().tolist()
print("Precio de Cierre data available (first 5):", close_values)

if isinstance(sma50, pd.DataFrame):
    sma50_values = sma50.iloc[:, 0].dropna().head().tolist()
else:
    sma50_values = sma50.dropna().head().tolist()
print("SMA 50 data available (first 5 after NaN):", sma50_values)

if isinstance(sma200, pd.DataFrame):
    sma200_values = sma200.iloc[:, 0].dropna().head().tolist()
else:
    sma200_values = sma200.dropna().head().tolist()
print("SMA 200 data available (first 5 after NaN):", sma200_values)

# Calcula el índice RSI utilizando ta, asegurándose de que el input sea 1-dimensional
if isinstance(data["Close"], pd.DataFrame):
    print("Close is a DataFrame, converting to Series")
    close_series = data["Close"].iloc[:, 0]
else:
    print("Close is a Series, using directly")
    close_series = data["Close"]
data["RSI"] = ta.momentum.RSIIndicator(close_series, window=14).rsi()

# Calcula la volatilidad y la correlación móvil entre el rendimiento y la volatilidad
data["volatility"] = data["Close"].pct_change().rolling(window=252).std() * (252**0.5)
data["corr252"] = (
    data["Close"].pct_change().rolling(window=252).corr(data["volatility"])
)

# Crea el gráfico utilizando Plotly
fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.8, 0.1, 0.1],
)

# Debugging: Output row heights for chart proportions
print("Chart row heights:", [0.7, 0.15, 0.15])

# Agrega el gráfico de precios, asegurándose de que los datos sean Series
if isinstance(data["Close"], pd.DataFrame):
    close_series_plot = data["Close"].iloc[:, 0]
else:
    close_series_plot = data["Close"]
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=close_series_plot,
        name="Precio de cierre",
        line=dict(color="#FF0000", width=1.2),
    ),
    row=1,
    col=1,
)

if isinstance(sma50, pd.DataFrame):
    sma50_series_plot = sma50.iloc[:, 0]
else:
    sma50_series_plot = sma50
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=sma50_series_plot,
        name="SMA 50",
        line=dict(dash="dash", color="#008000", width=0.8),
    ),
    row=1,
    col=1,
)

if isinstance(sma200, pd.DataFrame):
    sma200_series_plot = sma200.iloc[:, 0]
else:
    sma200_series_plot = sma200
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=sma200_series_plot,
        name="SMA 200",
        line=dict(dash="dash", color="#FFA500", width=0.8),
    ),
    row=1,
    col=1,
)

# Debugging: Confirm data length and content for plotting
print("Precio de Cierre data length for plotting:", len(close_series_plot))
print("SMA 50 data length for plotting:", len(sma50_series_plot.dropna()))
print("SMA 200 data length for plotting:", len(sma200_series_plot.dropna()))

# Debugging: Output line properties for Precio de Cierre, SMA 50, and SMA 200
print("Precio de Cierre line properties: color=#FF0000, width=1.2")
print("SMA 50 line properties: color=#008000, dash=dash, width=0.8")
print("SMA 200 line properties: color=#FFA500, dash=dash, width=0.8")

# Agrega el subgráfico de RSI
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["RSI"],
        name="RSI",
        yaxis="y2",
        line=dict(color="#00BFFF", width=0.5),
    ),
    row=2,
    col=1,
)

# Agrega el subgráfico de correlación móvil
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["corr252"],
        name="Correlación móvil",
        line=dict(color="#32CD32", width=0.5),
    ),
    row=3,
    col=1,
)

# Debugging: Output colors for RSI and Correlación móvil
print("RSI line properties: color=#00BFFF, width=0.5")
print("Correlación móvil line properties: color=#32CD32, width=0.5")

# Agrega una línea horizontal en y=70 y en y=30 para remarcar el valor para RSI con anotaciones
fig.add_shape(
    type="line",
    x0=data.index[0],
    x1=data.index[-1],
    y0=70,
    y1=70,
    line=dict(color="#808080", width=1.2),
    row=2,
    col=1,
)
fig.add_shape(
    type="line",
    x0=data.index[0],
    x1=data.index[-1],
    y0=30,
    y1=30,
    line=dict(color="#808080", width=1.2),
    row=2,
    col=1,
)
# Añadir anotaciones para aclarar el propósito de las líneas horizontales
fig.add_annotation(
    xref="paper",
    yref="y2",
    x=0.02,
    y=70,
    text="Overbought (70)",
    showarrow=False,
    font=dict(size=10, color="#000000"),
    row=2,
    col=1,
)
fig.add_annotation(
    xref="paper",
    yref="y2",
    x=0.02,
    y=30,
    text="Oversold (30)",
    showarrow=False,
    font=dict(size=10, color="#000000"),
    row=2,
    col=1,
)

# Debugging: Confirm annotations and horizontal lines for RSI thresholds
print("RSI Overbought line at y=70 added with annotation")
print("RSI Oversold line at y=30 added with annotation")


# Define el diseño del gráfico
fig.update_layout(title=ticker, height=800)

# Debugging: Confirm chart height
print("Chart height set to:", 800)

# Define el diseño de los ejes
fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
fig.update_xaxes(rangeslider_visible=False, row=2, col=1)
fig.update_xaxes(rangeslider_visible=False, row=3, col=1)
fig.update_yaxes(title_text="Precio de cierre", row=1, col=1)
fig.update_yaxes(title_text="RSI", row=2, col=1, side="left")
fig.update_yaxes(title_text="Correlac.móvil", row=3, col=1, side="left")

# fig.update_xaxes(
#    rangeslider_visible=False,
#    rangeselector=dict(
#        buttons=list([
#            dict(count=1, label="1m", step="month", stepmode="backward"),
#            dict(count=6, label="6m", step="month", stepmode="backward"),
#            dict(count=1, label="YTD", step="year", stepmode="todate"),
#            dict(count=1, label="1y", step="year", stepmode="backward"),
#            dict(count=5, label="5y", step="year", stepmode="backward"),
#            dict(count=10, label="10y", step="year", stepmode="backward"),
#            dict(step="all")
#        ])
#    )
# )

# Obtener la fecha actual
today = dt.date.today()

# Definir la fecha de inicio como hace un año
start_date = today - dt.timedelta(days=365)

# Establecer el rango de fechas por defecto para el botón "1y"
fig.update_layout(
    xaxis=dict(
        range=[start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(count=10, label="10y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )
)

st.plotly_chart(fig)

# Debugging: Confirm chart rendering with default width
print("Chart rendered with default width")


# Selección final de acciones para inversión

# st.write("Editable DataFrame", df.style.format({True: "✅", False: "❌"}), unsafe_allow_html=True)

# Tìtulo
st.markdown(
    '<p style="font-size:32px;background-color:#d9d9d9;color:red;font-weight:bold;text-align:center">FINAL STOCKS SELECTION</p>',
    unsafe_allow_html=True,
)

# Dataframe editable
final_selection = {"Stock": selected_stocks, "Selected": [True] * len(selected_stocks)}
df_final_selection = pd.DataFrame(final_selection)

edited_df = st.experimental_data_editor(df_final_selection)

# Debugging: Output the current state of the edited DataFrame
print("Final Stocks Selection DataFrame state:")
print(edited_df)

# Display updated selections dynamically
selected_stocks_updated = edited_df[edited_df["Selected"] == True]["Stock"].tolist()
if selected_stocks_updated:
    st.markdown(
        f"**Currently Selected Stocks for Investment:** {', '.join(selected_stocks_updated)}"
    )
else:
    st.markdown("**No stocks currently selected for investment.**")

# Add a confirmation button for final selection
if st.button("Confirm Final Selection"):
    if selected_stocks_updated:
        st.success(
            f"Selection confirmed! Final stocks for investment: {', '.join(selected_stocks_updated)}"
        )
    else:
        st.warning(
            "No stocks selected for investment. Please select at least one stock."
        )

# Debugging: Output the list of currently selected stocks and button interaction
print("Currently selected stocks for investment:", selected_stocks_updated)
print("Confirm Final Selection button rendered")
