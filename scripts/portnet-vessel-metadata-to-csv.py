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
    parser = argparse.ArgumentParser(description='Digitraffic portcall metadata parser')
    parser.add_argument('-i', '--input-json-dir', help='Comma separated list of input JSON files for portcalls', required=True)
    parser.add_argument('-o', '--output_file_name', help='Output file', required=True)

    args = vars(parser.parse_args())
    return args


def append_columns(df, column_name):
    df_add = json_normalize(df[column_name][0])
    df = pd.concat([df, df_add], axis=1)
    del df[column_name]
    return df


def convert_json_file_to_df(json_filename):
    with open(json_filename) as json_file:
        df = pd.read_json(json_file)
        if not "mmsi" in df.columns:
            return None
        df = append_columns(df, 'vesselDimensions')
        df = append_columns(df, 'vesselConstruction')
        df = append_columns(df, 'vesselSystem')
        df = append_columns(df, 'vesselRegistration')
        return df


def get_file_list(input_json_dir):
    f = []
    files = os.listdir(input_json_dir)
    for file in files:
        if ".json" in file:
            f.append(input_json_dir + "\\" + file)
    return f


def main():
    args = parse_args()

    input_json_dir = args['input_json_dir']
    output_file_name = args['output_file_name']

    logger.info("Input directory: {}".format(input_json_dir))
    files = get_file_list(input_json_dir)
    result = None
    for file in files:
        df = convert_json_file_to_df(file)
        if df is None:
            continue
        logger.debug("Appending {} rows".format(len(df)))
        if result is None:
            result = df
        else:
            result = result.append(df)

    logger.info("Total number of rows: {}".format(len(result)))
    result.to_csv(output_file_name, sep=",", quoting=0, index=False)


if __name__ == "__main__":
    main()
