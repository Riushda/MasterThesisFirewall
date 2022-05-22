import csv

import matplotlib.pyplot as plt

file = open('scaling.csv')
csvreader = csv.reader(file)

l_field = next(csvreader)
l_value = next(csvreader)

FONT_SIZE = 14

x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y_axis = [l_value, l_field]
labels = ["F = 2, V = 1", "F = 1, V = 2"]


def float_array(array):
    r = []
    for e in array:
        r.append(float(e))
    return r


plt.rcParams.update({'font.size': FONT_SIZE})
plt.xlabel('Number of members', fontsize=FONT_SIZE)
plt.ylabel('Latency (ms)', fontsize=FONT_SIZE)
for i in range(len(y_axis)):
    plt.plot(x, float_array(y_axis[i]), label=labels[i])
plt.legend()
plt.savefig(f"./graphs/scaling_mqtt.png")
plt.show()
