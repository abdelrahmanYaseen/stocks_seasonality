# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import flask

#Data prep
import pandas as pd
import plotly.graph_objects as go
import yfinance


# pip3.6 install --user yfinance
TICKER_TEXT = 'NCLH'
CLICKS = -1
FIG = None
DF = None

def getMonths(start, end):
    jans = pd.date_range(start, end, freq='AS-JAN').tolist()
    febs = pd.date_range(start, end, freq='AS-FEB').tolist()
    mars = pd.date_range(start, end, freq='AS-MAR').tolist()
    aprs = pd.date_range(start, end, freq='AS-APR').tolist()
    mays = pd.date_range(start, end, freq='AS-MAY').tolist()
    juns = pd.date_range(start, end, freq='AS-JUN').tolist()
    juls = pd.date_range(start, end, freq='AS-JUL').tolist()
    augs = pd.date_range(start, end, freq='AS-AUG').tolist()
    seps = pd.date_range(start, end, freq='AS-SEP').tolist()
    octs = pd.date_range(start, end, freq='AS-OCT').tolist()
    novs = pd.date_range(start, end, freq='AS-NOV').tolist()
    decs = pd.date_range(start, end, freq='AS-DEC').tolist()
    
    months = [jans, febs, mars, aprs, mays, juns, juls, augs, seps, octs, novs, decs]
    return months

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    
    html.Div(children=[dcc.Input(id="ticker", type="text", placeholder="ticker"),
                       html.Button('Go', id="btn")
                       
                       ],
             style={'width':'75%', 'margin':25, 'textAlign': 'center'}
             ),
    html.Div([dcc.Graph(id="bar-graph")]),
    dcc.RangeSlider(id = 'my-slider', step=1, allowCross=False, included=True, min=0)   ,
    html.H1(id='message', children='Hello Dash')
])


        
@app.callback(
    [dash.dependencies.Output('my-slider', 'max'),
    dash.dependencies.Output('my-slider', 'marks'), 
    dash.dependencies.Output('my-slider', 'value'), 
    dash.dependencies.Output('message', 'children'),
    dash.dependencies.Output('bar-graph', 'figure')
    ],
    [dash.dependencies.Input('my-slider', 'max'),
    dash.dependencies.Input('my-slider', 'marks'), 
    dash.dependencies.Input('message', 'children'),
    dash.dependencies.Input('bar-graph', 'figure'),
    
    dash.dependencies.Input('btn', 'n_clicks'),
     dash.dependencies.Input('my-slider', 'value')],
    [dash.dependencies.State('ticker', 'value')])
def update_everything(Max,Marks,Children,Figure,n_clicks,slider_value, ticker_value):
    
    global TICKER_TEXT
    global CLICKS
    global DF
    print(type(ticker_value))
    
    if not isinstance(ticker_value, str):
        ticker_value = TICKER_TEXT
    else:
        TICKER_TEXT = ticker_value
        
    print("update_veryhing")
    if not isinstance(n_clicks,int):
        n_clicks = 0
        
        
    if n_clicks > CLICKS:
        print("CLICK - n_clicks=", n_clicks)
        CLICKS = n_clicks
        msg = ""
        if ticker_value == None:
            TICKER_TEXT = "NCLH"
            
        ticker = yfinance.Ticker(TICKER_TEXT)
        df = ticker.history(period="100y",interval="1mo")
        
        if len(df) == 0:
            msg+=f" Couldn't find data for {TICKER_TEXT} "
            
            TICKER_TEXT = "NCLH"
            ticker = yfinance.Ticker(TICKER_TEXT)
            df = ticker.history(period="100y",interval="1mo")
            
        
        print(df.index[0],'*************', df.index[-1])
        markers = {
                0: {'label': str(df.index[0].date()), 'style': {'color': '#77b0b1'}},
                len(df)-1: {'label': str(df.index[-1].date()), 'style': {'color': '#f50'}}
            }
        msg+= f"- Showing data for {TICKER_TEXT}"
        DF = df
        slider_value=[0,len(df)-1]
        return [len(df)-1, 
                markers,
                slider_value,
                msg, 
                update_figure(slider_value,TICKER_TEXT)]
    else:
        print("SLIDER")
        return Max,Marks, slider_value, Children, update_figure(slider_value,TICKER_TEXT)
    
        


def update_figure(value_range, ticker_text):
    global DF
    print("updating figure")
    df = DF
    tot_profits=[]
    avg_profits=[]
    props=[]
    start = df.index[0]
    end = df.index[-1]
    if not value_range == None:
        start = df.index[value_range[0]]
        end = df.index[value_range[1]]
    months = getMonths(start, end)

    for month in months:
        month = [x for x in month if x in df.index]
        month_df = df.loc[month]
        tot_profit = 0
        profit_freq = 0
        loss_freq = 0
        i=-1
        for i in range(len(month_df)):
            op = month_df.iloc[i]['Open']
            cl = month_df.iloc[i]['Close']
            profit = (cl-op)/cl
    
            tot_profit+=profit
            if profit > 0:
                profit_freq+=1
            else:
                loss_freq+=1
        if i == -1:
            print("Couldn't find values in this month")
        tot_profits+=[tot_profit]
        avg_profits+=[tot_profit/len(month_df)]
        props+=[profit_freq/(profit_freq+loss_freq)]


        
    fig = go.Figure()
    colors = [f'rgb({int(255-x*255)},{int(x*255)},200)' for x in props]
    fig.add_trace(go.Bar(
        name = "Probabilities",
        x=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'],
        y=props,
        text=[str(round(x*100,1))+'%' for x in props],
        textposition='auto',
        marker_color=colors
    
    ))
    colors = [f'rgb({0},{int(255)},100)' if x >0 else f'rgb({int(255+x*255)},{0},100)' for x in avg_profits]
    
    fig.add_trace(go.Bar(
        name = "Average Profits",
        x=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'],
        y=[x for x in avg_profits],
        text=[str(round(x*100,1))+'%' for x in avg_profits],
        textposition='auto',
        marker_color=colors
    ))

    fig.update_layout(title=f"{ticker_text} | {start.date()}  -  {end.date()}",
                      yaxis=dict(tickformat=".2%", showgrid=False),
                      xaxis=dict(showgrid=False),
                      height=700,
                      )
    
    return fig






if __name__ == '__main__':
    server = flask.Flask(__name__)
    app = dash.Dash(external_stylesheets=external_stylesheets, server=server)