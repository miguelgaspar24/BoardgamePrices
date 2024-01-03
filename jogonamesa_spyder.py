
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

from credentials import get_credentials


def get_prices():
	'''
	Scrapes www.jogonamesa.pt for board game prices. Takes NO parameters.

	Returns a list of boardgame names, and pandas DataFrame containing those games' prices.
	'''

	session = requests.session()
	login_url = 'https://jogonamesa.pt/P/user_login.cgi'
	login = session.get(login_url, headers={'User-Agent': 'Mozilla/5.0'})
	login = session.post(
						 login_url,
						 data=get_credentials()
						)

	wishlist_url = 'https://jogonamesa.pt/P/user_wishlist.cgi'
	wishlist = session.get(wishlist_url)
	wishlist_html = wishlist.text
	wishlist_soup = BeautifulSoup(wishlist_html, features='html.parser')

	pages = wishlist_soup.find_all('a', class_='paginacao')
	n_pages = int(len(pages) / 2)
	wishlist_urls = [wishlist_url + '?accao=8&num={}'.format(str(page_number)) for page_number in range(1, n_pages + 1)]

	games = {}
	for url in wishlist_urls:

		page = session.get(url)
		page_html = page.content.decode('utf-8','ignore') #The decode() function here circumvents incorrectly decoded utf8 characters (mostly accented vowels)
		page_soup = BeautifulSoup(page_html, features='html.parser')
		name_blocks = page_soup.find_all('div', class_='wishlist_caracteristicas')
		price_blocks = page_soup.find_all('div', class_='wishlist_opcoes')

		for i, (name_block, price_block) in enumerate(zip(name_blocks, price_blocks)):
			name = name_block.a.string
			price_tags = price_block.find_all('a', 'botao')
			try:
				prices = []
				if len(price_tags) != 0:

					for tag in price_tags:
						price = tag.contents[1].split('€')[1]
						availability = tag.find_next('span').contents[0].string
						if 'Sem prev' not in availability:
							prices.append(price)

					if len(prices) == 0:
						raise AttributeError

					games[name] = min(prices)

				else:
					raise AttributeError

			except AttributeError:
				games[name] = np.nan

	price_table = pd.DataFrame.from_dict(games, orient='index').reset_index()

	price_table.columns = ['name', 'JogoNaMesa']
	price_table['name'] = price_table['name'].astype('str')
	price_table['JogoNaMesa'] = price_table['JogoNaMesa'].astype('float')
	price_table.sort_values(by=['name'], inplace=True)
	price_table.reset_index(inplace=True)
	price_table.drop(columns=['index'], inplace=True)

	games_list = list(games.keys())

	return games_list, price_table
