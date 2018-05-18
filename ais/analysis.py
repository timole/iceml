import pandas as pd
import numpy as np

MOVE_SPEED_THRESHOLD = 5
STOP_SPEED_THRESHOLD = 0.5

PREVIOUS_OBSERVATIONS_TIME_FRAME = 5 # store N minutues of observations

def filter_previous_observations_by_timestamp(df):
    if len(df) > 0:
        return df[lambda x: x['timestamp'] >= (df['timestamp'] - pd.Timedelta(15, unit='m'))]
    else:
        return df


def is_sudden_stop(d, prev):
    sog_mean = prev['sog'].mean()
    return sog_mean >= MOVE_SPEED_THRESHOLD and \
           d['sog'] < STOP_SPEED_THRESHOLD and \
           len(prev) > 1 and (prev['sudden_stopping'] == False).all()


def append_sudden_stopping(ais):
    ais.assign(sudden_stopping = None)
    vessels = {}

    for i, d in ais.iterrows():
        mmsi = d['mmsi']
        if not mmsi in vessels.keys():
            vessels[mmsi] = {}
            vessels[mmsi]['previous_observations'] = pd.DataFrame(columns=ais.columns)

        prev = filter_previous_observations_by_timestamp(vessels[mmsi]['previous_observations'])
        vessels[mmsi]['previous_observations'] = prev

        ais.set_value(i, 'sudden_stopping', is_sudden_stop(d, prev))

        vessels[mmsi]['previous_observations'] = vessels[mmsi]['previous_observations'].append(ais.loc[i])

    return ais


def merge_vessel_location_and_metadata(vl, vm):
    """ Merges dataframes (vessel location and meta data) into a single dataframe.
    Assumes that the dataframes are for a single mmsi and ordered by timestamp.
    """
    df = None

    vl_index = 0
    vm_index = 0

    colnames = ['timestamp', 'mmsi', 'lon', 'lat', 'sog', 'cog', 'heading', 'name', 'ship_type', 'callsign', 'imo', 'destination', 'eta', 'draught', 'pos_type', 'reference_point_a', 'reference_point_b', 'reference_point_c', 'reference_point_d']

    while vl.iloc[vl_index].timestamp < vm.iloc[vm_index].timestamp:
        vl_index += 1

    if df is None:
        df = pd.DataFrame(columns = colnames)

    while vl_index < len(vl):
        if vl.iloc[vl_index].timestamp and (vm_index + 1) < len(vm) and vm.iloc[vm_index].timestamp < vl.iloc[vl_index].timestamp:
            vm_index += 1
        df.loc[len(df) + 1] = {'timestamp': vl.iloc[vl_index].timestamp,
                               'mmsi': vl.iloc[vl_index].mmsi,
                               'lon': vl.iloc[vl_index].lon,
                               'lat': vl.iloc[vl_index].lat,
                               'sog': vl.iloc[vl_index].sog,
                               'cog': vl.iloc[vl_index].cog,
                               'heading': vl.iloc[vl_index].heading,
                               'name': vm.iloc[vm_index].name,
                               'ship_type': vm.iloc[vm_index].ship_type,
                               'callsign': vm.iloc[vm_index].callsign,
                               'imo': vm.iloc[vm_index].imo,
                               'destination': vm.iloc[vm_index].destination,
                               'eta': vm.iloc[vm_index].eta,
                               'draught': vm.iloc[vm_index].draught,
                               'pos_type': vm.iloc[vm_index].pos_type,
                               'reference_point_a': vm.iloc[vm_index].reference_point_a,
                               'reference_point_b': vm.iloc[vm_index].reference_point_b,
                               'reference_point_c': vm.iloc[vm_index].reference_point_c,
                               'reference_point_d': vm.iloc[vm_index].reference_point_d }
        vl_index += 1

    return df
