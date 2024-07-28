
import pandas as pd

from project.spyders import jogonamesa_spyder as spyder1


def test_output_length():
    assert len(spyder1.get_prices()) == 2

def test_output1():
    assert isinstance(spyder1.get_prices()[0], list)
    assert len(spyder1.get_prices()[0]) > 0

def test_output2():
    assert isinstance(spyder1.get_prices()[1], pd.DataFrame)
    assert len(spyder1.get_prices()[1]) > 0

