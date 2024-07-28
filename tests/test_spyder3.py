
import pandas as pd

from project.spyders import jogartabuleiro_spyder as spyder3


def test_output_length():
    assert len(spyder3.get_prices(['Agra', 'Expeditions'])) == 2

def test_output_type():
    assert isinstance(spyder3.get_prices(['Agra', 'Expeditions']), pd.DataFrame)

