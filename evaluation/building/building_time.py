import csv

import matplotlib.pyplot as plt

file = open('data.csv')
csvreader = csv.reader(file)

nftables_time = next(csvreader)
context_time = next(csvreader)
relations_time = next(csvreader)

FONT_SIZE = 14

x_relations = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
x_context = ["3", "6", "9", "12", "15"]


def float_array(array):
    r = []
    for e in array:
        r.append(float(e))
    return r


plt.rcParams.update({'font.size': FONT_SIZE})
plt.bar(x_context, float_array(context_time), color='black', width=0.8)
plt.xlabel('Number of members', fontsize=FONT_SIZE)
plt.ylabel('Time (s)', fontsize=FONT_SIZE)
plt.savefig(f"./graphs/context_building_time.png")
plt.show()

y_total = []
for j in range(len(nftables_time)):
    y_total .append(float(nftables_time[j]) + float(context_time[j]))
plt.bar(x_context, y_total, color='black', width=0.8)
plt.xlabel('Number of members', fontsize=FONT_SIZE)
plt.ylabel('Time (s)', fontsize=FONT_SIZE)
plt.savefig(f"./graphs/total_building_time.png")
plt.show()


plt.bar(x_relations, float_array(relations_time), color='black', width=0.8)
plt.xlabel('Number of relations', fontsize=FONT_SIZE)
plt.ylabel('Time (s)', fontsize=FONT_SIZE)
plt.savefig(f"./graphs/relations_building_time.png")
plt.show()
