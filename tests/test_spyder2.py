
import pandas as pd

from project.spyders import gameplay_spyder as spyder2


def test_output_length():
    assert len(spyder2.get_prices(['Agra', 'Expeditions'])) == 2

def test_output_type():
    assert isinstance(spyder2.get_prices(['Agra', 'Expeditions']), pd.DataFrame)

