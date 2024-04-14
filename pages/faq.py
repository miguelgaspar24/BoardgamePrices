
import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__)

layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.H1(children='The Price is Right: Board Game Edition', className='header-title'),
                    html.P(children=('This is a test page for the "use_pages" functionality of Dash'),
                           className='header-description')
                        ],
                className='header'
            )
        ]
)
