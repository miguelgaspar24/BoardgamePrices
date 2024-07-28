
import pandas as pd

from project.spyders import jogartabuleiro_spyder as spyder3


def test_output_length():
    assert len(spyder3.get_prices()) == 2

def test_output1():
    assert isinstance(spyder3.get_prices()[0], list)
    assert len(spyder3.get_prices()[0]) > 0

def test_output2():
    assert isinstance(spyder3.get_prices()[1], pd.DataFrame)
    assert len(spyder3.get_prices()[1]) > 0

