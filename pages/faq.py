
import dash
from dash import html


dash.register_page(__name__, path='/faq')

layout = html.Div(
                children=[
                    html.P(children=('This is a test page for the "use_pages" functionality of Dash'))
                        ]
            )
