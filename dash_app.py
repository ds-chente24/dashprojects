import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import date, timedelta

tickers = ['APPN','BYND', 'CHWY', 'CRWD', 'DOCU', 'FSLY', 'FVRR',
'GILD','GDRX', 'HAAC', 'MGNI', 'PI', 'PINS', 'RDFN', 'SE', 'SONO', 'SQ', 'STPK', 'TDOC', 
'TER', 'TTD', 'TWLO', 'U', 'VYGVF', 'VYM', 'ZM']

tday = date.today().strftime('%Y-%m-%d')
eday = (date.today()+timedelta(1)).strftime('%Y-%m-%d')
yrago = (date.today()-timedelta(730)).strftime('%Y-%m-%d')


#Load the dataset
adj_close_df = yf.download(tickers, start=yrago, end=eday)['Adj Close']
adj_close_df

#Melt Data
reset = adj_close_df.reset_index().rename(columns={adj_close_df.index.name:'Date'})
adj_close_df_melt = reset.melt(id_vars=['Date'], value_vars=tickers, var_name='Name')
adj_close_df_melt = reset.melt(id_vars='Date', var_name='Name', value_name='Adj_Close_Price')
adj_close_df_melt
adj_close_df_melt['MA200'] = adj_close_df_melt['Adj_Close_Price'].rolling(window=200).mean()
adj_close_df_melt['Percent from 200MA'] = (((adj_close_df_melt['Adj_Close_Price']-adj_close_df_melt['MA200'])/adj_close_df_melt['MA200']*100).round(2))
adj_close_df_melt['Excess'] = adj_close_df_melt['Percent from 200MA'] >= 70
adj_close_df_melt['Excess Line'] = ((adj_close_df_melt['MA200']*.70)+(adj_close_df_melt['MA200']))
df_excess = adj_close_df_melt.query('`Percent from 200MA`>=70')

#Create the Dash app
app = dash.Dash()
server = app.server

#Setup the app layout
app.layout = html.Div(children=[
    html.H1(children='Excess 200 Day Moving Average Dashboard'),
    dcc.Dropdown(id='ticker-dropdown',
                 options=[{'label': i, 'value': i}
                          for i in adj_close_df_melt['Name'].unique()],
                 value='APPN'),
    dcc.Graph(id='price-graph')
])

#Setup the callback function
@app.callback(
    Output(component_id='price-graph', component_property='figure'),
    [Input(component_id='ticker-dropdown', component_property='value')]
    )
def update_graph(selected_ticker):
    filtered_df = adj_close_df_melt[adj_close_df_melt['Name'] == selected_ticker]
    filtered_dft = filtered_df.tail(200)
    excessive_df = filtered_dft.query('`Percent from 200MA` >=70')
    fig_200MA = go.Figure()
    fig_200MA.add_scatter(x=excessive_df['Date'],
                      y=excessive_df['Adj_Close_Price'],
                      mode='markers',
                      name='Excessive',
                      marker_color='royalblue',
                      marker_symbol='circle-open')
    fig_200MA.add_scatter(x=filtered_dft['Date'],
                      y=filtered_dft['Adj_Close_Price'],
                      mode='lines',
                      name='Price',
                      line_color='royalblue')
    fig_200MA.add_scatter(x=filtered_dft['Date'],
                      y=filtered_dft['MA200'],
                      mode='lines',
                      name='200-day Moving Average',
                      line_color='green')
    fig_200MA.add_scatter(x=filtered_dft['Date'],
                         y=filtered_dft['Excess Line'],
                         mode='lines',
                         name='Excess Line',
                         line_color='firebrick')
    fig_200MA.update_layout(title= selected_ticker+' 200 Day Moving Average',
                        xaxis_title='Date',
                        yaxis_title='Price',
                        width= 800,
                        height= 350)
    return fig_200MA



