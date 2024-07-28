
import math
import os

import dash
from dash import dash_table, dcc, html, Input, Output, State, callback
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
from io import BytesIO
import pandas as pd
from PIL import Image
from plotly.subplots import make_subplots
import requests

from project.spyders import bgg_spyder


dash.register_page(__name__, name='The Price is Right', path= '/main')

root_path = r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data'

# Read the prices dataset from the stored Excel files
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

# Set some constants needed later
column_order = ['date', 'name', 'JogoNaMesa', 'Gameplay', 'JogarTabuleiro']
master_df = master_df[column_order].sort_values(by='date')
stores_prop = {'JogoNaMesa': {'color': 'red',
                              'url': 'https://jogonamesa.pt/P/ficha.cgi?bgg_id=',
                              'favicon': 'https://jogonamesa.pt/img/favicon.ico'},
               'Gameplay': {'color': 'blue',
                            'url': 'https://gameplay.pt/pt/',
                            'favicon': 'http://www.gameplay.pt/img/favicon.ico?1678899580'},
               'JogarTabuleiro': {'color': 'green',
                                  'url': 'https://jogartabuleiro.pt/',
                                  'favicon': 'https://jogartabuleiro.pt/wp-content/uploads/2018/06/logo_favicon_M9H_icon.ico'}
               }

sorted_dates = sorted(master_df['date'].unique(), reverse=True)

most_recent_date = sorted_dates[0]
previous_date = sorted_dates[1]

most_recent_prices = master_df[master_df['date']==most_recent_date]
previous_prices = master_df[master_df['date']==previous_date]

diff_prices = pd.merge(previous_prices, most_recent_prices, on='name', how='inner', suffixes=('_previous', '_current'))

diff_prices['JogoNaMesa_abs_diff'] = diff_prices['JogoNaMesa_current'] - diff_prices['JogoNaMesa_previous']
diff_prices['Gameplay_abs_diff'] = diff_prices['Gameplay_current'] - diff_prices['Gameplay_previous']
diff_prices['JogarTabuleiro_abs_diff'] = diff_prices['JogarTabuleiro_current'] - diff_prices['JogarTabuleiro_previous']

diff_prices['JogoNaMesa_perc_diff'] = diff_prices['JogoNaMesa_abs_diff'] / diff_prices['JogoNaMesa_previous']
diff_prices['Gameplay_perc_diff'] = diff_prices['Gameplay_abs_diff'] / diff_prices['Gameplay_previous']
diff_prices['JogarTabuleiro_perc_diff'] = diff_prices['JogarTabuleiro_abs_diff'] / diff_prices['JogarTabuleiro_previous']

diff_prices['max_abs_diff'] = diff_prices[['JogoNaMesa_abs_diff', 'Gameplay_abs_diff', 'JogarTabuleiro_abs_diff']].min(axis=1)
diff_prices.sort_values(by=['max_abs_diff', 'name'], ascending=True, inplace=True)

diff_prices.drop(columns=['date_previous',
                          'date_current',
                          'JogoNaMesa_previous',
                          'JogoNaMesa_current',
                          'Gameplay_previous',
                          'Gameplay_current',
                          'JogarTabuleiro_previous',
                          'JogarTabuleiro_current'
                        ],
                inplace=True
            )

current_games = master_df[master_df['date']==most_recent_date]['name'].sort_values().unique()


#############################################################################################################
#                                               PAGE LAYOUT                                                 #
#############################################################################################################

