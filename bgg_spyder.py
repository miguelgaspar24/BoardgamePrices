
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import requests


def get_game_properties(file_path, game_name):

    #savepath = r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data'
    filename = os.path.join(file_path, 'boardgames_bgg_ids.xlsx')
    bgg_ids_df = pd.read_excel(filename)

    game_id = bgg_ids_df.query('name=="' + game_name + '"')['BGG_ID'].values[0]

    session = requests.session()
    bgg_url = 'http://www.boardgamegeek.com/boardgame/' + str(game_id)
    bgg_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; W…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
    bgg_session = session.get(bgg_url, headers=bgg_headers)
    bgg_text = bgg_session.text
    bgg_soup = BeautifulSoup(bgg_text, features='html.parser')

    main_script = bgg_soup.find_all('script')[2].contents[0]
    clean_script = main_script.split('GEEK.geekitemPreload = ')[1].split(';\n\tGEEK.geekitemSettings')[0]

    game_properties = {}

    game_properties['url'] = bgg_url

    game_properties['language_dependence'] = json.loads(clean_script)['item']['polls']['languagedependence']

    game_properties['average_rating'] = json.loads(clean_script)['item']['stats']['average']
    game_properties['n_rating_votes'] = json.loads(clean_script)['item']['stats']['usersrated']
    game_properties['complexity'] = json.loads(clean_script)['item']['stats']['avgweight']

    game_properties['year_published'] = json.loads(clean_script)['item']['yearpublished']
    game_properties['min_players'] = json.loads(clean_script)['item']['minplayers']
    game_properties['max_players'] = json.loads(clean_script)['item']['maxplayers']
    game_properties['min_playtime'] = json.loads(clean_script)['item']['minplaytime']
    game_properties['max_playtime'] = json.loads(clean_script)['item']['maxplaytime']

    game_properties['designer'] = json.loads(clean_script)['item']['links']['boardgamedesigner'][0]['name']
    game_properties['artist'] = json.loads(clean_script)['item']['links']['boardgameartist'][0]['name']
    game_properties['publisher'] = json.loads(clean_script)['item']['links']['boardgamepublisher'][0]['name']

    types_list = json.loads(clean_script)['item']['links']['boardgamesubdomain']
    game_properties['types'] = [types_list[n]['name'].split(' ')[0] for n in range(len(types_list))]

    categories_list = json.loads(clean_script)['item']['links']['boardgamecategory']
    game_properties['categories'] = [categories_list[n]['name'] for n in range(len(categories_list))]

    mechanics_list = json.loads(clean_script)['item']['links']['boardgamemechanic']
    game_properties['mechanics'] = [mechanics_list[n]['name'] for n in range(len(mechanics_list))]

    #game_properties['game_image'] = json.loads(clean_script)['item']['images']['thumb']        # small size
    #game_properties['game_image'] = json.loads(clean_script)['item']['imageurl']               # medium size
    game_properties['game_image'] = json.loads(clean_script)['item']['images']['previewthumb']  # medium-large size
    #game_properties['game_image'] = json.loads(clean_script)['item']['images']['original']     # large size
    game_properties['background_image'] = json.loads(clean_script)['item']['topimageurl']

    return game_properties
