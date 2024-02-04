
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

from alive_progress import alive_it


def get_prices(list_of_games):
	'''
	Scrapes www.jogartabuleiro.pt for board game prices. Takes the following parameters:

    list_of_games (list): a list containing games of boardgames. This list is iterated over
                          to find the correspond prices on the website.

    Returns a pandas DataFrame containing the prices of all games present in list_of_games.
	'''

	session = requests.session()

	games = {}

	progress_bar = alive_it(list_of_games, bar='smooth', spinner='classic', title='Spyder 3 - JogarTabuleiro:')
	for i, game in enumerate(progress_bar):
		try:
			game_query = game
			if ' ' in game:
				game_query = game.replace(' ', '-')
			if ':' in game_query:
				game_query = game_query.replace(':', '')
				
			jogartabuleiro_url = 'https://jogartabuleiro.pt/produto/' + game_query
			jogartabuleiro_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; W…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
			jogartabuleiro_session = session.get(jogartabuleiro_url, headers=jogartabuleiro_headers)
			jogartabuleiro_text = jogartabuleiro_session.text
			jogartabuleiro_soup = BeautifulSoup(jogartabuleiro_text, features='html.parser')

			price_results = jogartabuleiro_soup.find_all('span', class_='woocommerce-Price-amount amount')
			rental_results = jogartabuleiro_soup.find_all('div', itemprop='description')
			language_results = jogartabuleiro_soup.find_all('td', class_='woocommerce-product-attributes-item__value')

			description = rental_results[0].text
			game_language = language_results[0].text.strip()

			if 'ALUGUER' in description:
				raise IndexError
			
			if game_language != 'Inglês':
				raise IndexError

			price = '{:.2f}'.format(price_results[1].text[1:])

			games[game] = price
		
		except IndexError as raised_error:
			games[game] = np.nan

	price_table = pd.DataFrame.from_dict(games, orient='index').reset_index()
	price_table.columns = ['name', 'JogarTabuleiro']
	price_table['name'] = price_table['name'].astype('str')
	price_table['JogarTabuleiro'] = price_table['JogarTabuleiro'].astype('float')
	price_table.sort_values(by=['name'], inplace=True)
	price_table.reset_index(inplace=True)
	price_table.drop(columns=['index'], inplace=True)

	return price_table
