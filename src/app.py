import pathlib 
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc 
import plotly.express as px
import pandas as pd 
from datetime import datetime as dt

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df_Paraguay = pd.read_csv(DATA_PATH.joinpath('Paraguay RT.csv'))
df_Paraguay = df_Paraguay.fillna(0)
df_Paraguay['Month'] = pd.DatetimeIndex(df_Paraguay['Date']).month
df_Paraguay['Year'] = pd.DatetimeIndex(df_Paraguay['Date']).year 
df_Paraguay['Quarter'] = 0
df_Paraguay['Quarter'].mask(df_Paraguay['Month'] == 12,df_Paraguay['Year'].astype(str), inplace=True)
df_Paraguay['Quarter'].mask(df_Paraguay['Month'] == 9,df_Paraguay['Year'].astype(str) + '-' + 'Q3', inplace=True) 
df_Paraguay['Quarter'].mask(df_Paraguay['Month'] == 6,df_Paraguay['Year'].astype(str) + '-' + 'Q2', inplace=True)
df_Paraguay['Quarter'].mask(df_Paraguay['Month'] == 3,df_Paraguay['Year'].astype(str) + '-' + 'Q1', inplace=True) 

df_FinMotion = pd.read_csv(DATA_PATH.joinpath('FinMotionParaguay.csv'))
df_FinMotion.drop(columns=df_FinMotion.columns[0], axis=1, inplace=True)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], 
            meta_tags=[{'name':'viewport', 'content':'widt=device-width, initial-scale=1.0'}], 
            prevent_initial_callbacks=True)
server = app.server 

categoriesDict = {'Capital Adecuado':['Activos y Contingentes Ponderados (AYCP)','Capital Nivel 1 (C1)', 'Capital Nivel 1 + 2 (C1+2)', 'C1 / AYCP', 'C1+2 / AYCP', 'Patrimonio Neto/Activos y Contingentes Totales', 'Activos y Contingentes/Patrimonio (veces)'], 
                'Calidad del Activo':['Préstamos Vencidos/Patrimonio Neto', 'Préstamos Vigentes/Préstamos Totales', 'Previsiones/Préstamos Vencidos', 'Previsiones/Préstamos Vigentes', 'Cartera Vencida/Cartera Total - Morosidad', 'Cartera Vencida/Cartera Total Neta de Previsiones', 'Renovados/Cartera', 'Refinanciados/Cartera', 'Reestructurados/Cartera', 'RRR+Medidas transitorias/Cartera', 'Vencidos+RRR+Medidas transitorias/Cartera', 'RRR/Cartera'], 
                'Depositos - Participacion por tipo de Instrumento':['Cuenta Corriente', 'A la Vista', 'Plazo Fijo', 'CDA', 'Títulos de Inversión', 'Intereses Devengados'],
                'Depositos - Participacion por Moneda':['Local', 'Extranjera'], 
                'Rentabilidad':['Utilidad antes de Impuesto/Activo (Anual)', 'Utilidad antes de Impuesto/Patrimonio (Anual)'], 
                'Liquidez':['Disponible + Inversiones Temporales/Depósitos', 'Disponible + Inversiones Temporales/Pasivo', 'Activo/Pasivo', 'Activo/Pasivo + Contingencias'], 
                'Consideraciones Administrativas':['Gastos Personales/Gastos Administrativos', 'Gastos Personales/Margen Operativo', 'Gastos Administrativos/Margen Operativo', 'Gastos Personales/Depósitos (Anual)', 'Gastos Administrativos/Depósitos (Anual)']}

names = list(categoriesDict.keys())
nestedOptions = categoriesDict[names[0]]

FinCategoriesDict = {'Asset Quality':['NPLs / Gross Loan Portfolio (GLP)','YoY GLP Growth', 'LLR/ NPLs', 'LLR/GLP', 'YoY Loan Growth'], 
                'Capitalization':['Regulatory CAR', 'CAR Headroom', 'Equity / Assets', 'OCER (NPLs - LLRs) / Equity', 'Internal Capital Generation'], 
                'Profitability':['ROAA', 'ROAE', 'Operating Profits / Average Assets'],
                'Funding Structure':['(Savings + Current) / Total Liabilities', 'Market Funds / Total Liabilities'], 
                'Liquidity':['(Cash and Deposits + Securities) / Total Assets', 'GLP / Deposits'], 
                'Market Share':['Total Assets Market Share', 'Deposits Market Share', 'GLP Market Share']}

FinNames = list(FinCategoriesDict.keys())
FinNestedOptions = FinCategoriesDict[FinNames[0]]



