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

TABLE_NAME = 'vessel_location'
COLUMN_NAMES = ','.join(['timestamp', 'mmsi', 'location', 'sog', 'cog', 'navstat', 'posacc', 'raim', 'heading', 'timestamp_seconds'])
TABLE_NAME_VESSEL_METADATA = 'vessel_metadata'
COLUMN_NAMES_VESSEL_METADATA = ','.join(['timestamp', 'name', 'callsign', 'imo', 'mmsi', 'destination', 'eta', 'draught', 'pos_type', 'reference_point_a', 'reference_point_b', 'reference_point_c', 'reference_point_d', 'ship_type'])
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
    parser = argparse.ArgumentParser(description='Digitraffic maritime')
    parser.add_argument('-i', '--input-json-file', help='Input JSON file for AIS data', required=True)
    args = vars(parser.parse_args())
    return args


def print_stats(startTime):
    print("Execution time: {} minutes:".format(round((datetime.datetime.now() - startTime).total_seconds() / 60, 1)))


def write_feature(j, cursor):
    if not "type" in j.keys() or j["type"] not in ["VESSEL_LOCATION", "VESSEL_METADATA"]:
        logger.debug("Skipped record with type={}".format(j["type"]))
        return

    if j["type"] == "VESSEL_LOCATION":
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
            sql = "insert into {} ({}) values (%s, %s, ST_GeogFromText('SRID=4326;POINT(%s %s)'), %s, %s, %s, B'%s', B'%s', %s, %s)".format(TABLE_NAME, COLUMN_NAMES)
            cursor.execute(sql, (timeString(timeStamp), mmsi, lon, lat, sog, cog, navStat, posAcc, raim, heading, timestampSeconds))

    if j["type"] == "VESSEL_METADATA":
        d = j["data"]
        timestamp = datetime.datetime.utcfromtimestamp(d["timestamp"]/1000.0)
        callsign = d["callSign"]
        imo = d["imo"]
        mmsi = d["mmsi"]
        destination = d["destination"]
        eta = d["eta"]
        draught = d["draught"]
        pos_type = d["posType"]
        reference_point_a = d["referencePointA"]
        reference_point_b = d["referencePointB"]
        reference_point_c = d["referencePointC"]
        reference_point_d = d["referencePointD"]
        ship_type = d["shipType"]
        name = d["name"]
        sql = "insert into {} ({}) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(TABLE_NAME_VESSEL_METADATA, COLUMN_NAMES_VESSEL_METADATA)
        cursor.execute(sql, (timestamp, name, callsign, imo, mmsi, destination, eta, draught, pos_type, reference_point_a, reference_point_b, reference_point_c, reference_point_d, ship_type))

def convert_json_file_to_psql(json_file, conn, cursor):
    f = open(json_file, 'r')
    i = 0
    for line in f:
        d = json.loads(line)
        write_feature(d, cursor)
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
