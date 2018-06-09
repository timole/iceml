import unittest

import pdb
import logging
import numpy as np
import pandas as pd
from ais import analysis

TEST_VESSEL_LOCATION_FILE = "testdata/vessellocations.csv"
TEST_VESSEL_METADATA_FILE = "testdata/vesselmetadatas.csv"
TEST_ICE_CONDITION_FILE = "testdata/iceconditions.csv"

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
        self.vl = pd.read_csv(TEST_VESSEL_LOCATION_FILE, parse_dates = ['timestamp'])
        self.vm = pd.read_csv(TEST_VESSEL_METADATA_FILE, parse_dates = ['timestamp'])
        self.ice = pd.read_csv(TEST_ICE_CONDITION_FILE, parse_dates = ['timestamp'])

    def test_number_of_observations(self):
        self.assertEqual(len(self.vl), 99063)

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
        vl = self.vl
        vl = vl[(vl['timestamp'] >= '2018-03-19 12:45:00') & (vl['timestamp'] < '2018-03-19 13:00:00')]
        analysis.append_sudden_stopping(vl)
        self.assertEqual(len(vl[vl['sudden_stopping'] == True]), 4)

    @staticmethod
    def create_vessel_meta_and_location_data(mmsi, time_offset='0 Seconds'):
        vm = pd.DataFrame(data = {'timestamp': pd.to_datetime(['2013-01-01 00:00:00.102', '2013-01-01 00:00:00.104', '2013-01-01 00:00:00.112']) + pd.to_timedelta(time_offset),
                                  'mmsi': [mmsi, mmsi, mmsi],
                                  'name': ['name1_' + str(mmsi), 'name2_' + str(mmsi), 'name3_' + str(mmsi)],
                                  'ship_type': [1, 1, 1],
                                  'callsign': ['ABCD', 'ABCD', 'ABCD'],
                                  'imo': [456789, 456789, 456789],
                                  'destination': ['KEMI', 'KEMI', 'KEMI'],
                                  'eta': [12345, 12345, 12345],
                                  'draught': [45, 45, 45],
                                  'pos_type': [1, 1, 1],
                                  'reference_point_a': [100, 100, 100],
                                  'reference_point_b': [10, 10, 10],
                                  'reference_point_c': [20, 20, 20],
                                  'reference_point_d': [25, 25, 25]})

        vl = pd.DataFrame(data = {'timestamp': pd.to_datetime(['2013-01-01 00:00:00.100', '2013-01-01 00:00:00.101', '2013-01-01 00:00:00.103', '2013-01-01 00:00:00.105', '2013-01-01 00:00:00.106']) + pd.to_timedelta(time_offset),
                                  'mmsi': [mmsi, mmsi, mmsi, mmsi, mmsi],
                                  'lon': [23.2, 23.2, 23.2, 23.2, 23.2],
                                  'lat': [65.1, 65.1, 65.1, 65.1, 65.1],
                                  'sog': [10, 10, 10, 10, 10],
                                  'cog': [120, 120, 120, 120, 120],
                                  'heading': [121, 121, 121, 121, 121]})
        return vm, vl

    def test_merge_location_and_metadata(self):
        vm, vl = self.create_vessel_meta_and_location_data(123)

        df = analysis.merge_vessel_meta_and_location_data(vm, vl)

        self.assertEqual(len(df), 3)
        self.assertEqual(df.name.isin(['name1_123', 'name2_123']).any(), True)
        self.assertEqual(~df.name.isin(['name3_123']).any(), True)

    def test_merge_multiple_location_and_metadata(self):
        vm, vl = self.create_vessel_meta_and_location_data(123, '0 Seconds')
        vm2, vl2 = self.create_vessel_meta_and_location_data(456, '10 Seconds')

        vm = vm.append(vm2)
        vl = vl.append(vl2)

        df = analysis.merge_vessel_meta_and_location_data(vm, vl)
        df = df.sort_values(by=['timestamp', 'mmsi'])

        self.assertEqual(len(df), 6)
        self.assertEqual(df.name.isin(['name1_123', 'name2_123']).any(), True)
        self.assertEqual(~df.name.isin(['name3_123']).any(), True)

    def test_merge_location_and_ice_condition(self):
        vl = pd.DataFrame(data = {'timestamp': pd.to_datetime(['2018-03-21 00:00:00.100', '2018-03-21 00:00:00.101', '2018-03-21 00:00:00.103', '2018-03-21 00:00:00.105', '2018-03-21 00:00:00.106']),
                                  'mmsi': [123, 123, 123, 123, 123],
                                  'lon': [0.2, 23.2, 23.2, 23.2, 23.2],
                                  'lat': [0.1, 65.1, 65.1, 65.1, 65.1],
                                  'sog': [10, 10, 10, 10, 10],
                                  'cog': [120, 120, 120, 120, 120],
                                  'heading': [121, 121, 121, 121, 121]})

        df = analysis.merge_location_and_ice_condition(vl, self.ice)
        self.assertTrue(np.isnan(df.iloc[0]['concentration']))
        self.assertTrue(np.isnan(df.iloc[0]['thickness']))
        self.assertEqual(df.iloc[1]['concentration'], 98)
        self.assertEqual(df.iloc[1]['thickness'], 0.8)


if __name__ == '__main__':
    unittest.main()
