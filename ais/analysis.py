import pandas as pd
import logging
logger = logging.getLogger(__name__)

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


def merge_vessel_meta_and_location_data(vm, vl):
    """ Merges dataframes (vessel meta data and vessel location) into a single dataframe.
    Assumes that the dataframes are for a single mmsi and ordered by timestamp.
    """
    logger = logging.getLogger(__name__)

    mmsis = vl['mmsi'].unique()

    df = None
    i = 0
    for mmsi in mmsis:
        logger.debug("Merge vessel {} ({}%)".format(mmsi, round(i / len(mmsis) * 100, 1)))
        result = merge_single_vessel_meta_and_location_data(vm[vm['mmsi'] == mmsi], vl[vl['mmsi'] == mmsi])
        if df is None:
            df = result
        else:
            df = df.append(result, ignore_index=True)
        i += 1

    return df


def merge_single_vessel_meta_and_location_data(vm, vl):
    vm = vm.sort_values('timestamp')
    vl = vl.sort_values('timestamp')

    vl_colnames = ['timestamp', 'mmsi', 'lon', 'lat', 'sog','cog', 'heading']
    vm_colnames = ['name', 'ship_type', 'callsign', 'imo', 'destination', 'eta', 'draught', 'pos_type', 'reference_point_a', 'reference_point_b', 'reference_point_c', 'reference_point_d'];
    n_rows = len(vl[vl['timestamp'] >= min(vm['timestamp'])])

    df = pd.DataFrame(index=range(n_rows), columns = vl_colnames + vm_colnames)

    if len(vm) == 0 or len(vl) == 0:
        return df

    vm_index = 0
    vl_index = 0

    i = 0
    while vl_index < len(vl):
        if vl.iloc[vl_index].timestamp > vm.iloc[vm_index].timestamp:
            while vm_index + 1 < len(vm) and vm.iloc[vm_index + 1].timestamp < vl.iloc[vl_index].timestamp:
                vm_index += 1

            if vm_index >= len(vm):
                break

            df.loc[i] = merge_vessel_row(vl, vl_index, vl_colnames, vm, vm_index, vm_colnames)
            i += 1
        vl_index += 1

    return df


def merge_vessel_row(vl, vl_index, vl_colnames, vm, vm_index, vm_colnames):
    d = {}
    for col_name in vl_colnames:
        d[col_name] = vl.iloc[vl_index][col_name]
    for col_name in vm_colnames:
        d[col_name] = vm.iloc[vm_index][col_name]
    return d
