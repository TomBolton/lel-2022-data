import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

from datetime import datetime
from pathlib import Path

PATH_TO_DATA = Path(__file__).parent.joinpath('data', 'LEL2022_anonymous_rider_data.csv')
TIME_FORMAT = '%d/%m/%Y %H:%M'

CONTROL_DISTANCES = {
    'Start': 0.0,
    'StIvesNorthbound': 99.6,
    'BostonNorthbound': 188.8,
    'LouthNorthbound':  241.9,
    'HessleNorthbound': 299.8,
    'MaltonNorthbound': 366.7,
    'BarnardCastle Northbound': 480.1,
    'BramptonNorthbound': 563.5,
    'MoffatNorthbound': 637.5,
    'Dunfermline': 748.6,
    'InnerleithenSouthbound': 829.9,
    'EskdalemuirSouthbound': 879.2,
    'BramptonSouthbound': 938.5,
    'BarnardCastleSouthbound': 1022.1,
    'MaltonSouthbound': 1133.9,
    'HessleSouthbound': 1200.7,
    'LouthSouthbound': 1259.1,
    'BostonSouthbound': 1312.1,
    'St IvesSouthbound': 1401.5,
    'GreatEastonSouthbound': 1471.8,
    'DebdenFinish': 1519.9,
}

CONTROLS = [k for k, v in sorted(CONTROL_DISTANCES.items(), key=lambda item: item[1])]

def read_datetime(time):
    try:
        return datetime.strptime(time, TIME_FORMAT)
    except ValueError:
        return None


def read_in_data():
    with open(PATH_TO_DATA, 'r') as f:
        # Each row is an OrderedDict, with the keys as the locations
        # and the value as a datatime string.
        rider_data = [row for row in csv.DictReader(f)]

    # Only select riders who started at 5am from Debden.
    rider_data = [row for row in rider_data if row['Start'] == '07/08/2022 05:00']
    rider_data = [row for row in rider_data if row['Start Location'] == 'Debden']

    # Remove the 'Start Location' key-value pair, as that is an exception
    # to the rest of the data.
    for row in rider_data:
        del row['Start Location']

    # Remove any control times which occur after a rider has a NULL value.
    # There are weird disconnected lines which looks like riders have missed/skipped
    # controls, which makes any graphs look messy. Assume that if a rider has a
    # NULL value, they have DNFed from that control onwwards, and remove any
    # subsequent times.
    cleaned_rider_data = []
    for rider in rider_data:
        has_dnfed = False
        for c in CONTROLS:
            time = rider[c]

            if time == 'NULL':
                has_dnfed = True

            if has_dnfed and time != 'NULL':
                rider[c] = 'NULL'

        cleaned_rider_data.append(rider)

    return rider_data


def calculate_relative_times(rider_data):
    # We want to analyse the times of each rider, relative to the start time.
    # So convert each datetime string to a datetime object, and subtract the
    # start time from each of the other times.
    rider_times = []

    for row in rider_data:

        # Convert the start time to a datetime object.
        start_time = read_datetime(row['Start'])

        if start_time is None:
            continue

        # Convert each of the other times to a datetime object, and subtract
        # the start time from it.
        relative_times = []
        for c in CONTROLS:
            time = read_datetime(row[c])

            if time is not None:
                diff_hours = (time - start_time).total_seconds() / 3600
                diff_hours = np.round(diff_hours, 2)
            else:
                diff_hours = None

            relative_times.append(diff_hours)

        rider_times.append(relative_times)


    # We now want to calculate the times relative to the average pace
    # required to finish with the 128 hour 20 min cut-off.
    reference_speed = CONTROL_DISTANCES['DebdenFinish'] / 100.0
    reference_times = [CONTROL_DISTANCES[loc] / reference_speed for loc in CONTROL_DISTANCES]

    # Now subtract the reference times from the rider times.
    for rider in rider_times:
        for i, time in enumerate(rider):
            if time is not None:
                rider[i] = time - reference_times[i]

    return rider_times


def main():
    rider_data = read_in_data()

    rider_times = calculate_relative_times(rider_data)

    # Sort riders according to the number of controls they reached.
    rider_times = sorted(rider_times, key=lambda x: x.count(None))

    # Plot each riders times on one graph.
    locations = list(rider_data[0].keys())
    locations = [loc.replace('Northbound', ' (N)') for loc in locations]
    locations = [loc.replace('Southbound', ' (S)') for loc in locations]

    distances = list(CONTROL_DISTANCES.values())

    # Get min/max final times
    time_max = np.max([r[-1] for r in rider_times if r[-1] is not None])
    time_min = np.min([r[-1] for r in rider_times if r[-1] is not None])

    for times in rider_times:
        finish_time = [t for t in times if t is not None][-1]
        normalised_finish_time = np.abs((finish_time - time_min) / (time_max - time_min))

        colour = cm.get_cmap('winter')(1 - normalised_finish_time)

        # Plot the line for this rider, as well as a marker
        # for the final control they reached.
        plt.plot(distances, times, color=colour, lw=2)

        # Find the last control they reached.
        last_control = None
        for i, time in enumerate(times):
            if time is not None:
                last_control = i

        plt.plot(
            distances[last_control],
            times[last_control],
            'X',
            color=colour,
            markersize=15,
            markeredgewidth=1.5,
            markeredgecolor='black',
        )

    # Add dashed black line to emphasise the 128 hour 20 min cut-off.
    plt.plot(distances, [0] * len(locations), 'k--', lw=2)

    # Tidy up the plot.
    plt.xticks(distances, labels=locations, rotation=45, ha='right', fontsize=18)
    plt.xlim([0, distances[-1] + 50])
    plt.ylabel('Time behind/ahead of 100 hour pace (hours)', fontsize=18)
    plt.title(f'Rider control times relative to 100 hour pace (n = {len(rider_times)})', fontsize=24)
    plt.grid(b='on')
    plt.subplots_adjust(bottom=0.2, top=0.9)

    ax = plt.gca()
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.spines.left.set_visible(False)

    fig = plt.gcf()
    fig.set_size_inches(15, 12)

    plt.savefig('rider_100hour_times.png', dpi=300)

    plt.show()



if __name__ == '__main__':
    main()
