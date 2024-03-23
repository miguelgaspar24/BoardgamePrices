
import math
import os

from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from plotly.subplots import make_subplots

import bgg_spyder
from PIL import Image
import requests
from io import BytesIO


root_path = r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data'

master_df = pd.DataFrame()
for year in os.listdir(root_path):
    if year.endswith('.xlsx'):
        continue
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
stores_prop = {'JogoNaMesa': {'color': 'red',
                              'url': 'https://jogonamesa.pt/P/home.cgi',
                              'favicon': 'https://jogonamesa.pt/img/favicon.ico'},
               'Gameplay': {'color': 'blue',
                            'url': 'https://gameplay.pt/pt/',
                            'favicon': 'http://www.gameplay.pt/img/favicon.ico?1678899580'},
               'JogarTabuleiro': {'color': 'green',
                                  'url': 'https://jogartabuleiro.pt/',
                                  'favicon': 'https://jogartabuleiro.pt/wp-content/uploads/2018/06/logo_favicon_M9H_icon.ico'}
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
            className='header'
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Game', className='menu-title'),
                        dcc.Dropdown(
                            options=[
                                    {'label': game, 'value': game}
                                    for game in games
                                    ],
                            id='game-filter',
                            clearable=False,
                            searchable=True,
                            className='dropdown',
                            placeholder='Select a game',
                            optionHeight=50
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children='Store', className='menu-title'),
                        dcc.Checklist(
                            options=[
                                    {'label': ' ' + store, 'value': store}
                                    for store in list(stores_prop.keys())
                                    ],
                            value=list(stores_prop.keys()),
                            id='store-filter',
                            className='checklist'
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children='Date Range', className='menu-title'),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=master_df['date'].min().date(),
                            max_date_allowed=master_df['date'].max().date(),
                            start_date=master_df['date'].min().date(),
                            end_date=master_df['date'].max().date(),
                            display_format ='DD/MM/YYYY'
                        )
                    ]
                )
            ],
            className='menu'
        ),
        dbc.Row(
            [
             dbc.Col(dbc.CardBody(
                        [html.Img(
                            id='game-cover-image',
                            className='image',
                            alt='Game Cover',
                            src=''
                                )
                            ]
                        )
                    ),
            dbc.Col(dbc.CardBody(
                    [html.H6('Average Rating'),
                    html.H5('No Data'),
                    html.Br(),
                    html.H6('Game Complexity'),
                    html.H5('No Data')
                    ],
                    id='average-rating-complexity',
                    className='text-center'
                )
            ),
           dbc.Col(dbc.CardBody(
                    [html.H6('Player Count'),
                    html.H5('No Data'),
                    html.Br(),
                    html.H6('Play Time'),
                    html.H5('No Data'),
                    ],
                    id='player-count-playtime',
                    className='text-center'
                )
            ),
            dbc.Col(dbc.CardBody(
                                [html.H6('Year Published'),
                                html.H5('No Data'),
                                html.Br(),
                                html.H6('Language Dependence'),
                                html.H5('No Data')
                                ],
                                id='date-language',
                                className='text-center'
                            ),
                    ),
                ], className='wrapper'
            ),
        dbc.Row(
            [
            dbc.Col(dbc.CardBody(
                [html.H6('Creators'),
                html.H5('No Data')
                ],
                id='creators',
                className='text-center'
            )
        ),
            dbc.Col(dbc.CardBody(
                                [html.H6('Types'),
                                html.H5('No Data')],
                                id='types',
                                className='text-center'
                            )
                        ),
             dbc.Col(dbc.CardBody(
                                [html.H6('Categories'),
                                html.H5('No Data')],
                                id='categories',
                                className='text-center'
                            )
                        ),
            dbc.Col(dbc.CardBody(
                                [html.H6('Mechanics'),
                                html.H5('No Data')],
                                id='mechanics',
                                className='text-center'
                            )
                        )
                    ], className='wrapper'
                ),
        dbc.Row(
            [
             dbc.Col(dbc.Card(dbc.CardBody(
                                [html.H5(' Lowest Price', className='bi bi-caret-down-fill text-success'),
                                html.H3('No Data')],
                                id='card-lowest',
                                className='text-center'
                            )
                        )
                ),
            dbc.Col(dbc.Card(dbc.CardBody(
                                [html.H5(' Highest Price', className='bi bi-caret-up-fill text-danger'),
                                html.H3('No Data')],
                                id='card-highest',
                                className='text-center'
                            )
                        )
                )
            ],
            className='wrapper'
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                                id='price-chart',
                                config={'displayModeBar': False},
                                ),
                                className='card-graph'
                    )
                ],
                className='wrapper'
            )
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
    
    fig.update_layout(margin={'l': 30, 'r': 30, 'b': 50, 't': 30},
                      yaxis={'title': 'Price', 'titlefont': {'size': 18}, 'ticksuffix': '€', 'tickformat': '.2f'},
                      xaxis={'title': 'Date', 'titlefont': {'size': 18}},
                      legend={'title': 'Store', 'font': {'size': 14}},
                      title={'text': 'Price over Time', 'font': {'size': 24}, 'yref': 'paper', 'automargin': True, 'y': 0.9, 'x': 0.5, 'xanchor': 'center'}
                      )
    
    for store in list(stores_prop.keys()):
        fig.append_trace({'x': filtered_data['date'],
                          'y': filtered_data[store],
                          'type': 'scatter',
                          'name': store,
                          'line': {'color': stores_prop[store]['color']},
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
    Output(component_id='card-lowest', component_property='children'),
    Output(component_id='card-highest', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_min_max_cards(game):

    filtered_data = master_df.query('name == @game')

    min_values = [filtered_data[store].min() for store in list(stores_prop.keys())]
    min_idx = min_values.index(min(min_values))
    min_store = list(stores_prop.keys())[min_idx]
    min_site = stores_prop[min_store]['url']
    min_card_value = 'No Data' if math.isnan(min(min_values)) else '{:.2f}'.format(min(min_values)) + '€'

    max_values = [filtered_data[store].max() for store in list(stores_prop.keys())]
    max_idx = max_values.index(max(max_values))
    max_store = list(stores_prop.keys())[max_idx]
    max_site = stores_prop[max_store]['url']
    max_card_value = 'No Data' if math.isnan(max(max_values)) else '{:.2f}'.format(max(max_values)) + '€'

    low_card = html.Div(
                    [html.H5(' Lowest Price', className='bi bi-caret-down-fill text-success'),
                     html.H3(min_card_value),
                     dbc.Button(children=[html.Img(src=stores_prop[min_store]['favicon']), ' ' + min_store],
                                outline=False,
                                href=min_site,
                                className='card-button'
                                )],
                    id='card-lowest',
                    className='text-center'
                )
                
    high_card = html.Div(
                    [html.H5(' Highest Price', className='bi bi-caret-up-fill text-danger'),
                     html.H3(max_card_value),
                     dbc.Button(children=[html.Img(src=stores_prop[max_store]['favicon']), ' ' + max_store],
                                outline=False,
                                href=max_site,
                                className='card-button'
                                )],
                    id='card-highest',
                    className='text-center'
                )
                    
    return (low_card, high_card)


@app.callback(
    Output(component_id='game-cover-image', component_property='src'),
    Input(component_id='game-filter', component_property='value')
)
def update_game_image(game):

    if game is None:
        return ''

    #root_path = r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data'
    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    image_url = game_props['game_image']

    image_content = requests.get(image_url)
    image_display = Image.open(BytesIO(image_content.content))

    image_source = image_display

    return image_source


@app.callback(
    Output(component_id='average-rating-complexity', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_game_rating(game):

    if game is None:
        return [html.H6('Average Rating'),
                html.H5('No Data'),
                html.Br(),
                html.H6('Game Complexity'),
                html.H5('No Data')]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_rating = game_props['average_rating']
    game_votes = game_props['n_rating_votes']
    game_complexity = game_props['complexity']

    rating_complexity = html.Div(
                            [html.H6('Average Rating'),
                            html.H5(round(float(game_rating), 1)),
                            html.H6(game_votes + ' votes'),
                            html.Br(),
                            html.H6('Complexity'),
                            html.H5(str(round(float(game_complexity), 1)) + ' / 5'),
                            ],
                            id='average-rating-complexity',
                            className='text-center'
                        )

    return rating_complexity


@app.callback(
    Output(component_id='player-count-playtime', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_player_count(game):

    if game is None:
        return [html.H6('Player Count'),
                html.H5('No Data'),
                html.Br(),
                html.H6('Play Time'),
                html.H5('No Data'),
                ]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_min_count = game_props['min_players']
    game_max_count = game_props['max_players']
    game_min_time = game_props['min_playtime']
    game_max_time = game_props['max_playtime']

    player_count = html.Div(
                        [html.H6('Player Count'),
                        html.H5(game_min_count + ' - ' + game_max_count),
                        html.Br(),
                        html.H6('Play Time'),
                        html.H5(game_min_time + ' - ' + game_max_time + ' mins.')
                        ],
                        id='player-count-playtime',
                        className='text-center'
                    )

    return player_count


@app.callback(
    Output(component_id='date-language', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_date_language(game):

    if game is None:
        return [html.H6('Year Published'),
                html.H5('No Data'),
                html.Br(),
                html.H6('Language Dependence'),
                html.H5('No Data')
                ]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_year = game_props['year_published']
    game_language = game_props['language_dependence']

    year_published = html.Div(
                    [html.H6('Year Published'),
                     html.H5(game_year),
                     html.Br(),
                     html.H6('Language Dependence'),
                     html.P(game_language)
                    ],
                    id='date-language',
                    className='text-center'
                )

    return year_published


@app.callback(
    Output(component_id='creators', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_creators(game):

    if game is None:
        return [html.H6('Creators'),
                html.H5('No Data')]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_designer = game_props['designer']
    game_artist = game_props['artist']
    game_publisher = game_props['publisher']

    creators = html.Div(
                    [html.H5('Designer'),
                     html.H6(game_designer),
                     html.Br(),
                     html.H5('Artist'),
                     html.H6(game_artist),
                     html.Br(),
                     html.H5('Publisher'),
                     html.H6(game_publisher)
                    ],
                    id='creators',
                    className='text-center'
                ),

    return creators


@app.callback(
    Output(component_id='types', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_types(game):

    if game is None:
        return [html.H6('Types'),
                html.H5('No Data')]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_types = game_props['types']

    types = html.Div(
                    [html.H5('Types'),
                     html.H6([html.P(typ) for typ in game_types])
                    ],
                    id='types',
                    className='text-center'
                ),

    return types


@app.callback(
    Output(component_id='categories', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_categories(game):

    if game is None:
        return [html.H6('Categories'),
                html.H5('No Data')]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_categories = game_props['categories']

    categories = html.Div(
                    [html.H5('Categories'),
                     html.H6([html.P(cat) for cat in game_categories])
                    ],
                    id='categories',
                    className='text-center'
                ),

    return categories


@app.callback(
    Output(component_id='mechanics', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_mechanics(game):

    if game is None:
        return [html.H6('Mechanics'),
                html.H5('No Data')]

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    game_mechanics = game_props['mechanics']

    mechanics = html.Div(
                    [html.H5('Mechanics'),
                     html.H6([html.P(mech) for mech in game_mechanics])
                    ],
                    id='mechanics',
                    className='text-center'
                ),

    return mechanics


if __name__ == '__main__':

    app.run_server(debug=True)
