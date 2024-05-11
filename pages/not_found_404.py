
import dash
from dash import html


dash.register_page(__name__, name='The Price is Right')

layout = html.Div(children=[html.H4('Welcome to the landing page.', className='page-text'),
                            html.H4('Please select a functional page from the navigation bar at the top.', className='page-text')])
