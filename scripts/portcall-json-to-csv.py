#!/usr/bin/python

import sys, re, pdb
import logging
import argparse
import numpy as np
import pandas as pd
import datetime
import logging
from pandas.io.json import json_normalize
import json
import requests
import psycopg2
import datetime,time

f = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(filename = "conversion.log", filemode='a', level=logging.DEBUG, format=f)
console = logging.StreamHandler()
formatter = logging.Formatter(f)
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Digitraffic portcall parser')
    parser.add_argument('-i', '--input-json-files', help='Comma separated list of input JSON files for portcalls', required=True)
    parser.add_argument('-o', '--output_file_name', help='Output file', required=True)

    args = vars(parser.parse_args())
    return args


def convert_json_file_to_df(json_file):
    with open(json_file) as f:
        d = json.load(f)

        portcalls = json_normalize(d["portCalls"])

        portcalls = portcalls['portCallId']
        return portcalls


def main():
    args = parse_args()

    input_json_files = args['input_json_files']
    output_file_name = args['output_file_name']

    logger.info("Input file: {}".format(input_json_files))
    files = input_json_files.split(',')
    result = None
    for file in files:
        df = convert_json_file_to_df(file)
        logger.debug("Appending {} rows".format(len(df)))
        if result is None:
            result = df
        else:
            result = result.append(df)

    logger.info("Total number of rows: {}".format(len(result)))
    result.to_csv(output_file_name, sep=",", quoting=0)


if __name__ == "__main__":
    main()
