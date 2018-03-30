import unittest

import pdb
import logging
import numpy as np
import pandas as pd
from ais import assistance

TEST_DATA_FILE = "testdata/testdata.csv"

# some vessels and icebreakers in the dataset
AURA = 230601000
BBC_VIRGINIA=305463000
KIISLA=230956000
SISU=230289000
YMER=265066000

class TestAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pd.set_option('display.width', 240)
        self.ais = pd.read_csv(TEST_DATA_FILE)

    def test_number_of_observations(self):
        self.assertEqual(len(self.ais), 99063)

    def test_append_tow_events(self):
        assistance.append_tow_events(self.ais)
        print(self.ais)

if __name__ == '__main__':
    unittest.main()
