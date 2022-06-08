import csv

import matplotlib.pyplot as plt

file = open('throughput_measurements.csv')
csvreader = csv.reader(file)

# measurement_type = "CoAP"
measurement_type = "MQTT"

y1 = next(csvreader)
y2 = next(csvreader)

FONT_SIZE = 14

y = []
match measurement_type:
    case "CoAP":
        y = y1
        x = ["200", "400", "600", "800", "1000", "1200", "1400", "1600", "1800", "2000"]
        plt.ylabel('Latency (ms)', fontsize=FONT_SIZE)
        plt.xlabel('Throughput (requests per second)', fontsize=FONT_SIZE)
    case "MQTT":
        y = y2
        x = ["10K", "20K", "30K", "40K", "50K", "60K", "70K", "80K", "90K", "100K"]
        plt.ylabel('Latency (ms)', fontsize=FONT_SIZE)
        plt.xlabel('Throughput (publish messages per second)', fontsize=FONT_SIZE)

def float_array(array):
    r = []
    for e in array:
        r.append(float(e))
    return r


plt.rcParams.update({'font.size': FONT_SIZE})



y = float_array(y)
plt.plot(x, y, marker='o')
# plt.legend()

match measurement_type:
    case "CoAP":
        plt.savefig(f"./graphs/throughput_CoAP.png")
    case "MQTT":
        plt.savefig(f"./graphs/throughput_MQTT.png")


#plt.show()
