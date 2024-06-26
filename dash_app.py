
import dash
from dash import Dash, html
import dash_bootstrap_components as dbc


external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]

app = Dash(__name__,
           title='The Price is Right',
           pages_folder='pages',
           use_pages=True,
           external_stylesheets=external_stylesheets)

app.layout = html.Div(
                children=[
                    dbc.NavbarSimple(
                                children=[
                                    dbc.NavItem(dbc.NavLink('Main', href='/main')),
                                    dbc.NavItem(dbc.NavLink('FAQ', href='/faq')),
                                    dbc.NavItem(dbc.NavLink('About', href='/about'))
                                ],
                                id='navbar',
                                brand='Home',
                                brand_href='/',
                                color='#222222',
                                dark=True
                            ),
                    html.Div(
                        children=[
                            html.H1(children='The Price is Right: Board Game Edition', className='header-title'),
                            html.P(children='🃏♟️🎲🧩', className='header-emoji'),
                            html.P(children=('Track the prices of board games across online vendors to find the best deals at any given time!'), className='header-description')
                                ],
                        className='header'
                    ),
                    dash.page_container
                ]
)


if __name__ == '__main__':

    app.run_server(debug=True)
