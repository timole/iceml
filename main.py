import logging
import argparse
import pandas as pd
import numpy as np
import os
import datetime
from ais import analysis

f = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(filename = "merge.log", filemode='a', level=logging.DEBUG, format=f)
console = logging.StreamHandler()
formatter = logging.Formatter(f)
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Vessel data combiner')
    parser.add_argument('-vm', '--vessel-meta-data-file', help='Vessel metadata input file', required=True)
    parser.add_argument('-vl', '--vessel-location-data-file', help='Vessel location data input file', required=True)
    parser.add_argument('-o', '--merged-data-file', help='Merged output file', required=True)
    args = vars(parser.parse_args())
    return args


def merge_files(vm_file, vl_file, merged_file):
    logger.info("Merge metadata from {} and location data from {} to file {}".format(vm_file, vl_file, merged_file))

    logger.info("Reading file {}".format(vm_file))
    vm = pd.read_csv(vm_file, parse_dates = ['timestamp'])

    logger.info("Reading file {}".format(vl_file))
    vl = pd.read_csv(vl_file, parse_dates = ['timestamp'])

    logger.info("Merging {} metadata rows and {} location data rows" .format(len(vm), len(vl)))
    merged = analysis.merge_vessel_meta_and_location_data(vm, vl)
    merged.to_csv(merged_file, sep=",")
    logger.info("Wrote {} rows to file {}".format(len(merged), merged_file))


def main():
    args = parse_args()

    start_time = datetime.datetime.now()
    merge_files(args['vessel_meta_data_file'], args['vessel_location_data_file'], args['merged_data_file'])
    logger.info("Execution time: {} seconds:".format(round((datetime.datetime.now() - start_time).total_seconds(), 1)))


if __name__ == "__main__":
    main()

