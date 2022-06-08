import csv

import matplotlib.pyplot as plt

file = open('context_measurements.csv')
csvreader = csv.reader(file)

# measurement_type = "queue_size"
# measurement_type = "service_time"
measurement_type = "queue_time"

y1 = next(csvreader)
y2 = next(csvreader)
y3 = next(csvreader)

y4 = next(csvreader)
y5 = next(csvreader)
y6 = next(csvreader)

y7 = next(csvreader)
y8 = next(csvreader)
y9 = next(csvreader)

FONT_SIZE = 14

x = ["25", "50", "100", "250", "500", "1000"]
interval = ["1 ms", "0.75 ms", "0.5 ms"]

match measurement_type:
    case "queue_size":
        y_axis = [y1, y2, y3]
        plt.ylabel('Mean queue size (Number of packets)', fontsize=FONT_SIZE)
    case "service_time":
        y_axis = [y4, y5, y6]
        plt.ylabel('Mean service time (ms)', fontsize=FONT_SIZE)
        plt.ylim([0, 6])
    case "queue_time":
        y_axis = [y7, y8, y9]
        plt.ylabel('Mean queue time (ms)', fontsize=FONT_SIZE)


def float_array(array):
    r = []
    for e in array:
        r.append(float(e))
    return r


plt.rcParams.update({'font.size': FONT_SIZE})

plt.xlabel('Burst size (Number of messages)', fontsize=FONT_SIZE)

for i in range(len(y_axis)):
    y_axis[i] = float_array(y_axis[i])
ymin = []
ymax = []
for i in range(len(y_axis[0])):
    ymin.append(min(y_axis[0][i], min(y_axis[1][i], y_axis[2][i])))
    ymax.append(max(y_axis[0][i], max(y_axis[1][i], y_axis[2][i])))
plt.vlines(x=x, ymin=ymin, ymax=ymax,
           colors='teal', ls='--')

for i in range(len(y_axis)):
    plt.plot(x, y_axis[i], label=interval[i], marker='o')
plt.legend()

match measurement_type:
    case "queue_size":
        plt.savefig(f"./graphs/mean_queue_size.png")
    case "service_time":
        plt.savefig(f"./graphs/mean_service_time.png")
    case "queue_time":
        plt.savefig(f"./graphs/mean_queue_time.png")

#plt.show()
