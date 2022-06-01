"""
This class contains some utility functions used by the classes of this package.
"""

from datetime import datetime


def parse_time_interval(value):
    if not isinstance(value, list):
        raise ValueError("Error: Wrong value for time, format is [\"xx:xx\",\"xx:xx\"].")

    if len(value) == 2:
        for x in range(2):
            split = value[x].split(":")
            if len(split) != 2:
                raise ValueError("Error: Wrong value for time, format is [\"xx:xx\",\"xx:xx\"].")
            if not ((0 <= int(split[0]) < 24) and (0 <= int(split[1]) < 60)):
                raise ValueError("Error: Wrong value for time, it must an integer. "
                                 "Max hour is 23 and max minute is 59.")
    else:
        raise ValueError("Error: Wrong value for time, format is [\"xx:xx\",\"xx:xx\"].")


def is_overlapping(first_inter, second_inter):
    for i in (first_inter, second_inter):
        for j in (first_inter, second_inter):
            if i != j:
                temp_i = i
                temp_j = j
                if i[0] > i[1]:
                    temp_i = [i[0], i[1] + 1440]
                    if j[0] < j[1]:
                        temp_j = [j[0] + 1440, j[1] + 1440]
                    else:
                        temp_j = [j[0], j[1] + 1440]
                elif j[0] > j[1]:
                    temp_j = [j[0], j[1] + 1440]
                    temp_i = [i[0] + 1440, i[1] + 1440]

                for x in range(2):
                    if temp_j[0] < temp_i[x] < temp_j[1]:
                        return True
    return False


def check_overlapping(intervals):
    int_intervals = []
    for interval in intervals:
        int_value = []
        for x in range(2):
            dt_object = datetime.strptime(interval[x], "%H:%M")
            int_value.append(dt_object.hour * 60 + dt_object.minute)
        int_intervals.append(int_value)

    for i in range(len(int_intervals)):
        for j in range(len(int_intervals)):
            if i != j:
                if is_overlapping(int_intervals[i], int_intervals[j]):
                    raise ValueError("Error: Overlapping time intervals.")


def invert_time_intervals(intervals):
    result = []
    for interval in intervals:
        result.append([interval[1], interval[0]])
    return result
