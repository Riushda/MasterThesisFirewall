import csv

import matplotlib.pyplot as plt

file = open('latency.csv')
csvreader = csv.reader(file)

l_10 = next(csvreader)
l_1 = next(csvreader)
l_01 = next(csvreader)

FONT_SIZE = 14
FIREWALL = True

x = ["25", "50", "100", "250", "500", "1000"]
y_axis = [l_10, l_1, l_01]
interval = ["10", "7.5", "5"]


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
    if FIREWALL:
        plt.savefig(f"./graphs/{str(interval[i])}_firewall_coap.png")
    else:
        plt.savefig(f"./graphs/{str(interval[i])}_coap.png")
    plt.show()
    i += 1
