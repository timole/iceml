#!/usr/bin/python

import sys, re, pdb
import logging
import argparse
import numpy as np
import pandas as pd
import datetime
import logging
import json
import requests
import psycopg2
import datetime,time

TABLE_NAME = 'ais_observation'
COLUMN_NAMES = ','.join(['timestamp', 'mmsi', 'location', 'sog', 'cog', 'navstat', 'posacc', 'raim', 'heading', 'timestamp_seconds'])
BATCH_SIZE = 1000

def connect():
    try:
        connect_str = "dbname='iceml' user='iceml' host='localhost' password='WinterNavigation'"
        conn = psycopg2.connect(connect_str)
        return conn
    except Exception as e:
        print("Db connection failed")
        print(e)

def timeString(timeStamp):
    return timeStamp.replace(tzinfo=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'

def geographyPoint(lon, lat): 
    return "ST_GeogFromText('SRID=4326;POINT({} {})')".format(lon, lat)

def log_config():
    f = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(filename = "conversion.log", filemode='a', level=logging.DEBUG, format=f)
    console = logging.StreamHandler()
    formatter = logging.Formatter(f)
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

def parse_args():
    parser = argparse.ArgumentParser(description='SOPERNOVUS analysator')
    parser.add_argument('-i', '--input-json-file', help='Input JSON file for AIS data', required=True)
    args = vars(parser.parse_args())
    return args

def print_stats(startTime):
    print("Execution time: {} minutes:".format(round((datetime.datetime.now() - startTime).total_seconds() / 60, 1)))

def write_feature(j, cursor):
    if not "type" in j.keys() or j["type"] != "VESSEL_LOCATION":
        logger.debug("Skipped record with type={}".format(j["type"]))
        return

    d = j["data"]
    mmsi = d["mmsi"]
    lon = d["geometry"]["coordinates"][0]
    lat = d["geometry"]["coordinates"][1]
    sog = d["properties"]["sog"]
    cog = d["properties"]["cog"]
    navStat = d["properties"]["navStat"]
    posAcc = 1 if d["properties"]["posAcc"] == "True" else 0
    raim = 1 if d["properties"]["raim"] == "True" else 0
    heading = d["properties"]["heading"]
    timestampSeconds = d["properties"]["timestamp"]
    timeStamp = datetime.datetime.utcfromtimestamp(d["properties"]["timestampExternal"]/1000.0)
    if lat >= 61:
        sql = "insert into {} ({}) values ('{}', {}, {}, {}, {}, {}, B'{}', B'{}', {}, {})".format(TABLE_NAME, COLUMN_NAMES, timeString(timeStamp), mmsi, geographyPoint(lon,lat), sog, cog, navStat, posAcc, raim, heading, timestampSeconds)
        cursor.execute(sql)
        return (timeStamp, True)
    else: 
        return (timeStamp, False)

def convert_json_file_to_psql(json_file, conn, cursor):
    f = open(json_file, 'r')
    i = 0
    for line in f:
        d = json.loads(line)
        result = write_feature(d, cursor)
        i = i + 1
        if i % BATCH_SIZE == 0:
            conn.commit()
            logger.info("committed {} records".format(BATCH_SIZE))
    conn.commit()
    logger.info("Wrote: N={}".format(i))

def main():
    args = parse_args()
    log_config()

    global logger
    logger = logging.getLogger(__name__)

    input_json_file = args['input_json_file']
    logger.info("Input file: {}".format(input_json_file))

    conn = connect()
    cursor = conn.cursor()

    start_time = datetime.datetime.now()
    convert_json_file_to_psql(input_json_file, conn, cursor)

    print_stats(start_time)

if __name__ == "__main__":
    main()
