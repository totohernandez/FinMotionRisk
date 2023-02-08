from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc 
import plotly.express as px
import pandas as pd 
from datetime import datetime as dt
import pathlib

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df_FinMotionRisk = pd.read_csv(DATA_PATH.joinpath('FinMotionRisk.csv'))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], 
            meta_tags=[{'name':'viewport', 'content':'widt=device-width, initial-scale=1.0'}])
server = app.server

categoriesDict = {'Market Share':['Total Assets Market Share', 'Deposits Market Share', 'Loans Market Share'],
                'Asset Quality':['NPLs / Gross Loan Portfolio (GLP)','YoY GLP Growth', 'LLR/ NPLs', 'LLR/GLP', 'YoY Loan Growth'], 
                'Capitalization':['Regulatory CAR', 'CAR Headroom', 'Equity / Assets', 'OCER (NPLs - LLRs) / Equity', 'Internal Capital Generation'], 
                'Profitability':['ROAA', 'ROAE', 'Operating Profits / Average Assets'],
                'Funding Structure':['(Savings + Current) / Total Liabilities', 'Market Funds / Total Liabilities'], 
                'Liquidity':['(Cash and Deposits + Securities) / Total Assets', 'GLP / Deposits']}

names = list(categoriesDict.keys())
nestedOptions = categoriesDict[names[0]]


app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Finance in Motion Risk Analysis Dashboard",
                        className='text-center text-primary, m-5'), 
                        width=12)
            ),

    dbc.Row(
        dbc.Col([
            html.P("Countries",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='country-dpdn', multi=True, 
                        options=[{'label':x, 'value':x} for x in sorted(df_FinMotionRisk['Country'].unique())],
                        value=['El Salvador', 'Guatemala', 'Honduras'],
                        clearable=False
                                )
                ])
            ), 
    dbc.Row(    
        dbc.Col([
            html.P("Banks",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='bank-dpdn', 
                        options=[],
                        value=['Banco Agricola, S.A.', 'Banco Financiera Centroamericana, S.A.', 'INDUSTRIAL, S. A.'],
                        multi= True
                        )
                ]),
            ), 
    dbc.Row([
        dbc.Col([
            html.P("Categories",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='category-dpdn', multi=False, 
                        options=[{'label':name, 'value':name} for name in names],
                        value='Profitability'
                        )
                ]), 
        dbc.Col([
            html.P("Indicators",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='indicators-dpdn', options=[], value='ROAA')
                ]),
            ]), 

    dbc.Row(dcc.Graph(id='graph-id', figure={})), 

    dbc.Row(
        dbc.Col([
            html.P("Select Banks to Compare",
                        className='text-center text-primary, mb-4'),
            dcc.Checklist(id='bank-cklst', 
                        options=[],
                        value=['Banco Agrícola, S.A.', 'Banco de América Central, S.A.']
                        ),
        ])
    ), 

    dbc.Row([
        dbc.Col([
            html.P("Graph Type",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='graphs-dpdn', 
                        options=['Bar Plot', 'Line Plot'],
                        value= 'Bar Plot',
                        clearable=False)
                ]),
        dbc.Col([
            html.P("Date Range", 
                        className='text-center text-primary, mb-4'), 
            dcc.Dropdown(id='date-rng', 
                        options=[{'label':x, 'value':x} for x in sorted(df_FinMotionRisk['Period'].unique())], 
                        multi=True, 
                        value=['2022-Q3', '2021-Q4', '2020-Q4'],
                        clearable=False)
                ])
            ])
])


# Filter Banks by Countries 1st Filter Dropdown
@app.callback(
    Output('bank-dpdn', 'options'),
    Input('country-dpdn', 'value')
)
def set_bank_options(Country):
    dff = df_FinMotionRisk[df_FinMotionRisk['Country'].isin(Country) ]
    return [{'label': b, 'value': b} for b in sorted(dff.Bank.unique())]

# Filter Indicators by Category
@app.callback(
    Output('indicators-dpdn', 'options'),
    [Input('category-dpdn', 'value')])
def set_indicators_options(category):
    return [{'label': i, 'value': i} for i in categoriesDict[category]]

@app.callback(
    Output('indicators-dpdn', 'value'),
    [Input('indicators-dpdn', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

#Graph Indicator Filtered by Banks Selected and Date Range 
@app.callback(
    Output('graph-id', component_property='figure'),
    [Input('bank-dpdn', 'value'),
    Input('indicators-dpdn', 'value'),
    Input('graphs-dpdn', 'value'),
    Input('date-rng', 'value')]
)

def update_graph(Banks, Indicator, Chart, Period):
    dff = df_FinMotionRisk[df_FinMotionRisk['Bank'].isin(Banks) & df_FinMotionRisk['Period'].isin(Period)]

    if Chart == 'Bar Plot':
        fig = px.bar(data_frame=dff, x='Period', y=dff[Indicator], color='Bank', orientation='v', barmode='group')
        fig.update_layout(yaxis_tickformat = '.2%')
    elif Chart == 'Line Plot':
        fig = px.line(data_frame=dff, x='Period', y=dff[Indicator], color='Bank')
        fig.update_layout(yaxis_tickformat = '.2%')
    return fig

if __name__=='__main__':
    app.run_server(debug=True, port=8000)
