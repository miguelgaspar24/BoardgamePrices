
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests


def get_prices(list_of_games):
    '''
    Scrapes www.gameplay.pt for boardgame prices. Takes the folllowing parameters:

    list_of_games (list): a list containing games of boardgames. This list is iterated over
                          to find the correspond prices on the website.

    Returns a pandas DataFrame containing the prices of all games present in list_of_games.
    '''

    session = requests.session()

    games = {}
    for i, game in enumerate(list_of_games):
        try:
            game_query = game
            if ' ' in game:
                game_query = game.replace(' ', '+')
                
            gameplay_url = 'http://www.gameplay.pt/search?search_query=' + game_query
            gameplay_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; W…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
            gameplay_session = session.get(gameplay_url, headers=gameplay_headers)
            gameplay_text = gameplay_session.text
            gameplay_soup = BeautifulSoup(gameplay_text, features='html.parser')
            search_results = gameplay_soup.find_all('div', class_='right-block')

            prices = []
            for result in search_results:
                name = result.a.string[1:-1]
                if ':' in game and ':' not in name:
                    try:
                        pre_colon = game.split(':')[0]
                        post_colon = game.split(':')[1]
                        pre_bracket = name.split('(')[0]
                        post_bracket = name.split('(')[1]
                    except IndexError:
                        raise ValueError
                    if pre_colon + post_colon == pre_bracket + post_bracket[:-1]:
                        price = result.span.string[1:-1].replace(',', '.')
                        prices.append(price)
                else:
                    if name == game:
                        price = result.span.string[1:-1].replace(',', '.')
                        prices.append(price)

            if len(prices) == 0:
                raise ValueError

            games[game] = min(prices)

        except ValueError:
            games[game] = np.nan

    price_table = pd.DataFrame.from_dict(games, orient='index').reset_index()
    price_table.columns = ['name', 'Gameplay']
    price_table['name'] = price_table['name'].astype('str')
    price_table['Gameplay'] = price_table['Gameplay'].astype('float')
    price_table.sort_values(by=['name'], inplace=True)
    price_table.reset_index(inplace=True)
    price_table.drop(columns=['index'], inplace=True)

    return price_table
