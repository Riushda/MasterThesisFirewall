import csv

import matplotlib.pyplot as plt

file = open('data.csv')
csvreader = csv.reader(file)

nftables = next(csvreader)
context = next(csvreader)

FONT_SIZE = 14

x = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
y_axis = [nftables, context]
titles = ["Nftables", "context", "total"]

def float_array(array):
    r = []
    for e in array:
        r.append(float(e))
    return r


i = 0
for y in y_axis:
    plt.rcParams.update({'font.size': FONT_SIZE})
    y = float_array(y)
    title = f"Building time for {titles[i]}"
    plt.title(title, fontsize=FONT_SIZE)
    plt.bar(x, y, color='black', width=0.8)
    plt.xlabel('Number of members', fontsize=FONT_SIZE)
    plt.ylabel('Time (s)', fontsize=FONT_SIZE)
    plt.savefig(f"./graphs/{titles[i]}_building_time.png")
    plt.show()
    i += 1

y1 = float_array(y_axis[0])
y2 = float_array(y_axis[1])
y = []
for j in range(len(y1)):
    y.append(y1[j] + y2[j])
print()
title = "Total building time"
plt.title(title, fontsize=FONT_SIZE)
plt.bar(x, y, color='black', width=0.8)
plt.xlabel('Number of members', fontsize=FONT_SIZE)
plt.ylabel('Time (s)', fontsize=FONT_SIZE)
plt.savefig(f"./graphs/total_building_time.png")
plt.show()

