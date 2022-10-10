import csv
from resource import RLIMIT_RSS
from turtle import color
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

from datetime import datetime
from pathlib import Path

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
RIDER1_TIMES = {
    'Start': '07/08/2022 12:30',
    'StIvesNorthbound': '07/08/2022 16:32',
    'BostonNorthbound': '07/08/2022 20:55',
    'LouthNorthbound':  '07/08/2022 23:47',
    'HessleNorthbound': '08/08/2022 09:16',
    'MaltonNorthbound': '08/08/2022 12:10',
    'BarnardCastle Northbound': '08/08/2022 18:09',
    'BramptonNorthbound': '08/08/2022 23:31',
    'MoffatNorthbound': '09/08/2022 10:05',
    'Dunfermline': '09/08/2022 15:44',
    'InnerleithenSouthbound': '09/08/2022 20:18',
    'EskdalemuirSouthbound': '10/08/2022 07:55',
    'BramptonSouthbound': '10/08/2022 11:09',
    'BarnardCastleSouthbound': '10/08/2022 16:09',
    'MaltonSouthbound': '10/08/2022 21:55',
    'HessleSouthbound': '11/08/2022 09:19',
    'LouthSouthbound': '11/08/2022 13:35',
    'BostonSouthbound': '11/08/2022 16:17',
    'St IvesSouthbound': '11/08/2022 20:49',
    'GreatEastonSouthbound': '12/08/2022 08:38',
    'DebdenFinish': '12/08/2022 11:27',
}
RIDER2_TIMES = {
    'Start': '07/08/2022 12:30',
    'StIvesNorthbound': '07/08/2022 16:33',
    'BostonNorthbound': '07/08/2022 20:55',
    'LouthNorthbound':  '07/08/2022 23:47',
    'HessleNorthbound': '08/08/2022 02:51',
    'MaltonNorthbound': '08/08/2022 06:51',
    'BarnardCastle Northbound': '08/08/2022 13:43',
    'BramptonNorthbound': '08/08/2022 19:37',
    'MoffatNorthbound': '09/08/2022 08:59',
    'Dunfermline': '09/08/2022 14:27',
    'InnerleithenSouthbound': '09/08/2022 19:06',
    'EskdalemuirSouthbound': '09/08/2022 21:59',
    'BramptonSouthbound': '10/08/2022 01:18',
    'BarnardCastleSouthbound': '10/08/2022 12:24',
    'MaltonSouthbound': '10/08/2022 18:47',
    'HessleSouthbound': '11/08/2022 06:50',
    'LouthSouthbound': '11/08/2022 10:10',
    'BostonSouthbound': '11/08/2022 13:09',
    'St IvesSouthbound': '11/08/2022 18:21',
    'GreatEastonSouthbound': '12/08/2022 08:39',
    'DebdenFinish': '12/08/2022 11:28',
}

CONTROLS = [k for k, v in sorted(RIDER1_TIMES.items(), key=lambda item: item[1])]

def read_datetime(time):
    try:
        return datetime.strptime(time, TIME_FORMAT)
    except ValueError:
        return None


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
    reference_speed = CONTROL_DISTANCES['DebdenFinish'] / 128.33
    reference_times = [CONTROL_DISTANCES[loc] / reference_speed for loc in CONTROL_DISTANCES]

    # Now subtract the reference times from the rider times.
    for rider in rider_times:
        for i, time in enumerate(rider):
            if time is not None:
                rider[i] = time - reference_times[i]

    return rider_times