app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Ratios Sistema Financiero Paraguay",
                        className='text-center text-primary, m-5'), 
                        width=12)
            ),

    dbc.Row(
        dbc.Col([
            html.P("Bank",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='bank-dpdn', multi=True, 
                        options=[{'label':x, 'value':x} for x in sorted(df_Paraguay['Bank'].unique())],
                        value=['Banco Itaú Paraguay S.A.' ,'Banking System Paraguay'], 
                        clearable=False
                                )
                ]), 
            ), 
    dbc.Row([
        dbc.Col([
            html.P("Categories",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='category-dpdn', multi=False, 
                        options=[{'label':name, 'value':name} for name in names]
                        )
                ]), 
        dbc.Col([
            html.P("Indicators",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='indicators-dpdn', options=[])
                ]),
            ]), 

    dbc.Row(dcc.Graph(id='graph-id', figure={})), 
 
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
                        options=[{'label':x, 'value':x} for x in sorted(df_Paraguay['Quarter'].unique())], 
                        multi=True, 
                        value=['2022-Q1', '2022-Q2', '2022-Q3'],
                        clearable=False)
                ])
            ]),
    dbc.Row(
        dbc.Col(html.H1("Finance in Motion Indicators Paraguay Banks",
                        className='text-center text-primary, m-5'), 
                        width=12)
            ),

    dbc.Row(
        dbc.Col([
            html.P("Bank",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='fin-bank-dpdn', multi=True, 
                        options=[{'label':x, 'value':x} for x in sorted(df_FinMotion['Bank'].unique())],
                        value=['Banco Itaú Paraguay S.A.' ,'Banking System Paraguay'], 
                        clearable=False
                                )
                ]), 
            ), 
    dbc.Row([
        dbc.Col([
            html.P("Categories",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='fin-category-dpdn', multi=False, 
                        options=[{'label':name, 'value':name} for name in FinNames]
                        )
                ]), 
        dbc.Col([
            html.P("Indicators",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='fin-indicators-dpdn', options=[])
                ]),
            ]), 

    dbc.Row(dcc.Graph(id='fin-graph-id', figure={})), 
 
    dbc.Row([
        dbc.Col([
            html.P("Graph Type",
                        className='text-center text-primary, mb-4'),
            dcc.Dropdown(id='fin-graphs-dpdn', 
                        options=['Bar Plot', 'Line Plot'],
                        value= 'Bar Plot',
                        clearable=False)
                ]),
        dbc.Col([
            html.P("Date Range", 
                        className='text-center text-primary, mb-4'), 
            dcc.Dropdown(id='fin-date-rng', 
                        options=[{'label':x, 'value':x} for x in sorted(df_FinMotion['Quarter'].unique())], 
                        multi=True, 
                        value=['2022-Q1', '2022-Q2', '2022-Q3'],
                        clearable=False)
                ])
            ])
])


# Filter Indicators by Category
@app.callback(
    Output('indicators-dpdn', 'options'),
    [Input('category-dpdn', 'value')])
def set_indicators_options(category):
    return [{'label': i, 'value': i} for i in categoriesDict[category]]

@app.callback(
    Output('indicators-dpdn', 'value'),
    [Input('indicators-dpdn', 'options')])
def set_indicator_value(available_options):
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
    dff = df_Paraguay[df_Paraguay['Bank'].isin(Banks) & df_Paraguay['Quarter'].isin(Period)]

    if Chart == 'Bar Plot':
        fig = px.bar(data_frame=dff, x='Quarter', y=dff[Indicator], color='Bank', orientation='v', barmode='group', labels={'Quarter':'Period'})
    elif Chart == 'Line Plot':
        fig = px.line(data_frame=dff, x='Quarter', y=dff[Indicator], color='Bank', labels={'Quarter':'Period'})
    return fig

# Finance in Motion Indicators
@app.callback(
    Output('fin-indicators-dpdn', 'options'),
    [Input('fin-category-dpdn', 'value')])
def set_fin_indicators_options(category):
    return [{'label': i, 'value': i} for i in FinCategoriesDict[category]]

@app.callback(
    Output('fin-indicators-dpdn', 'value'),
    [Input('fin-indicators-dpdn', 'options')])
def set_fin_indicator_value(available_options):
    return available_options[0]['value']

#Graph Indicator Filtered by Banks Selected and Date Range 
@app.callback(
    Output('fin-graph-id', component_property='figure'),
    [Input('fin-bank-dpdn', 'value'),
    Input('fin-indicators-dpdn', 'value'),
    Input('fin-graphs-dpdn', 'value'),
    Input('fin-date-rng', 'value')]
)

def update_graph(Banks, Indicator, Chart, Period):
    dff = df_FinMotion[df_FinMotion['Bank'].isin(Banks) & df_FinMotion['Quarter'].isin(Period)]

    if Chart == 'Bar Plot':
        fig = px.bar(data_frame=dff, x='Quarter', y=dff[Indicator], color='Bank', orientation='v', barmode='group', labels={'Quarter':'Period'})
        fig.update_layout(yaxis_tickformat = '.2%')
    elif Chart == 'Line Plot':
        fig = px.line(data_frame=dff, x='Quarter', y=dff[Indicator], color='Bank', labels={'Quarter':'Period'})
        fig.update_layout(yaxis_tickformat = '.2%')
    return fig
    
if __name__=='__main__':
    app.run_server(debug=True, port=8000)