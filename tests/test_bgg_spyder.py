
from project.spyders import bgg_spyder


def test_output_length():
    assert len(bgg_spyder.get_game_properties(r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data\boardgames_bgg_ids.xlsx', 'Stone Age')) == 1

def test_output_type():
    assert isinstance(bgg_spyder.get_game_properties(r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data\boardgames_bgg_ids.xlsx', 'Stone Age'), dict)

def test_output_contents():
    assert len(bgg_spyder.get_game_properties(r'C:\Users\migue\OneDrive\Desktop\virtual_envs\board_games_web_scraping\project\data\boardgames_bgg_ids.xlsx', 'Stone Age').keys()) == 18
