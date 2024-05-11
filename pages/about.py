
import dash
from dash import html


dash.register_page(__name__, name='The Price is Right', path='/about')

layout = html.Div(
                children=[
                    html.P('About', className='page-text', style={'font-weight': 'bold', 'font-size': 24}),
                    html.P(['This project is intended to extend knowledge and practice on Python-based web scraping, as well as other software development paradigms, such as logging, linting, unit testing dashboarding, version control, and creating git hooks. For more information, please visit my ', html.A('GitHub page.', href='https://github.com/miguelgaspar24/', target='_blank')], className='page-text')
                        ]
            )
