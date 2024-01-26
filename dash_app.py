
import os
import pandas as pd

from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go


root_path = r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data'

master_df = pd.DataFrame()
for year in os.listdir(root_path):
    for month in os.listdir(root_path + '\\' + year):
        xl = pd.ExcelFile(os.path.join(root_path, year, month))
        dates = xl.sheet_names
        for day in dates:
            file = xl.parse(day)
            file['date'] = pd.to_datetime(day, format='%Y-%m-%d')
            master_df = pd.concat([master_df, file])

column_order = ['date', 'name', 'JogoNaMesa', 'Gameplay', 'JogarTabuleiro']
master_df = master_df[column_order].sort_values(by='date')

games = master_df['name'].sort_values().unique()
colors = {'JogoNaMesa': 'red', 'Gameplay': 'blue', 'JogarTabuleiro': 'green'}
stores = list(colors.keys())
sites = {'JogoNaMesa': 'https://jogonamesa.pt/P/home.cgi',
         'Gameplay': 'https://gameplay.pt/pt/',
         'JogarTabuleiro': 'https://jogartabuleiro.pt/'
         }

external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'The Price is Right'

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children='🃏♟️🎲🧩', className='header-emoji'),
                html.H1(children='The Price is Right: Board Game Edition', className='header-title'),
                html.P(children=('Track the prices of board games across online vendors to find the best deals at any given time'),
                       className='header-description')
                    ],
            className='header',
                ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Game', className='menu-title'),
                        dcc.Dropdown(
                            id='game-filter',
                            options=[
                                {'label': game, 'value': game}
                                for game in games
                            ],
                            value='Last Will',
                            clearable=False,
                            searchable=True,
                            className='dropdown',
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children='Store', className='menu-title'),
                        dcc.Checklist(
                            id='store-filter',
                            options=[
                                {'label': store, 'value': store}
                                for store in stores
                            ],
                            value=stores,
                            className='checklist',
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children='Date Range', className='menu-title'
                        ),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=master_df['date'].min().date(),
                            max_date_allowed=master_df['date'].max().date(),
                            start_date=master_df['date'].min().date(),
                            end_date=master_df['date'].max().date(),
                            display_format ='DD/MM/YYYY'
                        ),
                    ]
                ),
            ],
            className='menu',
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5('Lowest Price', className='card-title'),
                                    html.P(str('Some placeholder text.'))
                                ], id='card-low'
                            )
                        ), width=6, ),
                dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5('Highest Price', className='card-title'),
                                    html.P(
                                        'This card also has some text content and not much else, but '
                                        'it is twice as wide as the first card.'
                                    )
                                ], id='card-high'
                            )
                        ), width=6, ),
            ], className='wrapper'
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='price-chart',
                        config={'displayModeBar': False},
                    ),
                    className='card',
                ),
            ],
            className='wrapper',
        ),
    ]
)


@app.callback(
    Output(component_id='price-chart', component_property='figure'),
    Input(component_id='game-filter', component_property='value'),
    Input(component_id='store-filter', component_property='value'),
    Input(component_id='date-range', component_property='start_date'),
    Input(component_id='date-range', component_property='end_date')
)
def update_charts(game, stores, start_date, end_date):
    filtered_data = master_df.query(
        'name == @game'
        ' and date >= @start_date and date <= @end_date'
    )

    fig = make_subplots(rows=1,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.009,
                        horizontal_spacing=0.009
                        )
    
    fig.update_layout(margin={'l': 30, 'r': 10, 'b': 50, 't': 30},
                      yaxis={'title': 'Price', 'titlefont': {'size': 18}, 'ticksuffix': '€', 'tickformat': '.2f'},
                      xaxis={'title': 'Date', 'titlefont': {'size': 18}},
                      legend={'title': 'Store', 'font': {'size': 14}},
                      title={'text': 'Price over Time', 'font': {'size': 24}, 'yref': 'paper', 'automargin': True, 'y': 0.9, 'x': 0.5, 'xanchor': 'center'}
                      )
    
    for store in stores:
        fig.append_trace({'x': filtered_data['date'],
                          'y': filtered_data[store],
                          'type': 'scatter',
                          'name': store,
                          'line': {'color': colors[store]},
                          'hovertemplate': '%{y:.2f}€'#<extra></extra>'
                          },
                        1,
                        1,
                        )

    return fig

@app.callback(
    Output(component_id='date-range', component_property='max_date_allowed'),
    Output(component_id='date-range', component_property='end_date'),
    Input(component_id='game-filter', component_property='value')
)
def update_date_picker_range(game):
    
    filtered_data = master_df.query('name == @game')

    max_date_allowed = filtered_data['date'].max().date()
    end_date = filtered_data['date'].max().date()

    return (max_date_allowed, end_date)


@app.callback(
    Output(component_id='card-low', component_property='children'),
    Output(component_id='card-high', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_date_picker_range(game):

    filtered_data = master_df.query('name == @game')

    min_values = [filtered_data[store].min() for store in stores]
    min_idx = min_values.index(min(min_values))
    min_store = stores[min_idx]
    min_site = sites[min_store]

    max_values = [filtered_data[store].max() for store in stores]
    max_idx = max_values.index(max(max_values))
    max_store = stores[max_idx]
    max_site = sites[max_store]

    low_card = dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5('Lowest Price', className='bi bi-caret-down-fill text-success'),
                                    html.H3(str(min(min_values))),
                                    dbc.Button('@ ' + min_store, color='success', outline=True, href=min_site),
                                ]
                            )
                        ), width='auto', id='card-low', className='text-center')

    high_card = dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5('Highest Price', className='bi bi-caret-up-fill text-danger'),
                                    html.H3(str(max(max_values))),
                                    dbc.Button('@ ' + max_store, color='danger', outline=True, href=max_site),
                                ]
                            )
                        ), width='auto', id='card-high', className='text-center')

    return (low_card, high_card)


if __name__ == '__main__':
    app.run_server(debug=True)