def main():
    rider_data = [RIDER1_TIMES, RIDER2_TIMES]

    rider_times = calculate_relative_times(rider_data)

    locations = list(CONTROL_DISTANCES.keys())
    locations = [loc.replace('Northbound', ' (N)') for loc in locations]
    locations = [loc.replace('Southbound', ' (S)') for loc in locations]

    distances = list(CONTROL_DISTANCES.values())

    colours = ['darkblue', 'darkred']

    for i, times in enumerate(rider_times):
        plt.plot(distances, times, color=colours[i], linewidth=2)

    # Add legend
    plt.legend(['Tom B', 'Mark B'], loc='lower left')

    # Add dashed black line to emphasise the 128 hour 20 min cut-off.
    plt.plot(distances, [0] * len(locations), 'k--', lw=2)

    arrowprops = [
        dict(facecolor=colours[0], edgecolor=colours[0], shrink=0.05, width=0.5, headwidth=5),
        dict(facecolor=colours[1], edgecolor=colours[1], shrink=0.05, width=0.5, headwidth=5),
    ]

    # Annotate sleep stops (Tom B)
    plt.annotate(
        'Sleep at Premier Inn\nbefore Hessle',
        xy=(CONTROL_DISTANCES['LouthNorthbound'], -8.5),
        xytext=(CONTROL_DISTANCES['LouthNorthbound'], -2.5),
        arrowprops=arrowprops[0],
        ha='left',
        color=colours[0],
    )
    plt.annotate(
        'Sleep at\nBrampton',
        xy=(CONTROL_DISTANCES['BramptonNorthbound'], -12),
        xytext=(CONTROL_DISTANCES['BramptonNorthbound'], -5.5),
        arrowprops=arrowprops[0],
        ha='left',
        color=colours[0],
    )
    plt.annotate(
        'Sleep at\nInnerleithen',
        xy=(CONTROL_DISTANCES['InnerleithenSouthbound'], -13.2),
        xytext=(CONTROL_DISTANCES['InnerleithenSouthbound'], -4.9),
        arrowprops=arrowprops[0],
        ha='left',
        color=colours[0],
    )
    plt.annotate(
        'Sleep at\nMalton',
        xy=(CONTROL_DISTANCES['MaltonSouthbound'], -13),
        xytext=(CONTROL_DISTANCES['MaltonSouthbound'], -6.5),
        arrowprops=arrowprops[0],
        ha='left',
        color=colours[0],
    )
    plt.annotate(
        'Sleep at\nSt. Ives',
        xy=(CONTROL_DISTANCES['St IvesSouthbound'], -13),
        xytext=(CONTROL_DISTANCES['St IvesSouthbound'], -6.5),
        arrowprops=arrowprops[0],
        ha='left',
        color=colours[0],
    )

    # Annotate sleep stops (Mark B)
    plt.annotate(
        'Sleep at\nBrampton',
        xy=(CONTROL_DISTANCES['BramptonNorthbound'], -17),
        xytext=(CONTROL_DISTANCES['BramptonNorthbound'], -22),
        arrowprops=arrowprops[1],
        ha='left',
        color=colours[1],
    )
    plt.annotate(
        'Sleep at\nBrampton',
        xy=(CONTROL_DISTANCES['BramptonSouthbound'], -18.5),
        xytext=(CONTROL_DISTANCES['BramptonSouthbound'], -23),
        arrowprops=arrowprops[1],
        ha='left',
        color=colours[1],
    )
    plt.annotate(
        'Sleep at\nMalton',
        xy=(CONTROL_DISTANCES['MaltonSouthbound'], -17.5),
        xytext=(CONTROL_DISTANCES['MaltonSouthbound'], -22),
        arrowprops=arrowprops[1],
        ha='left',
        color=colours[1],
    )
    plt.annotate(
        '(Waited for\nTom B to\ncatch up!)\nSleep at\nSt. Ives',
        xy=(CONTROL_DISTANCES['St IvesSouthbound'], -16.5),
        xytext=(CONTROL_DISTANCES['St IvesSouthbound'], -22.5),
        arrowprops=arrowprops[1],
        ha='left',
        color=colours[1],
    )

    # Add text to finish point
    plt.plot(
        CONTROL_DISTANCES['DebdenFinish'],
        rider_times[0][-1],
        'o',
        color='teal',
        markersize=12,
        markeredgewidth=1,
        markeredgecolor='white',
    )
    total_time = rider_times[0][-1] + 128.33
    plt.text(
        CONTROL_DISTANCES['DebdenFinish'],
        rider_times[0][-1] - 2,
        f'Finished together\n at {total_time} hours',
        color='teal',
    )

    # Tidy up the plot.
    plt.xticks(distances, labels=locations, rotation=45, ha='right', fontsize=12)
    plt.xlim([0, distances[-1] + 25])
    plt.ylim([-25, 2])
    plt.ylabel('Time behind/ahead of 128 hour pace (hours)', fontsize=12)
    plt.title(f'The Bolton boys: control times relative to 128 hour pace', fontsize=18, y=1.15)
    plt.grid(b='on')
    plt.subplots_adjust(bottom=0.15, top=0.8)

    ax = plt.gca()
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.spines.left.set_visible(False)

    ax2 = ax.twiny()
    ax2.spines.right.set_visible(False)
    ax2.spines.top.set_visible(False)
    ax2.set_xticks(ax.get_xticks())
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticklabels([f'{int(np.round(dist, 0))} km' for dist in distances], fontsize=12, rotation=45, ha='left')

    fig = plt.gcf()
    fig.set_size_inches(12, 10)

    plt.savefig('my_times.png', dpi=300)

    plt.show()



if __name__ == '__main__':
    main()
