
import os
import pandas as pd

from dash import Dash, Input, Output, dcc, html
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

external_stylesheets = [
    {
        'href': (
            'https://fonts.googleapis.com/css2?'
            'family=Lato:wght@400;700&display=swap'
        ),
        'rel': 'stylesheet',
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'The Price is Right'

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children='🃏♟️🎲🧩', className='header-emoji'),
                html.H1(
                    children='The Price is Right: Board Game Edition', className='header-title'
                ),
                html.P(
                    children=(
                        'Track the prices of board games across online vendors to find the best deals at any given time'
                    ),
                    className='header-description',
                ),
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

    max_date_allowed = master_df['date'].max().date()
    end_date = master_df['date'].max().date()
    print(master_df['date'].max().date())
    return (max_date_allowed, end_date)


if __name__ == '__main__':
    app.run_server(debug=True)