layout = html.Div(
        children=[
# -----------------------------------------------------------------------------------------------------
#                                            1. MENU FILTERS
# -----------------------------------------------------------------------------------------------------
            html.Div(
                children=[
# --------------------------------------- Listing Mode Selector ---------------------------------------
                    html.Div(
                        children=[
                            html.Div(children='Mode', className='menu-title'),
                            dbc.RadioItems(options=[' Current', ' Legacy'],
                                           value=' Current',
                                           id='mode-select',
                                           labelCheckedClassName='fw-bold text-dark',
                                           inputCheckedClassName='border-0 bg-warning'
                                        )
                        ]
                    ),
# --------------------------------------- Game Selection Dropdown -------------------------------------
                    html.Div(
                        children=[
                            html.Div(children='Game', className='menu-title'),
                            dcc.Dropdown(
                                options=[
                                        {'label': game, 'value': game}
                                        for game in current_games
                                        ],
                                value='Alchemists',
                                id='game-filter',
                                clearable=False,
                                searchable=True,
                                placeholder='Select a game',
                                optionHeight=80
                            )
                        ], style={'width': '250px'}
                    ),
# -------------------------------------- Store Checklist Selector -------------------------------------
                    html.Div(
                        children=[
                            html.Div(children='Store', className='menu-title'),
                            dbc.Checklist(
                                options=[
                                        {'label': ' ' + store, 'value': store}
                                        for store in list(stores_prop.keys())
                                        ],
                                value=list(stores_prop.keys()),
                                input_checked_style={'backgroundColor': '#373737', 'borderColor': '#ebab2a', 'borderWidth': 2},
                                #label_checked_style={'color': 'green'},
                                id='store-filter',
                                className='checklist',
                            )
                        ]
                    ),
# ----------------------------------------- Date Range Selector ---------------------------------------
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
                ], className='menu'
            ),
# -----------------------------------------------------------------------------------------------------
#                                 2. DAILY GAME PRICE OSCILATIONS
# -----------------------------------------------------------------------------------------------------
            html.Div([
                html.H3('Top 10 Daily Price Drops', className='text-center'),
                dash_table.DataTable(
                            id='data-table',
                            data=diff_prices.query('max_abs_diff < 0').head(10).to_dict('records'),
                            columns=[
                                {'name': 'Game', 'id': 'name', 'type': 'text'},
                                {'name': 'JNM', 'id': 'JogoNaMesa_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                                #{'name': 'JNM (%)', 'id': 'JogoNaMesa_perc_diff', 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.percentage, sign=Sign.positive)},
                                {'name': 'GP', 'id': 'Gameplay_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                                #{'name': 'GP (%)', 'id': 'Gameplay_perc_diff', 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.percentage, sign=Sign.positive)},
                                {'name': 'JT', 'id': 'JogarTabuleiro_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                                #{'name': 'JT (%)', 'id': 'JogarTabuleiro_perc_diff', 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.percentage, sign=Sign.positive)}
                            ],
                            #virtualization=True,
                            #fixed_rows={'headers': True},
                            sort_action='native',
                            sort_mode='multi',
                            page_action='native',
                            page_current=0,
                            page_size=5,
                            tooltip_header={col: col.split('_')[0] for col in diff_prices.columns if col not in ['name']},
                            tooltip_data=[
                                    {
                                     column: {'value': str(value), 'type': 'markdown'}
                                     for column, value in row.items() if column in ['name'] and len(value) > 32
                                    } for row in diff_prices.to_dict('records')
                                ],
                            tooltip_delay=0,
                            tooltip_duration=None,
                            style_cell={'minWidth': 95,
                                        'maxWidth': 95,
                                        'width': 95,
                                        #'overflow': 'hidden',
                                        #'textOverflow': 'ellipsis',
                                        'whiteSpace': 'normal',
                                        'height': 'auto',
                                        'textAlign': 'center',
                                        'border': '1.5px solid #4682B4'
                                        },
                            style_cell_conditional=[
                                            {'if': {'column_id': 'name'},
                                            'width': '30%'}
                                            ],
                            style_data={
                                'backgroundColor': 'white',
                                'color': 'black'
                                },
                            style_data_conditional=[
                                            {'if': {'column_id': 'name'},
                                            'textAlign': 'right'},
                                            {'if': {'row_index': 'odd'},
                                            'backgroundColor': '#DCDCDC'},
                                            {'if': {'filter_query': '{JogoNaMesa_abs_diff} < 0',
                                                    'column_id': 'JogoNaMesa_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#03C04A'},
                                            {'if': {'filter_query': '{JogoNaMesa_abs_diff} = 0',
                                                    'column_id': 'JogoNaMesa_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#FCD12A'},
                                            {'if': {'filter_query': '{JogoNaMesa_abs_diff} > 0',
                                                    'column_id': 'JogoNaMesa_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#EA3C53'},
                                            {'if': {'filter_query': '{Gameplay_abs_diff} < 0',
                                                    'column_id': 'Gameplay_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#03C04A'},
                                            {'if': {'filter_query': '{Gameplay_abs_diff} = 0',
                                                    'column_id': 'Gameplay_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#FCD12A'},
                                            {'if': {'filter_query': '{Gameplay_abs_diff} > 0',
                                                    'column_id': 'Gameplay_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#EA3C53'},
                                            {'if': {'filter_query': '{JogarTabuleiro_abs_diff} < 0',
                                                    'column_id': 'JogarTabuleiro_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#03C04A'},
                                            {'if': {'filter_query': '{JogarTabuleiro_abs_diff} = 0',
                                                    'column_id': 'JogarTabuleiro_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#FCD12A'},
                                            {'if': {'filter_query': '{JogarTabuleiro_abs_diff} > 0',
                                                    'column_id': 'JogarTabuleiro_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#EA3C53'}
                                            ],
                            style_header={
                                'backgroundColor': '#3C3C3C',
                                'color': 'white',
                                'height': '40px',
                                'fontWeight': 'bold',
                                'fontSize': 15,
                                'border': '1.5px solid lightgray'
                                },
                            css=[
                                {
                                'selector': '.dash-table-tooltip',
                                'rule': 'background-color: #3C3C3C; \
                                        font-family: monospace; \
                                        color: white; \
                                        text-align: center; \
                                        border: 2px solid #EBAB2A'
                                }
                            ]
                        )
                ], className='wrapper'
            ),
# -----------------------------------------------------------------------------------------------------
#                                     3. GAME INFO EXPOSED ROW
# -----------------------------------------------------------------------------------------------------
            html.H3('Game Details', className='text-center'),
            dbc.Row(
                [
# ------------------------------------------ Game Cover -----------------------------------------------
                dbc.Col(dbc.CardBody(
                            [html.A([
                                    html.Img(
                                        id='game-cover-image',
                                        className='image',
                                        alt='Game Cover',
                                        src=''
                                        ),
                                    #dbc.Spinner(html.Div(id='loading-image'), color='warning')
                                    dcc.Loading(html.Div(id='loading-image'),
                                                type='graph',
                                                color='firebrick',
                                                fullscreen=True
                                            )
                                    ], id='bgg-game-url', href='https://boardgamegeek.com/', target='_blank' # target=_blank makes URLs open in a new browser tab
                                )
                            ]
                        )
                    ),
# ----------------------------- Game BGG Rating, Votes, and Complexity --------------------------------
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
# --------------------------------- Player Count and Game Duration-------------------------------------
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
# ------------------------------ Release Year and Language Dependence ---------------------------------
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
# -----------------------------------------------------------------------------------------------------
#                              4. GAME INFO COLLAPSIBLE CONTENT
# -----------------------------------------------------------------------------------------------------
            dbc.Row(
                [
                dbc.Col(dbc.CardBody(
                            [
# ------------------------------------ Collapse Button Control ----------------------------------------
                            dbc.Button(
                                'Additional Game Info',
                                id='collapse-button',
                                className='d-grid gap-2 col-3 mx-auto card-button',
                                color='dark',
                                n_clicks=0,
                            ),
# ----------------------------------- Collapsible Area Content -----------------------------------------
                            dbc.Collapse(
                                dbc.Row(
                                        [
                                        dbc.Col(
                                            dbc.CardBody('No Data',
                                            id='collapse-content-creators',
                                            className='text-center')),
                                        dbc.Col(
                                            dbc.CardBody('No Data',
                                            id='collapse-content-types',
                                            className='text-center')),
                                        dbc.Col(
                                            dbc.CardBody('No Data',
                                            id='collapse-content-categories',
                                            className='text-center')),
                                        dbc.Col(
                                            dbc.CardBody('No Data',
                                            id='collapse-content-mechanics',
                                            className='text-center')),
                                        ]
                                    ), id='collapse', is_open=False
                                )
                            ], className='d-grid gap-2'
                        )
                    )
                ], className='wrapper'
            ),
# -----------------------------------------------------------------------------------------------------
#                                   5. DAY-TO-DAY PRICE VARIATION
# -----------------------------------------------------------------------------------------------------
           html.Div([
                html.H4('Daily Price Variation', className='text-center'),
                dash_table.DataTable(
                            id='game-table',
                            data=diff_prices.head(0).to_dict('records'),
                            columns=[
                                {'name': 'Game', 'id': 'name', 'type': 'text'},
                                {'name': 'JNM', 'id': 'JogoNaMesa_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                                #{'name': 'JNM (%)', 'id': 'JogoNaMesa_perc_diff', 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.percentage, sign=Sign.positive)},
                                {'name': 'GP', 'id': 'Gameplay_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                                #{'name': 'GP (%)', 'id': 'Gameplay_perc_diff', 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.percentage, sign=Sign.positive)},
                                {'name': 'JT', 'id': 'JogarTabuleiro_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                                #{'name': 'JT (%)', 'id': 'JogarTabuleiro_perc_diff', 'type': 'numeric', 'format': Format(precision=1, scheme=Scheme.percentage, sign=Sign.positive)}
                            ],
                            sort_action='native',
                            sort_mode='multi',
                            page_action='native',
                            page_current=0,
                            page_size=1,
                            tooltip_header={col: col.split('_')[0] for col in diff_prices.columns if col not in ['name']},
                            tooltip_data=[
                                    {
                                     column: {'value': str(value), 'type': 'markdown'}
                                     for column, value in row.items() if column in ['name'] and len(value) > 32
                                    } for row in diff_prices.to_dict('records')
                                ],
                            tooltip_delay=0,
                            tooltip_duration=None,
                            style_cell={'minWidth': 95,
                                        'maxWidth': 95,
                                        'width': 95,
                                        'whiteSpace': 'normal',
                                        'height': 'auto',
                                        'textAlign': 'center',
                                        'border': '1.5px solid #4682B4'
                                        },
                            style_cell_conditional=[
                                            {'if': {'column_id': 'name'},
                                            'width': '30%'}
                                            ],
                            style_data={
                                'backgroundColor': 'white',
                                'color': 'black'
                                },
                            style_data_conditional=[
                                            {'if': {'column_id': 'name'},
                                            'textAlign': 'right'},
                                            {'if': {'row_index': 'odd'},
                                            'backgroundColor': '#DCDCDC'},
                                            {'if': {'filter_query': '{JogoNaMesa_abs_diff} < 0',
                                                    'column_id': 'JogoNaMesa_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#03C04A'},
                                            {'if': {'filter_query': '{JogoNaMesa_abs_diff} = 0',
                                                    'column_id': 'JogoNaMesa_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#FCD12A'},
                                            {'if': {'filter_query': '{JogoNaMesa_abs_diff} > 0',
                                                    'column_id': 'JogoNaMesa_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#EA3C53'},
                                            {'if': {'filter_query': '{Gameplay_abs_diff} < 0',
                                                    'column_id': 'Gameplay_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#03C04A'},
                                            {'if': {'filter_query': '{Gameplay_abs_diff} = 0',
                                                    'column_id': 'Gameplay_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#FCD12A'},
                                            {'if': {'filter_query': '{Gameplay_abs_diff} > 0',
                                                    'column_id': 'Gameplay_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#EA3C53'},
                                            {'if': {'filter_query': '{JogarTabuleiro_abs_diff} < 0',
                                                    'column_id': 'JogarTabuleiro_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#03C04A'},
                                            {'if': {'filter_query': '{JogarTabuleiro_abs_diff} = 0',
                                                    'column_id': 'JogarTabuleiro_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#FCD12A'},
                                            {'if': {'filter_query': '{JogarTabuleiro_abs_diff} > 0',
                                                    'column_id': 'JogarTabuleiro_abs_diff'},
                                            'color': 'black',
                                            'backgroundColor': '#EA3C53'}
                                            ],
                            style_header={
                                'backgroundColor': '#3C3C3C',
                                'color': 'white',
                                'height': '40px',
                                'fontWeight': 'bold',
                                'fontSize': 15,
                                'border': '1.5px solid lightgray'
                                },
                            css=[
                                {
                                'selector': '.dash-table-tooltip',
                                'rule': 'background-color: #3C3C3C; \
                                        font-family: monospace; \
                                        color: white; \
                                        text-align: center; \
                                        border: 2px solid #EBAB2A'
                                }
                            ]
                        )
                ], className='wrapper'
            ),
# -----------------------------------------------------------------------------------------------------
#                                   6. HISTORICAL LOW-HIGH PRICES
# -----------------------------------------------------------------------------------------------------
            dbc.Row(
                [
# ----------------------------------------- Lowest Price ----------------------------------------------
                dbc.Col(dbc.Card(dbc.CardBody(
                                    [html.H5(' Lowest Price', className='bi bi-caret-down-fill text-success'),
                                    html.H3('No Data')],
                                    id='card-lowest',
                                    className='text-center'
                                )
                            )
                    ),
# ----------------------------------------- Highest Price ---------------------------------------------
                dbc.Col(dbc.Card(dbc.CardBody(
                                    [html.H5(' Highest Price', className='bi bi-caret-up-fill text-danger'),
                                    html.H3('No Data')],
                                    id='card-highest',
                                    className='text-center'
                                )
                            )
                    )
                ], className='wrapper'
            ),
# -----------------------------------------------------------------------------------------------------
#                                       7. PRICE GRAPH OVER TIME
# -----------------------------------------------------------------------------------------------------
            html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(
                                    id='price-chart',
                                    config={'displayModeBar': False},
                                    ),
                                    className='card-graph'
                        )
                    ], className='wrapper'
            )
    ]
)


#############################################################################################################
#                                               CALLBACKS                                                   #
#############################################################################################################

# -----------------------------------------------------------------------------------------------------
#                                            1. MENU FILTERS
# -----------------------------------------------------------------------------------------------------

# --------------------------------------- Listing Mode Selector ---------------------------------------

@callback(
    Output(component_id='game-filter', component_property='options'),
    Input(component_id='mode-select', component_property='value')
)
def update_game_filter(value):
    
    if value == ' Legacy':
        current_games = master_df['name'].sort_values().unique()

    if value == ' Current':
        most_recent_date = sorted(master_df['date'].unique(), reverse=True)[0]
        current_games = master_df[master_df['date']==most_recent_date]['name'].sort_values().unique()

    return current_games


# ----------------------------------------- Date Range Selector ---------------------------------------
@callback(
    Output(component_id='date-range', component_property='max_date_allowed'),
    Output(component_id='date-range', component_property='end_date'),
    Output(component_id='date-range', component_property='min_date_allowed'),
    Output(component_id='date-range', component_property='start_date'),
    Input(component_id='game-filter', component_property='value'),
    Input(component_id='mode-select', component_property='value')
)
def update_date_picker_range(game, mode):
    
    if mode == ' Legacy':
        filtered_data = master_df.query('name == @game')

    if mode == ' Current':
        filtered_data = master_df.query('name == @game and date >= "2023-01-01"')

    max_date_allowed = filtered_data['date'].max().date()
    end_date = filtered_data['date'].max().date()

    min_date_allowed = filtered_data['date'].min().date()
    start_date = filtered_data['date'].min().date()

    return (max_date_allowed, end_date, min_date_allowed, start_date)

# -----------------------------------------------------------------------------------------------------
#                                 2. DAILY GAME PRICE OSCILATIONS
# -----------------------------------------------------------------------------------------------------

@callback(
    Output(component_id='data-table', component_property='data'),
    Output(component_id='data-table', component_property='columns'),
    Input(component_id='game-filter', component_property='value'),
    Input(component_id='store-filter', component_property='value')
)
def update_data_table(game, stores):
    
    table_data = diff_prices.query('max_abs_diff < 0').head(10).to_dict('records')

    base_columns = {
                    'JogoNaMesa': {'name': 'JNM', 'id': 'JogoNaMesa_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                    'Gameplay': {'name': 'GP', 'id': 'Gameplay_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                    'JogarTabuleiro': {'name': 'JT', 'id': 'JogarTabuleiro_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')}
                }
    
    table_columns = [base_columns[store] for store in stores]
    table_columns.insert(0, {'name': 'Game', 'id': 'name', 'type': 'text'})

    return (table_data, table_columns)

# -----------------------------------------------------------------------------------------------------
#                                     3. GAME INFO EXPOSED ROW
# -----------------------------------------------------------------------------------------------------

# ----------------------------------------- Game Cover ------------------------------------------------
@callback(
    Output(component_id='game-cover-image', component_property='src'),
    Output(component_id='bgg-game-url', component_property='href'),
    Output(component_id='loading-image', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_game_image(game):

    if game is None:
        return ('', '', '')

    global root_path

    game_props = bgg_spyder.get_game_properties(root_path, game)

    image_url = game_props['game_image']
    game_url = game_props['url']

    image_content = requests.get(image_url)
    image_display = Image.open(BytesIO(image_content.content))

    image_source = image_display

    return (image_source, game_url, '')


# ---------------------------- Game BGG Rating, Number of Votes, and Complexity -----------------------
@callback(
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


# --------------------------------- Player Count and Game Duration ------------------------------------
@callback(
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


# ------------------------------- Release Year and Language Dependence --------------------------------
@callback(
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

# -----------------------------------------------------------------------------------------------------
#                              4. GAME INFO COLLAPSIBLE CONTENT
# -----------------------------------------------------------------------------------------------------

# -------------------------- Open and Close Collapsible Element  -------------------------------------
@callback(
    Output(component_id='collapse', component_property='is_open'),
    Input(component_id='collapse-button', component_property='n_clicks'),
    State(component_id='collapse', component_property='is_open')
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# -------------------------- Game Designer, Artit, and Publisher -------------------------------------
@callback(
    Output('collapse-content-creators', 'children'),
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


# -------------------------------------- Game Type ---------------------------------------------------
@callback(
    Output('collapse-content-types', 'children'),
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


# ------------------------------------ Game Categories -----------------------------------------------
@callback(
    Output(component_id='collapse-content-categories', component_property='children'),
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


# ------------------------------------ Game Mechanics ------------------------------------------------
@callback(
    Output(component_id='collapse-content-mechanics', component_property='children'),
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

# -----------------------------------------------------------------------------------------------------
#                                   5. DAY-TO-DAY PRICE VARIATION
# -----------------------------------------------------------------------------------------------------

@callback(
    Output(component_id='game-table', component_property='data'),
    Output(component_id='game-table', component_property='columns'),
    Input(component_id='game-filter', component_property='value'),
    Input(component_id='store-filter', component_property='value')
)
def update_game_table(game, stores):
    
    filtered_data = diff_prices.query('name == @game')
    table_data = filtered_data.to_dict('records')

    base_columns = {
                'JogoNaMesa': {'name': 'JNM', 'id': 'JogoNaMesa_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                'Gameplay': {'name': 'GP', 'id': 'Gameplay_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')},
                'JogarTabuleiro': {'name': 'JT', 'id': 'JogarTabuleiro_abs_diff', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix='€')}
            }
    
    table_columns = [base_columns[store] for store in stores]
    table_columns.insert(0, {'name': 'Game', 'id': 'name', 'type': 'text'})

    return (table_data, table_columns)

# -----------------------------------------------------------------------------------------------------
#                                   6. HISTORICAL LOW-HIGH PRICES
# -----------------------------------------------------------------------------------------------------

@callback(
    Output(component_id='card-lowest', component_property='children'),
    Output(component_id='card-highest', component_property='children'),
    Input(component_id='game-filter', component_property='value')
)
def update_min_max_cards(game):

    try:
        global root_path

        game_props = bgg_spyder.get_game_properties(root_path, game)

        game_url = game_props['url']
        game_id = game_url.split('/')[4]
    
    except TypeError:
        game_id = ''

    filtered_data = master_df.query('name == @game')

    min_values = [filtered_data[store].min() for store in list(stores_prop.keys())]
    min_idx = min_values.index(min(min_values))
    min_store = list(stores_prop.keys())[min_idx]
    min_site = stores_prop[min_store]['url'] + game_id if min_store == 'JogoNaMesa' else stores_prop[min_store]['url']
    min_card_value = 'No Data' if math.isnan(min(min_values)) else '{:.2f}'.format(min(min_values)) + '€'

    max_values = [filtered_data[store].max() for store in list(stores_prop.keys())]
    max_idx = max_values.index(max(max_values))
    max_store = list(stores_prop.keys())[max_idx]
    max_site = stores_prop[max_store]['url'] + game_id if max_store == 'JogoNaMesa' else stores_prop[max_store]['url']
    max_card_value = 'No Data' if math.isnan(max(max_values)) else '{:.2f}'.format(max(max_values)) + '€'

    low_card = html.Div(
                    [html.H5(' Lowest Price', className='bi bi-caret-down-fill text-success'),
                     html.H3(min_card_value),
                     dbc.Button(children=[html.Img(src=stores_prop[min_store]['favicon']), ' ' + min_store],
                                outline=False,
                                href=min_site,
                                target='_blank',
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
                                target='_blank',
                                className='card-button'
                                )],
                    id='card-highest',
                    className='text-center'
                )
                    
    return (low_card, high_card)

# -----------------------------------------------------------------------------------------------------
#                                       7. PRICE GRAPH OVER TIME
# -----------------------------------------------------------------------------------------------------

@callback(
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

    for store in list(stores):
        fig.append_trace({'x': filtered_data['date'],
                          'y': filtered_data[store],
                          'type': 'scatter',
                          'name': store,
                          'line': {'color': stores_prop[store]['color'], 'width': 3},
                          'hovertemplate': '%{y:.2f}€'#<extra></extra>'
                          },
                        1,
                        1,
                        )

    return fig
