
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
from unidecode import unidecode

from alive_progress import alive_it


def get_prices(list_of_games):
    '''
    Scrapes www.gameplay.pt for boardgame prices. Takes the folllowing parameters:

    list_of_games (list): a list containing games of boardgames. This list is iterated over
                          to find the correspond prices on the website.

    Returns a pandas DataFrame containing the prices of all games present in list_of_games.
    '''

    session = requests.session()

    games = {}

    progress_bar = alive_it(list_of_games, bar='smooth', spinner='classic', title='Spyder 2 - GamePlay:      ')
    for i, game in enumerate(progress_bar):
        try:
            game_query = game
            if ' ' in game:
                game_query = game.replace(' ', '+')
                
            gameplay_url = 'http://www.gameplay.pt/en/search?search_query=' + game_query
            gameplay_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; W…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
            gameplay_session = session.get(gameplay_url, headers=gameplay_headers)
            gameplay_text = gameplay_session.text
            gameplay_soup = BeautifulSoup(gameplay_text, features='html.parser')
            
            search_results = gameplay_soup.find_all('a', class_="thumbnail product-thumbnail")

            for result in search_results:

                game_url = result.img['data-full-size-image-url']

                curated_game_name = unidecode(game.replace('Ultimate Edition', 'Master Set').lower()).replace('-', '').replace(' ', '-').replace(':', '')
                curated_game_url = game_url.split('/')[-1].split('.')[0]
                
                # Fixes issues with "7 Wonders Duel: Agora" and "Aquatica" urls
                if 'preorder' in curated_game_url:
                    curated_game_url = curated_game_url.split('preorder-')[1]

                if curated_game_name == curated_game_url:

                    game_page = session.get(result['href'], headers=gameplay_headers)
                    game_text = game_page.text
                    game_soup = BeautifulSoup(game_text, features='html.parser')
                    price = '{:.2f}'.format(float(game_soup.find('div', class_='current-price').span.text[1:]))
                    break

                else:
                    price = np.nan

            games[game] = price

        except TypeError:
            games[game] = np.nan

    price_table = pd.DataFrame.from_dict(games, orient='index').reset_index()
    price_table.columns = ['name', 'Gameplay']
    price_table['name'] = price_table['name'].astype('str')
    price_table['Gameplay'] = price_table['Gameplay'].astype('float')
    price_table.sort_values(by=['name'], inplace=True)
    price_table.reset_index(inplace=True)
    price_table.drop(columns=['index'], inplace=True)

    return price_table
