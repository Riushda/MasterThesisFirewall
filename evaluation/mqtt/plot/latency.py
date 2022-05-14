import csv

import matplotlib.pyplot as plt

file = open('latency.csv')
csvreader = csv.reader(file)

l_10 = next(csvreader)
l_1 = next(csvreader)
l_01 = next(csvreader)
l_001 = next(csvreader)

FONT_SIZE = 14


x = ["10", "100", "1000", "10000"]
y_axis = [l_10, l_1, l_01, l_001]
interval = ["10", "1", "0.1", "0.01"]


def float_array(array):
    r = []
    for e in array:
        r.append(float(e))
    return r


i = 0
for y in y_axis:
    # fig = plt.figure(figsize=(5, 5))
    plt.rcParams.update({'font.size': FONT_SIZE})
    y = float_array(y)
    title = f"{interval[i]} ms interval"
    plt.title(title, fontsize=FONT_SIZE)
    plt.bar(x, y, color='black',
            width=0.8)
    # plt.xlabel('Number of messages', fontsize=FONT_SIZE)
    # plt.ylabel('Latency (ms)', fontsize=FONT_SIZE)
    plt.savefig(f"./graphs/{str(interval[i])}_mqtt.png")
    plt.show()
    i += 1
