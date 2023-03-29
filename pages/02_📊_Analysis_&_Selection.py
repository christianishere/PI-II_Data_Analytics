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




#from selenium.webdriver import Firefox, FirefoxOptions
#from selenium.webdriver.common.by import By




df_bh = pd.read_csv('data/berkshire_porfolio.csv')


# DATAFRAME

st.header('Berkshire Hathaway Portfolio')
cant_empresas  = len(df_bh)

st.write(f'''
      Size: **{cant_empresas} companies**.
''')

st.dataframe(df_bh)

st.write(f'''
      Source: **[hedgefollow.com](https://hedgefollow.com/funds/Berkshire+Hathaway)**

''')

hide_st_style='''
            <style>
            header {visibility: hidden;}
            </style>
            '''
st.markdown(hide_st_style, unsafe_allow_html=True)



# MULTISELECCION DE EMPRESAS PARA ANALIZAR

selected_stocks = st.sidebar.multiselect(
    "Companies Selection to Analyze",
    df_bh['Stock'].unique(),
    default=df_bh['Stock'].unique()[:5])






# GRAFICO MULTI-INDICES (MEDIA MOVIL, RSI, CORRELACION MOVIL)

# Define los tickers que queremos visualizar
# tickers = ['AAPL', 'BAC', 'CVX', 'KO', 'AXP', 'KHC']


st.header('Technical Chart (Indicators) Selection')

# Crea un botón para cada ticker
ticker = st.radio('Choose an Option', selected_stocks)

# Descarga los datos del ticker utilizando yfinance
data = yf.download(ticker, start='2000-01-01')

# Calcula las medias móviles
sma50 = data['Close'].rolling(window=50).mean()
sma200 = data['Close'].rolling(window=200).mean()

# Calcula el índice RSI utilizando ta
data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()

# Calcula la volatilidad y la correlación móvil entre el rendimiento y la volatilidad
data['volatility'] = data['Close'].pct_change().rolling(window=252).std() * (252 ** 0.5)
data['corr252'] = data['Close'].pct_change().rolling(window=252).corr(data['volatility'])

# Crea el gráfico utilizando Plotly
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                    row_heights=[0.6, 0.2, 0.2])

# Agrega el gráfico de precios
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Precio de cierre'), row=1, col=1)

fig.add_trace(go.Scatter(x=data.index, y=sma50, name='SMA 50', line=dict(dash='dash', color='#008000', width=0.8)), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=sma200, name='SMA 200', line=dict(dash='dash', width=0.8)), row=1, col=1)

# Agrega el subgráfico de RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', yaxis='y2', line=dict(color='#000000', width=0.3)), row=2, col=1)

# Agrega el subgráfico de correlación móvil
fig.add_trace(go.Scatter(x=data.index, y=data['corr252'], name='Correlación móvil', line=dict(color='#000000', width=0.3)), row=3, col=1)

# Agrega una línea horizontal en y=70 y en y=30 para remarcar el valor para RSI
fig.add_shape(type="line", x0=data.index[0], x1=data.index[-1], y0=70, y1=70, line=dict(color="#000000", width=0.8), row=2, col=1)
fig.add_shape(type="line", x0=data.index[0], x1=data.index[-1], y0=30, y1=30, line=dict(color="#000000", width=0.8), row=2, col=1)


# Define el diseño del gráfico
fig.update_layout(title=ticker, height=800)

# Define el diseño de los ejes
fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
fig.update_xaxes(rangeslider_visible=False, row=2, col=1)
fig.update_xaxes(rangeslider_visible=False, row=3, col=1)
fig.update_yaxes(title_text='Precio de cierre', row=1, col=1)
fig.update_yaxes(title_text='RSI', row=2, col=1, side='left')
fig.update_yaxes(title_text='Correlac.móvil', row=3, col=1, side='left')

#fig.update_xaxes(
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
#)

# Obtener la fecha actual
today = dt.date.today()

# Definir la fecha de inicio como hace un año
start_date = today - dt.timedelta(days=365)

# Establecer el rango de fechas por defecto para el botón "1y"
fig.update_layout(xaxis=dict(
                     range=[start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')],
                     rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(count=5, label="5y", step="year", stepmode="backward"),
                            dict(count=10, label="10y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                     )
                 ))

st.plotly_chart(fig)




# Selección final de acciones para inversión

# st.write("Editable DataFrame", df.style.format({True: "✅", False: "❌"}), unsafe_allow_html=True)

# Tìtulo
st.markdown('<p style="font-size:32px;background-color:#d9d9d9;color:red;font-weight:bold;text-align:center">FINAL STOCKS SELECTION</p>', unsafe_allow_html=True)

# Dataframe editable
final_selection = {"Stock": selected_stocks, "Selected": [True]*len(selected_stocks)}
df_final_selection = pd.DataFrame(final_selection)

edited_df = st.experimental_data_editor(df_final_selection)




