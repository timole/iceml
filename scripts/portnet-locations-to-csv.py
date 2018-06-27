#!/usr/bin/python

import argparse
import pandas as pd
import logging
from pandas.io.json import json_normalize
import os


f = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(filename = "conversion.log", filemode='a', level=logging.DEBUG, format=f)
console = logging.StreamHandler()
formatter = logging.Formatter(f)
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Digitraffic portnet location data parser')
    parser.add_argument('-i', '--input_file', help='Input JSON file', required=True)
    parser.add_argument('-o', '--output_file', help='Output CSV file', required=True)

    args = vars(parser.parse_args())
    return args


def append_columns(df, column_name):
    df_add = json_normalize(df[column_name][0])
    df = pd.concat([df, df_add], axis=1)
    del df[column_name]
    return df


def convert_json_file_to_df(json_file):
    df = pd.read_json(json_file)
    locations = json_normalize(df['ssnLocationFeatureCollection']['features'])
    ports_fi = locations[(pd.notnull(locations['locode'])) & (pd.notnull(locations['geometry.coordinates'])) & (locations['locode'].str.startswith('FI'))][['locode', 'properties.locationName', 'geometry.coordinates']]
    ports_fi = ports_fi.merge(ports_fi['geometry.coordinates'].apply(lambda coords: pd.Series({'lon': coords[0], 'lat': coords[1]})), left_index=True, right_index=True)
    del ports_fi['geometry.coordinates']
    ports_fi.columns = ['locode', 'name', 'lat', 'lon']
    return ports_fi



def main():
    args = parse_args()

    input_file = args['input_file']
    output_file_name = args['output_file']

    logger.info("Input file: {}".format(input_file))

    df = convert_json_file_to_df(input_file)
    logger.info("Total number of rows: {}".format(len(df)))
    df.to_csv(output_file_name, sep=",", quoting=0, index=False)


if __name__ == "__main__":
    main()
