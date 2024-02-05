
from bs4 import BeautifulSoup
import numpy as np
import os
import pandas as pd
import requests

from alive_progress import alive_it

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
	bgg_ids = {}

	progress_bar = alive_it(wishlist_urls, bar='smooth', spinner='classic', title='Spyder 1 - JogoNaMesa:    ')
	for url in progress_bar:

		page = session.get(url)
		page_html = page.content.decode('utf-8','ignore') #The decode() function here circumvents incorrectly decoded utf8 characters (mostly accented vowels)
		page_soup = BeautifulSoup(page_html, features='html.parser')
		name_blocks = page_soup.find_all('div', class_='wishlist_caracteristicas')
		price_blocks = page_soup.find_all('div', class_='wishlist_opcoes')

		for i, (name_block, price_block) in enumerate(zip(name_blocks, price_blocks)):
			name = name_block.a.string

			bgg_id = name_block.find('a', class_='bgg')['href'].split('/boardgame/')[1]
			bgg_ids[name] = int(bgg_id)

			price_tags = price_block.find_all('a', 'botao')
			try:
				prices = []
				if len(price_tags) != 0:

					for tag in price_tags:
						price = '{:.2f}'.format(tag.contents[1].split('€')[1])
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

	games_list = list(games.keys())

	price_table = pd.DataFrame.from_dict(games, orient='index').reset_index()

	price_table.columns = ['name', 'JogoNaMesa']
	price_table['name'] = price_table['name'].astype('str')
	price_table['JogoNaMesa'] = price_table['JogoNaMesa'].astype('float')
	price_table.sort_values(by=['name'], inplace=True)
	price_table.reset_index(inplace=True)
	price_table.drop(columns=['index'], inplace=True)

	bgg_id_table = pd.DataFrame.from_dict(bgg_ids, orient='index').reset_index()
	
	bgg_id_table.columns = ['name', 'BGG_ID']
	bgg_id_table['name'] = bgg_id_table['name'].astype('str')
	bgg_id_table['BGG_ID'] = bgg_id_table['BGG_ID'].astype('int')
	bgg_id_table.sort_values(by=['name'], inplace=True)
	bgg_id_table.reset_index(inplace=True)
	bgg_id_table.drop(columns=['index'], inplace=True)

	savepath = r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data'
	filename = os.path.join(savepath, 'boardgames_bgg_ids.xlsx')
	if not os.path.isfile(filename):
		bgg_id_table.to_excel(
							filename,
							index=False,
							sheet_name='data',
							na_rep='NaN',
							)
	else:
		with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
			bgg_id_table.to_excel(
								writer,
								index=False,
								sheet_name='data',
								na_rep='NaN',
								)

	return games_list, price_table
