# Importando bibliotecas
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import yfinance as yf

import streamlit as st

import seaborn as sns

import warnings
warnings.filterwarnings("ignore")

# %matplotlib inline
# %config InlineBackend.figure_format='retina'




sp500_index = pd.read_csv('data/sp500_index.csv')



def plot_time_series(sp500_index):
    # Crear la figura

    fig = px.line(sp500_index, x="Date", y=["Close"], color_discrete_sequence=['#AEC6CF'])    

    # Personalizar el aspecto de la gráfica
    fig.update_layout(
    #    title={
    #        'text': 'S&P 500 Close Price since 2000-01-01',
    #        'x': 0.3,
    #        'y': 1,
    #        'font': dict(size=30)},
        xaxis_title="Date",
        yaxis_title="Price",
        plot_bgcolor="white",
    )
    # Cambiar el nombre de la variable en la leyenda
    #fig.update_traces(name='S&P500 Price')
    # Cambiar los nombres de la leyenda
    #fig.update_layout(
    #    legend=dict(
    #        title='<b>Leyenda:</b>',
    #        orientation='v',
    #        yanchor='bottom',
    #        y=0.01,
    #        xanchor='right',
    #        x=1,
    #        bgcolor='rgba(0,0,0,0)',
    #        font=dict(size=12)
    #    )
    #)
    # Customizacion de las ventanas temporales
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(step="all", label="all")
            ])
        )
    )

    # Agregar botón de reset
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                type='buttons',
                showactive=False,
                buttons=[{
                    'label': 'Reset',
                    'method': 'update',
                    'args': [{'x': [sp500_index['Date']], 'y': [sp500_index['Close']], 'type': 'scatter'}]
                }],
                xanchor='left',  # Ajustar la posición del botón reset
                x=0.9,
                y=1.15  # Ajustar la posición vertical del botón reset
            )
        ]
    )

    # Ocultar la leyenda de la variable
    fig.update_layout(showlegend=False)
    
    st.title('S&P 500 Close Price since 2000')

    # Mostrar la figura
    st.plotly_chart(fig, config=dict(displayModeBar=False), use_container_width=True)

# Llamar a la función con los datos deseados
plot_time_series(sp500_index)


# cargar datos en un dataframe
# df = pd.read_csv('sp500_index.csv')

# definir parámetros para la función get_candlestick_plot
ma1 = 50
ma2 = 200
ticker = 'S&P 500 Index'

# llamar a la función para generar el gráfico
def get_candlestick_plot(sp500_index, ma1, ma2, ticker):

    
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.1,
    #    subplot_titles = (f'{ticker} Stock Price', 'Volume Chart'),
        row_width = [0.3, 0.7]
    )
    
    fig.add_trace(
        go.Candlestick(
            x = sp500_index['Date'],
            open = sp500_index['Open'], 
            high = sp500_index['High'],
            low = sp500_index['Low'],
            close = sp500_index['Close'],
            name = 'Candlestick chart'
        ),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Line(x = sp500_index['Date'], y = sp500_index[f'{ma1}ma'], name = f'{ma1} SMA'),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Line(x = sp500_index['Date'], y = sp500_index[f'{ma2}ma'], name = f'{ma2} SMA'),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Bar(x = sp500_index['Date'], y = sp500_index['Volume'], name = 'Volume', marker_color='#AEC6CF'),
        row = 2,
        col = 1,
    )
    
    fig['layout']['xaxis2']['title'] = 'Date'
    fig['layout']['yaxis']['title'] = 'Price'
    fig['layout']['yaxis2']['title'] = 'Volume'

    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )

    
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(step="all", label="all")
            ])
        )
    )


    
    return fig

# crear la página Streamlit y agregar el gráfico generado
st.title('S&P 500 Index Candlestick Chart')


fig = get_candlestick_plot(sp500_index, ma1, ma2, ticker)

st.plotly_chart(fig, use_container_width=True)




st.image('images/Pyramid_2020_900_6625.jpg', width=650)


# GRAFICO RENDIMIENTOS ANUALES DESDE 2000

def plot_sp500_return():
    # Obtener los datos del índice S&P 500
    sp500_return = yf.Ticker("^GSPC").history(start='2000-01-01', end=None)
    # Borrando las columnas 'Dividends' and 'Stock Splits'
    sp500_return = sp500_return.drop(columns=['Dividends', 'Stock Splits'])
    # Calculando el rendimiento diario del precio de cierre y agregando la columna 'return'
    sp500_return['Return'] = sp500_return['Close'].pct_change()
    # Convirtiendo la columna 'date' como tipo 'datetime'
    sp500_return['Date'] = pd.to_datetime(sp500_return.index)

    # Calcular el retorno anual
    year_return = sp500_return.set_index('Date')['Close'].resample("Y").last().pct_change().to_frame().reset_index()
    year_return['Close'] = year_return['Close'] * 100
    # Crea columna de booleanos
    year_return['Up/Down'] = year_return['Close'] > 0
    year_return['Up/Down'] = year_return['Up/Down'].replace({True: 'Up', False: 'Down'})
    
    # Definir el color basado en la columna de booleanos
    fig = px.bar(year_return, x='Date', y='Close', color='Up/Down',
                 color_discrete_sequence=['rgb(200, 50, 30)', 'rgb(50, 200, 30)'], width=800)
    # establecer el título y los títulos de los ejes
    fig.update_layout(title='Annualized S&P 500 Close Price Return since 2000',
                      xaxis_title='Year',
                      yaxis_title='Return (%)',
                      template="seaborn" ,
                      bargap=0.05)
    fig.update_layout(xaxis_rangeslider_visible=False, height=500, plot_bgcolor='white')
    # Cambiar los nombres de la leyenda
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1))

    # Mostrar la gráfica en la página de Streamlit
    st.plotly_chart(fig)
    
# Llamar a la función para mostrar la gráfica en la página de Streamlit
plot_sp500_return()





