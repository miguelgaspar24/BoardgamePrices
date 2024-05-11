
import dash
from dash import html


dash.register_page(__name__, name='The Price is Right', path='/faq')

layout = html.Div(
                children=[
                    html.P('FAQ', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('This section explains how each element of the main page works and which options are available for each.', className='page-text'),
                    html.P('Menu Filters', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('Mode = "Current" uses only the games currently in the Jogo Na Mesa wishlist. Mode = "Legacy" uses all games that have ever historically been in the Jogo Na Mesa wishlist. Game is a dropdown list that allows selection of the specific game whose history and pricing we want to analyze. Store is a multi-selection list that allows selection and deselection of any of the listed stores to include or exclude them, respectively, from consideration. Date Range allows the selection of the start and end date to consider for analysis', className='page-text'),
                    html.P('Top 10 Daily Price Drops', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('This table lists up to 10 games whose games have dropped in any of the available selected vendors. Price drops are labelled green, no price changes are labelled yellow, and unavailable data is left blank', className='page-text'),
                    html.P('Game Details', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('Game details scraped from the respective BoardGameGeek page, such as player count, language dependence, rating, and year published, for instance. The "Additional Game Info" button can be clicked on to reveal game authors and categoriations. Clicking the button a second time will collapse the results back again.', className='page-text'),
                    html.P('Daily Price Variations', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('This table contains a single row with the price variation of the currently selected game between the current day and the last available day of price data for that game. As in the "Top 10 Daily Price Drops" table, price drops are labelled green, no price changes are labelled yellow, unavailable data is left blank, and price increases are labelled red.', className='page-text'),
                    html.P('Historical Min-Max Pricing', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('These two cards show the historically lowest and highest price for the currently selected game, as well as the respective vendor where they were detected as lowest/highest. Clicking the button with the vendor name sends us to that vendor website', className='page-text'),
                    html.P('Graph Area', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P('The graph shows the price progression of the currently selected game over time for each of the selected vendors. Specific vendors can be excluded and re-included by clicking on their respective line in the graph area or in the legend on the right area of the graph.', className='page-text')
                        ]
            )
