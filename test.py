import unittest

import pdb
import logging
import numpy as np
import pandas as pd
from ais import analysis

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
        self.ais = pd.read_csv(TEST_DATA_FILE, parse_dates = ['timestamp'])

    def test_number_of_observations(self):
        self.assertEqual(len(self.ais), 99063)


    def test_append_sudden_stopping(self):
        df = pd.DataFrame(data = {'timestamp': ['2013-01-01 00:00:00', '2013-01-01 00:00:01', '2013-01-01 00:00:02', '2013-01-01 00:00:03'],
                                  'mmsi': [123, 123, 123, 123],
                                  'sog': [10, 10, 7, 0]})
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        analysis.append_sudden_stopping(df)
        self.assertTrue(df.iloc[3]['sudden_stopping'])
        self.assertTrue((df.iloc[0:2]['sudden_stopping'] == False).all())


    def test_append_sudden_stopping_continuous(self):
        df = pd.DataFrame(data = {'timestamp': ['2013-01-01 00:00:00', '2013-01-01 00:00:01', '2013-01-01 00:00:02', '2013-01-01 00:00:03', '2013-01-01 00:00:04'],
                                  'mmsi': [123, 123, 123, 123, 123],
                                  'sog': [12, 12, 13, 0, 0]})
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        analysis.append_sudden_stopping(df)
        self.assertTrue(df.iloc[3]['sudden_stopping'])
        self.assertTrue((df.iloc[0:2]['sudden_stopping'] == False).all())
        self.assertFalse(df.iloc[4]['sudden_stopping'])


    def test_append_sudden_stopping_sample_data(self):
        ais = self.ais
        ais = ais[(ais['timestamp'] >= '2018-03-19 12:45:00') & (ais['timestamp'] < '2018-03-19 13:00:00')]
        analysis.append_sudden_stopping(ais)
        self.assertEqual(len(ais[ais['sudden_stopping'] == True]), 4)


if __name__ == '__main__':
    unittest.main()
