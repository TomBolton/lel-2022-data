import csv
from turtle import width
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

    # Remove the 'Start Location' key-value pair, as that is an exception
    # to the rest of the data.
    for row in rider_data:
        del row['Start Location']

    return rider_data


def calculate_finish_times(rider_data):
    # We want to analyse the times of each rider, relative to the start time.
    # So convert each datetime string to a datetime object, and subtract the
    # start time from each of the other times.
    finish_times = []

    n_finish_no_start = 0

    for row in rider_data:
        # Convert the start and end times to a datetime object.
        start_time = read_datetime(row['Start'])
        end_time = read_datetime(row['DebdenFinish'])

        if end_time is not None and start_time is None:
            n_finish_no_start += 1

        if start_time is None or end_time is None:
            continue

        diff_hours = (end_time - start_time).total_seconds() / 3600
        diff_hours = np.round(diff_hours, 2)

        finish_times.append(diff_hours)

    print(f'Number of riders with a finish time but no start time: {n_finish_no_start}')

    return finish_times


def main():
    rider_data = read_in_data()

    finish_times = calculate_finish_times(rider_data)

    time_bins = np.linspace(66, 140, 38)

    # Plot the finish times as a histogram.
    plt.hist(finish_times, bins=time_bins, color='darkcyan', edgecolor='white')

    ax = plt.gca()
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.spines.left.set_visible(False)
    ax.set_axisbelow(True)

    # Add dashed black lines to emphasise the 100 and 128 hour.
    y_lim = ax.get_ylim()
    n_max = int(y_lim[1])

    x_special = [100, 128.33]
    colours = ['r', 'k']
    for i, x in enumerate(x_special):
        plt.plot([x] * n_max, np.arange(n_max), f'{colours[i]}--', lw=2)
        plt.text(
            x + 1,
            n_max - 5,
            f'{x} hours',
            ha='left',
            va='top',
            fontsize=18,
            color=colours[i],
        )

    # Show totals
    n_100 = np.sum(np.array(finish_times) < 100)
    n_128 = np.sum(np.array(finish_times) < 128.33) - n_100
    n_dnf = len(finish_times) - n_100 - n_128

    plt.text(
        64,
        n_max - 47,
        f'{n_100} under 100 hours',
        ha='left',
        va='top',
        fontsize=18,
    )
    plt.text(
        64,
        n_max - 57,
        f'{n_128} between 100 and 128.33 hours',
        ha='left',
        va='top',
        fontsize=18,
    )
    plt.text(
        64,
        n_max - 67,
        f'{n_dnf} after 128.33 hours',
        ha='left',
        va='top',
        fontsize=18,
    )

    # Highlight fastest and slowest times.
    fastest = np.min(finish_times)
    slowest = np.max(finish_times)

    plt.text(
        fastest,
        35,
        f'{fastest} hours',
        ha='left',
        va='top',
        fontsize=18,
        color='r',
    )
    plt.text(
        slowest,
        35,
        f'{slowest} hours',
        ha='left',
        va='top',
        fontsize=18,
        color='k',
    )
    ax.arrow(fastest, 30, 0, -27, width=0.2, fc='r', ec='r', length_includes_head=True)
    ax.arrow(slowest, 30, 0, -27, width=0.2, fc='k', ec='k', length_includes_head=True)

    # Tidy up the plot.
    plt.xlabel('Finish time (hours)', fontsize=18)
    plt.ylabel('Number of riders', fontsize=18)
    plt.title(f'Frequency of rider finish times (n = {len(finish_times)}, 2 hour bins)', fontsize=24)
    plt.grid(b='on')
    plt.minorticks_on()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    fig = plt.gcf()
    fig.set_size_inches(15, 10)

    #plt.savefig('finish_times.png', dpi=300)

    plt.show()



if __name__ == '__main__':
    main()
